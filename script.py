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
    return datetime.strptime(dt, "%Y-%m-%d %H:%M:%S.%f").strftime("%d-%m-%Y %H:%M") if pd.notna(dt) else ""

# Streamlit UI
st.title("Alliance Players Management")

# Add Active Player
st.subheader("Add Active Player")
new_player_name = st.text_input("Player Name")
new_player_id = st.text_input("Player ID")
if st.button("Add Player"):
    if new_player_name and new_player_id:
        new_entry = pd.DataFrame([[new_player_name, new_player_id, datetime.now()]], 
                                 columns=["Player Name", "Player ID", "Time Added"])
        active_players = pd.concat([active_players, new_entry], ignore_index=True)
        save_data()
        st.success(f"Player {new_player_name} added to Active Players.")
    else:
        st.error("Please enter both Player Name and Player ID.")

# Function to render tables with settings button
def render_table(title, df, action_buttons):
    st.subheader(title)

    if not df.empty:
        for index, row in df.iterrows():
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])

            col1.write(row["Player Name"])
            col2.write(row["Player ID"])
            col3.write(format_datetime(row.get("Time Added", row.get("Time Banned", row.get("Time Removed", "")))))

            # Settings button to expand actions
            with col4:
                if st.button("⚙ Settings", key=f"settings_{index}"):
                    with st.expander(f"Actions for {row['Player Name']}"):
                        if "ban" in action_buttons and st.button("🚫 Ban", key=f"ban_{index}"):
                            banned_players.loc[len(banned_players)] = row
                            banned_players.iloc[-1, banned_players.columns.get_loc("Time Banned")] = datetime.now()
                            df.drop(index, inplace=True)
                            save_data()
                            st.experimental_rerun()

                        if "restore" in action_buttons and st.button("🔄 Restore", key=f"restore_{index}"):
                            active_players.loc[len(active_players)] = row
                            active_players.iloc[-1, active_players.columns.get_loc("Time Added")] = datetime.now()
                            df.drop(index, inplace=True)
                            save_data()
                            st.experimental_rerun()

                        if "remove" in action_buttons and st.button("❌ Remove", key=f"remove_{index}"):
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

