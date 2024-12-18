import streamlit as st
import pandas as pd
from datetime import date, datetime
from helper import call_rl_api, render_html_table

st.set_page_config(page_title="Fiddler RocketLane Time Reporting",layout='wide')

# Assume this function checks if the user is authenticated
# def is_user_authenticated():
#     # This should check an actual condition in your app's session state or other state mechanism
#     return st.session_state.get("authentication_status", False)

# # Check if user is authenticated at the very top before any page logic
# if not is_user_authenticated():
#     st.error("You must be logged in to view this page.")
#     st.stop()  # Prevents the execution of the rest of the script

# The rest of your studies list page logic here since the user is authenticated
def display_billable_report():

    page_function= ''
    project_id = ''

    if 'page_function' in st.query_params:   
        page_function = st.query_params['page_function']

    if 'project_id' in st.query_params:
        project_id = st.query_params['project_id']

    print('page_function: ' + page_function)
    print('project_id: ' + str(project_id))

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
        totalHours = round(totalMins/60, 2)

        st.markdown('Total Hours: ' + str(totalHours))
        st.markdown('Total Minutes: ' + str(totalMins))
        st.subheader("Select Columns to Display")
        selected_columns = st.multiselect(
            "Select columns to include in the table:",
            options=df_report.columns.tolist(),
            #default=df_report.columns.tolist()  # By default, select all columns
            default=['project.projectName','task.taskName','projectPhase.phaseName','user.firstName','user.lastName','user.emailId','date','minutes','createdAt','billable']
        )

        df_report['createdAt'] = pd.to_datetime(df_report['createdAt'], unit='ms').dt.strftime('%Y-%m-%d')
        filtered_df = df_report[selected_columns]

        # Display dataframe as HTML table
        html_table = render_html_table(filtered_df)
        st.markdown(html_table, unsafe_allow_html=True)
        
        # Back button to return to the main page
        st.markdown('[Go back to main page](projects)', unsafe_allow_html=True)
    else:
        st.markdown('No records in report.')

# Main logic
if __name__ == "__main__":
    display_billable_report()