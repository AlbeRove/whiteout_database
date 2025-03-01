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

# Ensure session state keys exist
if "player_name" not in st.session_state:
    st.session_state.player_name = ""
if "player_id" not in st.session_state:
    st.session_state.player_id = ""

# Add Active Player and Ban Player Buttons side by side
st.subheader("Add or Ban Player")
new_player_name = st.text_input("Player Name", key="player_name")
new_player_id = st.text_input("Player ID", key="player_id")

col1, col2 = st.columns([1, 1])  # Create two columns for the buttons

# Add Player Button in green (via Markdown with custom HTML)
with col1:
    if st.button("Add Player"):
        if new_player_name and new_player_id:
            # Check if the player ID already exists in any list
            if new_player_id in active_players["Player ID"].values or \
               new_player_id in banned_players["Player ID"].values or \
               new_player_id in former_players["Player ID"].values:
                st.error(f"Player ID {new_player_id} already exists in the system.")
            elif new_player_id in banned_players["Player ID"].values:
                st.warning(f"Player ID {new_player_id} is currently banned. Cannot add as an active player.")
            else:
                # Add player to active list
                new_entry = pd.DataFrame([[new_player_name, new_player_id, datetime.now()]], 
                                         columns=["Player Name", "Player ID", "Time Added"])
                active_players = pd.concat([active_players, new_entry], ignore_index=True)
                save_data()
                st.success(f"Player {new_player_name} added to Active Players.")
                # Clear input fields after adding the player
                st.session_state.player_name = ""
                st.session_state.player_id = ""

# Ban Player Button logic
with col2:
    if st.button("Ban Player"):
        if new_player_name and new_player_id:
            # Check if the player is already in banned or former players
            if new_player_id in banned_players["Player ID"].values:
                st.error(f"Player ID {new_player_id} is already banned.")
            elif new_player_id in former_players["Player ID"].values:
                # If the player is in former players, move them to banned players
                player_in_former = former_players[former_players["Player ID"] == new_player_id]
                banned_players = pd.concat([banned_players, player_in_former], ignore_index=True)
                banned_players.iloc[-1, banned_players.columns.get_loc("Time Banned")] = datetime.now()
                former_players = former_players[former_players["Player ID"] != new_player_id]
                save_data()
                st.success(f"Player {new_player_name} moved from Former Players to Banned Players.")
            else:
                # If the player is in active players, move them to banned
                player_in_active = active_players[active_players["Player ID"] == new_player_id]
                if not player_in_active.empty:
                    banned_players.loc[len(banned_players)] = player_in_active.iloc[0]
                    banned_players.iloc[-1, banned_players.columns.get_loc("Time Banned")] = datetime.now()
                    active_players = active_players[active_players["Player ID"] != new_player_id]
                    save_data()
                    st.success(f"Player {new_player_name} has been banned from Active Players.")
                else:
                    # If the player is not in active, just add them to banned list
                    new_entry = pd.DataFrame([[new_player_name, new_player_id, datetime.now()]], 
                                             columns=["Player Name", "Player ID", "Time Banned"])
                    banned_players = pd.concat([banned_players, new_entry], ignore_index=True)
                    save_data()
                    st.success(f"Player {new_player_name} has been directly added to Banned Players.")
        
        # Clear input fields after banning the player
        st.session_state.player_name = ""
        st.session_state.player_id = ""

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
                        # If not in active players, directly add to banned
                        banned_players.loc[len(banned_players)] = selected_player
                        banned_players.iloc[-1, banned_players.columns.get_loc("Time Banned")] = datetime.now()
                        save_data()
                        st.success(f"Player {selected_player['Player Name']} has been added to Banned Players.")
                elif action == "Restore":
                    if selected_player["Player ID"] in banned_players["Player ID"].values:
                        active_players.loc[len(active_players)] = selected_player
                        active_players.iloc[-1, active_players.columns.get_loc("Time Added")] = datetime.now()
                        banned_players = banned_players[banned_players["Player ID"] != selected_player["Player ID"]]
                        save_data()
                        st.success(f"Player {selected_player['Player Name']} has been restored
