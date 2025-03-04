import streamlit as st
import requests
import base64
import os

def upload_to_github(repo, branch="master"):
    """
    Uploads active_players.csv, banned_players.csv, and former_players.csv to the specified GitHub repository.

    Args:
        repo (str): Your GitHub repository in the format "username/repo-name".
        branch (str, optional): The branch to upload the files to. Defaults to "main".
    """

    # Load GitHub Token
    GITHUB_TOKEN = st.secrets["github"]["token"] if "github" in st.secrets else os.getenv("GITHUB_TOKEN")
    if not GITHUB_TOKEN:
        st.error("GitHub token is missing! Store it in Streamlit secrets or an environment variable.")
        return

    # File names
    files = ["active_players.csv", "banned_players.csv", "former_players.csv"]

    # GitHub API URL
    base_url = f"https://api.github.com/repos/{repo}/contents/"

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    for file_name in files:
        try:
            # Read file content
            with open(file_name, "rb") as f:
                content = base64.b64encode(f.read()).decode()

            file_url = base_url + file_name

            # Check if the file already exists (to get the SHA)
            response = requests.get(file_url, headers=headers)
            sha = response.json().get("sha", "")

            # Prepare API request payload
            data = {
                "message": f"Update {file_name}",
                "content": content,
                "branch": branch
            }
            if sha:
                data["sha"] = sha  # Required for updating existing files

            # Upload file via GitHub API
            response = requests.put(file_url, headers=headers, json=data)

            if response.status_code in [200, 201]:
                st.success(f"✅ Successfully uploaded {file_name} to {repo} on {branch} branch!")
            else:
                st.error(f"❌ Failed to upload {file_name}. Response: {response.json()}")

        except Exception as e:
            st.error(f"⚠️ Error uploading {file_name}: {e}")

