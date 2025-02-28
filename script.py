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
        return pd.read_csv(file_path)
    return pd.DataFrame(columns=columns)

# Save data to CSV
def save_data(df, file_path):
    df.to_csv(file_path, index=False)

# Initialize player lists
active_players = load_data(ACTIVE_PLAYERS_FILE, ["Player Name", "Player ID", "Time Added"])
banned_players = load_data(BANNED_PLAYERS_FILE, ["Player Name", "Player ID", "Time Banned"])
former_players = load_data(FORMER_PLAYERS_FILE, ["Player Name", "Player ID", "Time Removed"])

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
        save_data(active_players, ACTIVE_PLAYERS_FILE)
        st.success(f"Player {new_player_name} added to Active Players.")
    else:
        st.error("Please enter both Player Name and Player ID.")

# Remove Active Player (Moves to Former Players)
st.subheader("Remove Active Player")
if not active_players.empty:
    remove_player_name = st.selectbox("Select Player to Remove", active_players["Player Name"].tolist())
    if st.button("Remove Player"):
        player_data = active_players[active_players["Player Name"] == remove_player_name]
        former_entry = player_data.copy()
        former_entry["Time Removed"] = datetime.now()
        
        active_players = active_players[active_players["Player Name"] != remove_player_name]
        former_players = pd.concat([former_players, former_entry], ignore_index=True)
        
        save_data(active_players, ACTIVE_PLAYERS_FILE)
        save_data(former_players, FORMER_PLAYERS_FILE)
        
        st.success(f"Player {remove_player_name} moved to Former Players.")
else:
    st.warning("No active players available to remove.")

# Ban Player (Moves to Banned Players)
st.subheader("Ban Player")
if not active_players.empty:
    ban_player_name = st.selectbox("Select Player to Ban", active_players["Player Name"].tolist())
    if st.button("Ban Player"):
        player_data = active_players[active_players["Player Name"] == ban_player_name]
        banned_entry = player_data.copy()
        banned_entry["Time Banned"] = datetime.now()

        active_players = active_players[active_players["Player Name"] != ban_player_name]
        banned_players = pd.concat([banned_players, banned_entry], ignore_index=True)

        save_data(active_players, ACTIVE_PLAYERS_FILE)
        save_data(banned_players, BANNED_PLAYERS_FILE)

        st.success(f"Player {ban_player_name} has been banned.")
else:
    st.warning("No active players available to ban.")

# View Active Players
st.subheader("Active Players")
st.dataframe(active_players)

# View Banned Players
st.subheader("Banned Players")
st.dataframe(banned_players)

# View Former Players
st.subheader("Former Players")
st.dataframe(former_players)

# Remove All Banned Players
if st.button("Remove All Banned Players"):
    banned_players = pd.DataFrame(columns=["Player Name", "Player ID", "Time Banned"])
    save_data(banned_players, BANNED_PLAYERS_FILE)
    st.success("All banned players have been removed!")

# Remove All Former Players
if st.button("Remove All Former Players"):
    former_players = pd.DataFrame(columns=["Player Name", "Player ID", "Time Removed"])
    save_data(former_players, FORMER_PLAYERS_FILE)
    st.success("All former players have been removed!")

# Save Data Buttons
st.subheader("Export Data")
if st.button("Save Active Players to CSV"):
    save_data(active_players, ACTIVE_PLAYERS_FILE)
    st.success("Active players saved to CSV!")

if st.button("Save Banned Players to CSV"):
    save_data(banned_players, BANNED_PLAYERS_FILE)
    st.success("Banned players saved to CSV!")

if st.button("Save Former Players to CSV"):
    save_data(former_players, FORMER_PLAYERS_FILE)
    st.success("Former players saved to CSV!")
