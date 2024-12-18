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
def render_html_table(df):
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

    # Add a "Generate Billable Report" link that directs to the second page using query parameter
    if 'projectId' in df.columns:
        df['Action'] = df['projectId'].apply(lambda x: f'<a href="billable_report?page_function=billable_report&project_id={x}" target="_self">Billable Report</a>')

    # Move 'Action' column to the front
    cols = df.columns.tolist()
    cols = [cols[-1]] + cols[:-1]
    df = df[cols]

    # Convert dataframe to HTML and append the CSS
    html_table = df.to_html(escape=False, index=False)
    return html_table + css