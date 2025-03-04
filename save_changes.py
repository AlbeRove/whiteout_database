import streamlit as st
import requests
import base64
import os

import streamlit as st
import pandas as pd
import base64
import requests
import os

def upload_dataframe_to_github(df, file_name, repo, branch="master"):
    """
    Uploads a DataFrame to GitHub as a CSV file.

    Args:
        df (pandas.DataFrame): The DataFrame to upload.
        file_name (str): The name of the file (e.g., 'active_players.csv').
        repo (str): The GitHub repository (e.g., 'user/repo-name').
        branch (str, optional): The branch to upload to. Defaults to 'master'.
    """

    # Load GitHub Token
    GITHUB_TOKEN = st.secrets["github"]["token"] if "github" in st.secrets else os.getenv("GITHUB_TOKEN")
    if not GITHUB_TOKEN:
        st.error("GitHub token is missing!")
        return

    # Convert DataFrame to CSV in memory
    csv_data = df.to_csv(index=False)

    # Base64 encode the CSV content
    encoded_content = base64.b64encode(csv_data.encode()).decode()

    # GitHub API URL
    base_url = f"https://api.github.com/repos/{repo}/contents/{file_name}"

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Prepare the API payload
    data = {
        "message": f"Update {file_name}",
        "content": encoded_content,
        "branch": branch
    }

    # Check if the file already exists and get the SHA (if updating)
    response = requests.get(base_url, headers=headers)
    sha = response.json().get("sha", "")

    if sha:
        data["sha"] = sha  # Required for updating existing files

    # Upload the file via the GitHub API
    response = requests.put(base_url, headers=headers, json=data)

    # Debugging the API response
    if response.status_code == 200:
        st.success(f"✅ Successfully uploaded {file_name} to {repo} on {branch}!")
    else:
        st.error(f"❌ Failed to upload {file_name}. Response: {response.json()}")



