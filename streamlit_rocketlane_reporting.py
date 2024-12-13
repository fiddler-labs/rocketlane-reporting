import streamlit as st
import pandas as pd
import requests
import json
import os
from datetime import date, datetime

RL_API_KEY = os.environ.get('RL_API_KEY')
RL_API_URL = 'https://api.rocketlane.com/api/1.0'

HEADERS = {
    "accept": "application/json",
    "api-key": RL_API_KEY
}

st.set_page_config(page_title="Fiddler RocketLane Time Reporting",layout='wide')

# Parse URL query parameters to determine which "page" to render
query_params = st.query_params()
page = query_params.get("page", ["main"])[0]
project_id = query_params.get("project_id", [""])[0]



# Convenience function to call Rocketlane API and return a dataframe
def call_rl_api(uri) -> pd.DataFrame:
    
    url = '/'.join([RL_API_URL,uri])
    print(url)
    response = requests.get(url, headers=HEADERS)
    tasks = json.loads(response.text)
    if 'data' in tasks:
        df = pd.json_normalize(tasks['data'])
    else:
        df = pd.json_normalize(tasks)
    return df


# Function to render dataframe as HTML table
def render_html_table(df, page):
    # Adding CSS for hover effect
    css = """
    <style>
    table {
        width: 100%;
        border-collapse: collapse;
        text-align: left;
    }
    th, td {
        padding: 8px;
        text-align: left;
        border: 1px solid #ddd;
        white-space: nowrap; /* Prevent text wrapping */
    }
    tr:hover {
        background-color: #f1f1f1;
        cursor: pointer;
    }
    </style>
    """

    # Add a "Generate Billable Report" link to the beginning of each row
    #df['Action'] = '<a href="https://example.com/generate-report" target="_blank">Billable Report</a>'
    #df['Action'] = '<a href="?page=billable_report&name={}" target="_self">Generate Billable Report</a>'.format(df['projectName'][0])

    if page != "billable_report":
         # Add a "Generate Billable Report" link that directs to the second page using query parameter
        df['Action'] = df['projectId'].apply(lambda x: f'<a href="?page=billable_report&project_id={x}" target="_self">Billable Report</a>')
    
    # Move 'Action' column to the front
    cols = df.columns.tolist()
    cols = [cols[-1]] + cols[:-1]
    df = df[cols]

    # Convert dataframe to HTML and append the CSS
    html_table = df.to_html(escape=False, index=False)
    return html_table + css


st.markdown("""
    <style>
    .main {
        text-align: left;
        justify-content: flex-start;
        padding-left: 10px; /* Adjust padding as needed */
        padding-right: 10px;
    }
    </style>
""", unsafe_allow_html=True)


# Conditional rendering based on the page parameter
if page == "billable_report" and project_id:

    # Get the current date and time
    now = datetime.now()

    # Create a new date object for the beginning of the month
    start_of_month = date(now.year, now.month, 1)
    end_of_month = date(now.year, now.month, 30)

    # Date range input
    val = st.date_input(
        "Select a date range:",
        #value=(date(2023, 1, 1), date(2023, 12, 31))  # Default date range
        value=(start_of_month, end_of_month)  # Default date range
    )
    try:
        start_date, end_date = val
    except ValueError:
        st.error("You must pick a start and end date")
        st.stop() 

    # Billable Hours input
    selected_hours = st.selectbox(
        "Hours:",  # Label for the dropdown
        ["All", "Billable", "Not Billable"]  # List of values
    )

    str_start_date = start_date.strftime("%Y-%m-%d")
    str_end_date = end_date.strftime("%Y-%m-%d")

    df_project = call_rl_api(f'projects/{project_id}')
    projectName = df_project.iloc[0]['projectName']

    time_entry_uri = f'time-entries?project.eq={project_id}&includeFields=status,sourceType&sortBy=date&sortOrder=ASC&date.ge={str_start_date}&date.le={str_end_date}'
    
    if selected_hours == "Billable":
        time_entry_uri = time_entry_uri + '&billable.eq=true'
    elif selected_hours == "Not Billable":
        time_entry_uri = time_entry_uri + '&billable.eq=false'

    df_report = call_rl_api(time_entry_uri)
     
     # Billable Report Page
    st.title(f"Billable Report for {projectName}")
    st.write(f"Generating billable report for {projectName}...")
    
    if not df_report.empty:
        totalMins = df_report['minutes'].sum()
        totalHours = totalMins/60

        st.markdown('Total Hours: ' + str(totalHours))
        st.markdown('Total Minutes: ' + str(totalMins))
        st.subheader("Select Columns to Display")
        selected_columns = st.multiselect(
            "Select columns to include in the table:",
            options=df_report.columns.tolist(),
            default=df_report.columns.tolist()  # By default, select all columns
            #default=['project.projectName','task.taskName','projectPhase.phaseName','user.firstName','user.lastName','user.emailId','date','minutes','createdAt','billable']
        )

        df_report['createdAt'] = pd.to_datetime(df_report['createdAt'], unit='ms').dt.strftime('%Y-%m-%d')
        filtered_df = df_report[selected_columns]

        # Display dataframe as HTML table
        html_table = render_html_table(filtered_df, page)
        st.markdown(html_table, unsafe_allow_html=True)
        
        # Back button to return to the main page
        st.markdown('[Go back to main page](?page=main)', unsafe_allow_html=True)
    else:
        st.markdown('No records in report.')
    
else:
    # Example DataFrame
    df_projects = call_rl_api('projects?includeArchive.eq=false')

    # Streamlit app title
    st.title("Active RocketLane Projects")

    # Display the dataframe
    #st.subheader("Original DataFrame")
    #st.write(df_projects)

    st.subheader("Select Columns to Display")
    selected_columns = st.multiselect(
        "Select columns to include in the table:",
        options=df_projects.columns.tolist(),
        #default=df_projects.columns.tolist()  # By default, select all columns
        default=['projectId','projectName','customer.companyName','startDate','dueDate','owner.firstName','status.label']
    )

    # Filter the DataFrame based on selected columns (add 'Action' column to selected)
    #if 'Action' not in selected_columns:
    #   selected_columns = ['Action'] + selected_columns

    # Filter the DataFrame based on selected columns
    filtered_df = df_projects[selected_columns]

    # Display dataframe as HTML table
    html_table = render_html_table(filtered_df, page)
    st.markdown(html_table, unsafe_allow_html=True)
