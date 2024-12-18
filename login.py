import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader


# For authentication purposes, load the users.yaml
with open('users.yaml') as file:
    user_config = yaml.load(file, Loader=SafeLoader)

st.set_page_config(page_title="Fiddler RocketLane Time Reporting",layout='wide')

# Create the authenticator object
authenticator = stauth.Authenticate(
    user_config['credentials'],
    user_config['cookie']['name'],
    user_config['cookie']['key'],
    user_config['cookie']['expiry_days']
)
print("streamlit version: ", st.__version__)
#print("streamlit auth version: ", stauth.__version__)

# Render the login widget by providing a name for the form and its location (i.e., sidebar or main)
name, authentication_status, username = authenticator.login("Login", "sidebar")

print("authentication_status: " + str(authentication_status))

# Confirm the users was properly authenticated
#if authentication_status:
if authentication_status:
    st.session_state['authenticated'] = True
    st.session_state['username'] = username
    page_function = ''
    if 'page_function' in st.query_params:   
        page_function = st.query_params['page_function']
    if page_function == 'billable_report': 
        st.switch_page("pages/billable_report.py")
    else:
        st.switch_page("pages/projects.py")
elif authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')