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
col1, col2 = st.columns([1, 1])  # Create two columns for the buttons

# Player Name and ID input fields
with col1:
    new_player_name = st.text_input("Player Name", key="player_name")
with col2:
    new_player_id = st.text_input("Player ID", key="player_id")

# Add Player Button in green
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
                # Clear input fields *before* using the session_state variables
                st.session_state["player_name"] = ""
                st.session_state["player_id"] = ""

# Ban Player Button in red
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
        
        # Clear input fields *before* using the session_state variables
        st.session_state["player_name"] = ""
        st.session_state["player_id"] = ""

# Function to render tables (with scroll functionality if more than 10 entries)
def render_table(title, df):
    st.subheader(title)

    if not df.empty:
        if len(df) > 10:
            st.dataframe(df, height=300)  # Scrollable table if more than 10 rows
        else:
            for index, row in df.iterrows():
                col1, col2, col3 = st.columns([3, 2, 2])

                col1.write(row["Player Name"])
                col2.write(f"<p style='color: white;'>{row['Player ID']}</p>", unsafe_allow_html=True)  # Player ID in white
                col3.write(format_datetime(row.get("Time Added", row.get("Time Banned", row.get("Time Removed", "")))))
    else:
        st.info(f"No {title.lower()} yet.")

# Render tables without action buttons
render_table("Active Players", active_players)
render_table("Banned Players", banned_players)
render_table("Former Players", former_players)

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
