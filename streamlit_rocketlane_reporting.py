import streamlit as st
import pandas as pd
import requests
import json
import os

RL_API_KEY = os.environ.get('RL_API_KEY')
RL_API_URL = 'https://api.rocketlane.com/api/1.0'

HEADERS = {
    "accept": "application/json",
    "api-key": RL_API_KEY
}

# Parse URL query parameters to determine which "page" to render
query_params = st.experimental_get_query_params()
page = query_params.get("page", ["main"])[0]
project_id = query_params.get("project_id", [""])[0]

# Convenience function to call Rocketlane API and return a dataframe
def call_rl_api(uri) -> pd.DataFrame:
    
    url = '/'.join([RL_API_URL,uri])
    print(url)
    response = requests.get(url, headers=HEADERS)
    tasks = json.loads(response.text)
    df = pd.json_normalize(tasks['data'])
    return df


# Function to render dataframe as HTML table
def render_html_table(df, page):
    # Adding CSS for hover effect
    css = """
    <style>
    table {
        width: 100%;
        border-collapse: collapse;
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




# Conditional rendering based on the page parameter
if page == "billable_report" and project_id:
    
    df_report = call_rl_api(f'time-entries?project.eq={project_id}&sortBy=billable&billable.eq=true')
    projectName = df_report.iloc[0][5]
    # Billable Report Page
    st.title(f"Billable Report for {projectName}")
    st.write(f"Generating billable report for {projectName}...")
    
    #st.subheader("Original DataFrame")
    #st.write(df_report)

    st.subheader("Select Columns to Display")
    selected_columns = st.multiselect(
        "Select columns to include in the table:",
        options=df_report.columns.tolist(),
        #default=df_report.columns.tolist()  # By default, select all columns
        default=['project.projectName','task.taskName','projectPhase.phaseName','user.firstName','user.lastName','user.emailId','date','minutes','createdAt','billable']
    )

    filtered_df = df_report[selected_columns]

    # Display dataframe as HTML table
    html_table = render_html_table(filtered_df, page)
    st.markdown(html_table, unsafe_allow_html=True)
    
    # Back button to return to the main page
    st.markdown('[Go back to main page](?page=main)', unsafe_allow_html=True)
    
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
