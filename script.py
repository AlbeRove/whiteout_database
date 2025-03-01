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
st.title("[ARW] Players management app")
st.markdown("by Pollo1907 🐔")

# Add Active Player and Ban Player Buttons side by side
st.subheader("Add or Ban Player")
new_player_name = st.text_input("Player Name", key="player_name")
new_player_id = st.text_input("Player ID", key="player_id")

col1, col2 = st.columns([1, 1])  # Create two columns for the buttons

# Add Player Button in green (via Markdown with custom HTML)
with col1:
    add_player_button = st.markdown(
        """
        <style>
        .green-button {
            background-color: #4CAF50;
            color: white;
            border-radius: 15px;
            width: 120px;
            height: 40px;
            font-size: 16px;
            text-align: center;
            cursor: pointer;
            border: none;
        }
        </style>
        <button class="green-button" onclick="window.location.reload()">Add Player</button>
        """,
        unsafe_allow_html=True
    )

# Ban Player Button in red (via Markdown with custom HTML)
with col2:
    ban_player_button = st.markdown(
        """
        <style>
        .red-button {
            background-color: #F44336;
            color: white;
            border-radius: 15px;
            width: 120px;
            height: 40px;
            font-size: 16px;
            text-align: center;
            cursor: pointer;
            border: none;
        }
        </style>
        <button class="red-button" onclick="window.location.reload()">Ban Player</button>
        """,
        unsafe_allow_html=True
    )

# Add custom button logic
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
            # Clear input fields after adding the player
            st.session_state.player_name = ""
            st.session_state.player_id = ""

if st.button("Ban Player"):
    if new_player_name and new_player_id:
        # Check if the player exists in active players before banning
        player_exists = active_players[active_players["Player ID"] == new_player_id]
        if not player_exists.empty:
            banned_players.loc[len(banned_players)] = player_exists.iloc[0]
            banned_players.iloc[-1, banned_players.columns.get_loc("Time Banned")] = datetime.now()
            active_players = active_players[active_players["Player ID"] != new_player_id]
            save_data()
            st.success(f"Player {new_player_name} has been banned.")
            # Clear input fields after banning the player
            st.session_state.player_name = ""
            st.session_state.player_id = ""
        else:
            st.error(f"Player ID {new_player_id} not found in Active Players.")
    else:
        st.error("Please enter both Player Name and Player ID.")

# Render tables with scroll feature for more than 10 entries
def render_table(title, df):
    st.subheader(title)

    if not df.empty:
        if len(df) > 10:
            # Add a scrollable table if the table has more than 10 rows
            st.dataframe(df, height=300)  # This will create a scrollable table
        else:
            # Render normal table if less than 10 rows
            st.table(df)
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
    st.write(f"**Player ID**: {selected_player['Player ID']}")  # Player ID now in default white color

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


# Add download buttons
st.subheader("Download Data Files")
# Download Active Players CSV
csv_active = active_players.to_csv(index=False)
st.download_button(
    label="Download Active Players CSV",
    data=csv_active,
    file_name="active_players.csv",
    mime="text/csv"
)

# Download Banned Players CSV
csv_banned = banned_players.to_csv(index=False)
st.download_button(
    label="Download Banned Players CSV",
    data=csv_banned,
    file_name="banned_players.csv",
    mime="text/csv"
)

# Download Former Players CSV
csv_former = former_players.to_csv(index=False)
st.download_button(
    label="Download Former Players CSV",
    data=csv_former,
    file_name="former_players.csv",
    mime="text/csv"
)
