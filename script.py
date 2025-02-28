import streamlit as st
import pandas as pd
import os
from datetime import datetime

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

# Streamlit UI
st.title("Alliance Players Management")

# Add Active Player
st.subheader("Add Active Player")
new_player_name = st.text_input("Player Name")
new_player_id = st.text_input("Player ID")
if st.button("Add Player"):
    if new_player_name and new_player_id:
        # Check if the player ID already exists in any list
        if new_player_id in active_players["Player ID"].values or \
           new_player_id in banned_players["Player ID"].values or \
           new_player_id in former_players["Player ID"].values:
            st.error(f"Player ID {new_player_id} already exists in the system.")
        else:
            new_entry = pd.DataFrame([[new_player_name, new_player_id, datetime.now()]], 
                                     columns=["Player Name", "Player ID", "Time Added"])
            active_players = pd.concat([active_players, new_entry], ignore_index=True)
            save_data()
            st.success(f"Player {new_player_name} added to Active Players.")
            # No rerun here; Streamlit will refresh automatically
    else:
        st.error("Please enter both Player Name and Player ID.")

# Function to render tables (without action buttons)
def render_table(title, df):
    st.subheader(title)

    if not df.empty:
        for index, row in df.iterrows():
            col1, col2, col3 = st.columns([3, 2, 2])

            col1.write(row["Player Name"])
            col2.write(row["Player ID"])
            col3.write(format_datetime(row.get("Time Added", row.get("Time Banned", row.get("Time Removed", "")))))
    else:
        st.info(f"No {title.lower()} yet.")

# Render tables without action buttons
render_table("Active Players", active_players)
render_table("Banned Players", banned_players)
render_table("Former Players", former_players)

# Player Search & Management Section
st.subheader("Player Management")
search_query = st.text_input("Search for a player by name or ID")

# Filter players from all lists based on the search query
# Convert 'Player ID' and 'Player Name' columns to strings before applying .str.contains()
filtered_players = pd.concat([active_players, banned_players, former_players])
filtered_players = filtered_players[
    filtered_players['Player Name'].astype(str).str.contains(search_query, case=False, na=False) |
    filtered_players['Player ID'].astype(str).str.contains(search_query, case=False, na=False)
]

if not filtered_players.empty:
    player_to_manage = st.selectbox("Select Player to Manage", filtered_players["Player Name"].unique())

    # Find selected player details
    selected_player = filtered_players[filtered_players["Player Name"] == player_to_manage].iloc[0]

    st.write(f"**Player Name**: {selected_player['Player Name']}")
    st.write(f"**Player ID**: {selected_player['Player ID']}")

    # Provide management options
    action = st.radio("Choose an action", ["Ban", "Restore", "Remove"])

    if action:
        if st.button("Confirm"):
            with st.spinner(f"Processing {action}..."):
                if action == "Ban":
                    if selected_player["Player ID"] in active_players["Player ID"].values:
                        banned_players.loc[len(banned_players)] = selected_player
                        banned_players.iloc[-1, banned_players.columns.get_loc("Time Banned")] = datetime.now()
                        active_players = active_players[active_players["Player ID"] != selected_player["Player ID"]]
                        save_data()
                        st.success(f"Player {selected_player['Player Name']} has been banned.")
                        # No rerun here; Streamlit will refresh automatically
                    else:
                        st.error(f"Player {selected_player['Player Name']} is already banned or removed.")

                elif action == "Restore":
                    if selected_player["Player ID"] in banned_players["Player ID"].values:
                        active_players.loc[len(active_players)] = selected_player
                        active_players.iloc[-1, active_players.columns.get_loc("Time Added")] = datetime.now()
                        banned_players = banned_players[banned_players["Player ID"] != selected_player["Player ID"]]
                        save_data()
                        st.success(f"Player {selected_player['Player Name']} has been restored.")
                        # No rerun here; Streamlit will refresh automatically
                    else:
                        st.error(f"Player {selected_player['Player Name']} is not in the banned list.")

                elif action == "Remove":
                    if selected_player["Player ID"] not in former_players["Player ID"].values:
                        former_players.loc[len(former_players)] = selected_player
                        former_players.iloc[-1, former_players.columns.get_loc("Time Removed")] = datetime.now()
                        active_players = active_players[active_players["Player ID"] != selected_player["Player ID"]]
                        banned_players = banned_players[banned_players["Player ID"] != selected_player["Player ID"]]
                        save_data()
                        st.success(f"Player {selected_player['Player Name']} has been removed.")
                        # No rerun here; Streamlit will refresh automatically
                    else:
                        st.error(f"Player {selected_player['Player Name']} is already removed.")
                st.rerun()
                
    else:
        st.info("Select an action and click Confirm.")

else:
    st.info("No players found. Try refining your search.")

# SAVE button (green, rounded corners)
st.markdown(
    "<style> div.stButton > button:first-child { background-color: #4CAF50; color: white; border-radius: 15px; width: 100px; height: 40px; font-size: 16px; } </style>", 
    unsafe_allow_html=True
)
if st.button("SAVE"):
    save_data()
    st.success("All data has been saved!")
