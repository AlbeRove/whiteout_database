import streamlit as st
import pandas as pd
import os
from datetime import datetime
from utils import *
from save_changes import *
import subprocess
import streamlit.components.v1 as components

def ChangeButtonColour(widget_label, font_color, background_color='transparent'):
    htmlstr = f"""
        <script>
            var elements = window.parent.document.querySelectorAll('button');
            for (var i = 0; i < elements.length; ++i) {{ 
                if (elements[i].innerText == '{widget_label}') {{ 
                    elements[i].style.color ='{font_color}';
                    elements[i].style.background = '{background_color}'
                }}
            }}
        </script>
        """
    components.html(f"{htmlstr}", height=0, width=0)

# Streamlit UI
st.title("[ARW] Players management app")
st.markdown("by Pollo1907 🐔")

# File paths for CSV storage
ACTIVE_PLAYERS_FILE = "active_players.csv"
BANNED_PLAYERS_FILE = "banned_players.csv"
FORMER_PLAYERS_FILE = "former_players.csv"
# Initialize player lists
active_load = load_data(ACTIVE_PLAYERS_FILE, ["Player Name", "Player ID", "Time Added"])
banned_load = load_data(BANNED_PLAYERS_FILE, ["Player Name", "Player ID", "Time Banned"])
former_load = load_data(FORMER_PLAYERS_FILE, ["Player Name", "Player ID", "Time Removed"])

active_players = active_load.copy()
banned_players = banned_load.copy()
former_players = former_load.copy()

active_players["Player ID"] = active_players["Player ID"].astype(str)
banned_players["Player ID"] = banned_players["Player ID"].astype(str)
former_players["Player ID"] = former_players["Player ID"].astype(str)

# Player Name and ID input fields
new_player_name = st.text_input("Enter Player Name", key="player_name")
new_player_name = new_player_name.replace("[ARW]", "")

new_player_id = str(st.text_input("Enter Player ID", key="player_id"))

# Add Active Player and Ban Player Buttons side by side
col1, col2 = st.columns([1,1])  # Create two columns for the buttons

# Add Player Button
with col1:
    confirm_clicked = st.button("Confirm", key="confirm", help="Confirm a player")
    ChangeButtonColour('Confirm', 'white', '#45a049')
# Ban Player Button in red
with col2:
    ban_clicked = st.button("Ban", key="ban", help="Ban a player")
    ChangeButtonColour('Ban', 'white', '#d32f2f')
if confirm_clicked:
    if not new_player_name and new_player_id:
        st.error('Please enter a valid player name and ID')
    else:
        # Check if the player ID exists in any list
        if new_player_id in active_players["Player ID"].values:
            st.error(f"Player ID {new_player_name} is already in Active Players.")
            
        elif new_player_id in banned_players["Player ID"].values:
            st.warning(f"Player ID {new_player_id} is currently banned. Cannot add as an active player.")
            
        elif new_player_id in former_players["Player ID"].values:
            # If the player is in former players, move them to active
            player_in_former = former_players[former_players["Player ID"] == new_player_id]
            active_players = pd.concat([active_players, player_in_former], ignore_index=True)
            active_players.iloc[-1, active_players.columns.get_loc("Time Added")] = datetime.now().strftime("%d:%m:%Y %H:%M").strftime("%d:%m:%Y %H:%M")
            former_players = former_players[former_players["Player ID"] != new_player_id]
            st.success(f"Player {new_player_name} moved to Active Players.")
        else:
            # If the player is not found in any list, add them to active players
            new_entry = pd.DataFrame([[new_player_name, new_player_id, datetime.now().strftime("%d:%m:%Y %H:%M")]], 
                                     columns=["Player Name", "Player ID", "Time Added"])
            active_players = pd.concat([active_players, new_entry], ignore_index=True)
            st.success(f"Player {new_player_name} added to Active Players.")



if ban_clicked:
    if not new_player_name and new_player_id:
        st.error('Please enter a valid player name and ID')
    else:
        # Check if the player is already in banned or former players
        if new_player_id in banned_players["Player ID"].values:
            st.error(f"Player ID {new_player_id} is already banned.")
        
        elif new_player_id in former_players["Player ID"].values:
            # If the player is in former players, move them to banned players
            player_in_former = former_players[former_players["Player ID"] == new_player_id]
            banned_players = pd.concat([banned_players, player_in_former], ignore_index=True)
            banned_players.iloc[-1, banned_players.columns.get_loc("Time Banned")] = datetime.now().strftime("%d:%m:%Y %H:%M")
            former_players = former_players[former_players["Player ID"] != new_player_id]
            st.success(f"Player {new_player_name} moved from Former Players to Banned Players.")
        elif new_player_id in active_players["Player ID"].values:
            # If the player is in active players, move them to banned
            player_in_active = active_players[active_players["Player ID"] == new_player_id]
            banned_players = pd.concat([banned_players, player_in_active], ignore_index=True)
            banned_players.iloc[-1, banned_players.columns.get_loc("Time Added")] = datetime.now().strftime("%d:%m:%Y %H:%M")
            active_players = active_players[active_players["Player ID"] != new_player_id]
            st.success(f"Player {new_player_name} has been banned from Active Players.")
        else:
            # If the player is not in active, just add them to banned list
            new_entry = pd.DataFrame([[new_player_name, new_player_id, datetime.now().strftime("%d:%m:%Y %H:%M")]], 
                                     columns=["Player Name", "Player ID", "Time Banned"])
            banned_players = pd.concat([banned_players, new_entry], ignore_index=True)
            st.success(f"Player {new_player_name} has been directly added to Banned Players.")


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
                col2.write(f"<p style='color: white;'>{row['Player ID']}</p>", unsafe_allow_html=True)
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
    action = st.radio("Choose an action", ["Ban", "Re-join alliance", "Remove from alliance"])

    if action:
        confirm_change = st.button("Confirm")
        ChangeButtonColour('Confirm', 'white', '#45a049')
        if confirm_change:
            with st.spinner(f"Processing {action}..."):
                if action == "Ban":
                    if selected_player["Player ID"] in active_players["Player ID"].values:
                        banned_players.loc[len(banned_players)] = selected_player
                        banned_players.iloc[-1, banned_players.columns.get_loc("Time Banned")] = datetime.now().strftime("%d:%m:%Y %H:%M")
                        active_players = active_players[active_players["Player ID"] != selected_player["Player ID"]]
                        st.success(f"Player {selected_player['Player Name']} has been banned.")
                    elif selected_player["Player ID"] in former_players["Player ID"].values:
                        banned_players.loc[len(banned_players)] = selected_player
                        banned_players.iloc[-1, banned_players.columns.get_loc("Time Banned")] = datetime.now().strftime("%d:%m:%Y %H:%M")
                        former_players = former_players[former_players["Player ID"] != selected_player["Player ID"]]
                        st.success(f"Player {selected_player['Player Name']} has been banned.")
                    else:
                        st.error(f"Player {selected_player['Player Name']} is already banned or removed.")

                elif action == "Re-join alliance":
                    if selected_player["Player ID"] in banned_players["Player ID"].values:
                        active_players.loc[len(active_players)] = selected_player
                        active_players.iloc[-1, active_players.columns.get_loc("Time Added")] = datetime.now().strftime("%d:%m:%Y %H:%M")
                        banned_players = banned_players[banned_players["Player ID"] != selected_player["Player ID"]]
                        st.success(f"Player {selected_player['Player Name']} has been restored.")
                    else:
                        st.error(f"Player {selected_player['Player Name']} is not in the banned list.")

                elif action == "Remove from active":
                    if selected_player["Player ID"] not in former_players["Player ID"].values:
                        former_players.loc[len(former_players)] = selected_player
                        former_players.iloc[-1, former_players.columns.get_loc("Time Removed")] = datetime.now().strftime("%d:%m:%Y %H:%M")
                        active_players = active_players[active_players["Player ID"] != selected_player["Player ID"]]
                        banned_players = banned_players[banned_players["Player ID"] != selected_player["Player ID"]]
                        st.success(f"Player {selected_player['Player Name']} has been removed.")
                    else:
                        st.error(f"Player {selected_player['Player Name']} is already removed.")
                st.rerun()
                
    else:
        st.info("Select an action and click Confirm.")

else:
    st.info("No players found")

GITHUB_REPO = 'AlbeRove/whiteout_database'
save_clicked = st.button('Save')
ChangeButtonColour('Save', 'white', '#1C86EE')
if save_clicked:
    save_data(active_players, banned_players, former_players)
    print(banned_players)
#    upload_to_github(GITHUB_REPO)
    upload_dataframe_to_github(banned_players, 'banned_players.csv', GITHUB_REPO, branch="master")
    st.success("All data has been saved!")


# Add download buttons
st.subheader("Download Data Files")
# Download Active Players CSV
csv_active = active_players.to_csv(index=False)
st.download_button(label="Download Active Players CSV",
                   data=csv_active,
                   file_name="active_players.csv",
                   mime="text/csv")

# Download Banned Players CSV
csv_banned = banned_players.to_csv(index=False)
st.download_button(label="Download Banned Players CSV",
                   data=csv_banned,
                   file_name="banned_players.csv",
                   mime="text/csv")

# Download Former Players CSV
csv_former = former_players.to_csv(index=False)
st.download_button(label="Download Former Players CSV",
                   data=csv_former,
                   file_name="former_players.csv",
                   mime="text/csv")
