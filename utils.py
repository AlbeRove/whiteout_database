import pandas as pd
from datetime import datetime
import os

# File paths for CSV storage
ACTIVE_PLAYERS_FILE = "active_players.csv"
BANNED_PLAYERS_FILE = "banned_players.csv"
FORMER_PLAYERS_FILE = "former_players.csv"

# Load data from CSV files
def load_data(file_path, columns):
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            if df.empty:
                return pd.DataFrame(columns=columns)
            return df
        except pd.errors.EmptyDataError:
            return pd.DataFrame(columns=columns)
    return pd.DataFrame(columns=columns)

# Save data to CSV
def save_data():
    active_players.to_csv(ACTIVE_PLAYERS_FILE, index=False)
    banned_players.to_csv(BANNED_PLAYERS_FILE, index=False)
    former_players.to_csv(FORMER_PLAYERS_FILE, index=False)

    # Add Git commands to push changes
    subprocess.run(["git", "add", "active_players.csv", "banned_players.csv", "former_players.csv"])
    subprocess.run(["git", "commit", "-m", "Updated player data"])
    subprocess.run(["git", "push", "origin", "main"])  # Adjust branch name if needed

# Initialize player lists
active_players = load_data(ACTIVE_PLAYERS_FILE, ["Player Name", "Player ID", "Time Added"])
banned_players = load_data(BANNED_PLAYERS_FILE, ["Player Name", "Player ID", "Time Banned"])
former_players = load_data(FORMER_PLAYERS_FILE, ["Player Name", "Player ID", "Time Removed"])

# Format date-time function
def format_datetime(dt):
    if pd.isna(dt) or dt == "":
        return ""
    try:
        return datetime.strptime(str(dt), "%Y-%m-%d %H:%M:%S.%f").strftime("%d-%m-%Y %H:%M")
    except ValueError:
        return str(dt)
