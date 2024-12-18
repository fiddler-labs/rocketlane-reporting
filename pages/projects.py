import streamlit as st
import pandas as pd
from helper import call_rl_api, render_html_table
import numpy as np

st.set_page_config(page_title="Fiddler RocketLane Time Reporting",layout='wide')

# # Assume this function checks if the user is authenticated
# def is_user_authenticated():
#     # This should check an actual condition in your app's session state or other state mechanism
#     return st.session_state.get("authentication_status", False)

# # Check if user is authenticated at the very top before any page logic
# if not is_user_authenticated():
#     st.error("You must be logged in to view this page.")
#     st.stop()  # Prevents the execution of the rest of the script

# The rest of your studies list page logic here since the user is authenticated
def display_active_projects():

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

    # Example DataFrame
    df_projects = call_rl_api('projects?includeArchive.eq=false')

    # Streamlit app title
    st.title("Active RocketLane Projects")

    st.subheader("Select Columns to Display")
    selected_columns = st.multiselect(
        "Select columns to include in the table:",
        options=df_projects.columns.tolist(),
        #default=df_projects.columns.tolist()  # By default, select all columns
        default=['projectId','projectName','customer.companyName','startDate','dueDate','owner.firstName','status.label']
    )

    # Filter the DataFrame based on selected columns
    filtered_df = df_projects[selected_columns]

    # Display dataframe as HTML table
    html_table = render_html_table(filtered_df)
    st.markdown(html_table, unsafe_allow_html=True)

# Main logic
if __name__ == "__main__":
    display_active_projects()
