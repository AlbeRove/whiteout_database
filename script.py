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
        # Check if the player ID is already in active players list
        if new_player_id in active_players["Player ID"].values:
            st.error(f"Player ID {new_player_id} is already in Active Players.")
        else:
            new_entry = pd.DataFrame([[new_player_name, new_player_id, datetime.now()]], 
                                     columns=["Player Name", "Player ID", "Time Added"])
            active_players = pd.concat([active_players, new_entry], ignore_index=True)
            save_data()
            st.success(f"Player {new_player_name} added to Active Players.")
    else:
        st.error("Please enter both Player Name and Player ID.")

# Function to render tables with action dropdowns
def render_table(title, df, action_buttons):
    st.subheader(title)

    if not df.empty:
        for index, row in df.iterrows():
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])

            col1.write(row["Player Name"])
            col2.write(row["Player ID"])
            col3.write(format_datetime(row.get("Time Added", row.get("Time Banned", row.get("Time Removed", "")))))

            # Action dropdown (instead of expanding)
            with col4:
                action = st.selectbox("Choose action", ["", *action_buttons], key=f"action_{index}")

                if action:
                    with st.spinner(f"Processing {action}..."):
                        if action == "🚫 Ban":
                            banned_players.loc[len(banned_players)] = row
                            banned_players.iloc[-1, banned_players.columns.get_loc("Time Banned")] = datetime.now()
                            df.drop(index, inplace=True)
                            save_data()
                            st.experimental_rerun()
            
                        elif action == "🔄 Move to active":
                            if row["Player ID"] in active_players["Player ID"].values:
                                st.error(f"Player {row['Player Name']} is already in Active Players.")
                            else:
                                active_players.loc[len(active_players)] = row
                                active_players.iloc[-1, active_players.columns.get_loc("Time Added")] = datetime.now()
                                df.drop(index, inplace=True)
                                save_data()
                                st.experimental_rerun()
            
                        elif action == "❌ Remove":
                            # Move player to Former Players instead of just dropping
                            former_players.loc[len(former_players)] = row
                            former_players.iloc[-1, former_players.columns.get_loc("Time Removed")] = datetime.now()
                            df.drop(index, inplace=True)
                            save_data()
                            st.experimental_rerun()

    else:
        st.info(f"No {title.lower()} yet.")

# Render tables
render_table("Active Players", active_players, ["ban", "remove"])
render_table("Banned Players", banned_players, ["remove"])
render_table("Former Players", former_players, ["restore", "remove"])

# SAVE button (green, rounded corners)
st.markdown(
    "<style> div.stButton > button:first-child { background-color: #4CAF50; color: white; border-radius: 15px; width: 100px; height: 40px; font-size: 16px; } </style>", 
    unsafe_allow_html=True
)
if st.button("SAVE"):
    save_data()
    st.success("All data has been saved!")
