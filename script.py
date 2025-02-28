import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Setup the database and tables
Base = declarative_base()

class ActivePlayer(Base):
    __tablename__ = 'active_players'
    Player_ID = Column(String, primary_key=True)
    Name = Column(String, nullable=False)
    Time_Added = Column(DateTime, nullable=False)

class BannedPlayer(Base):
    __tablename__ = 'banned_players'
    Player_ID = Column(String, primary_key=True)
    Name = Column(String, nullable=False)
    Time_Banned = Column(DateTime, nullable=False)

class FormerPlayer(Base):
    __tablename__ = 'former_players'
    Player_ID = Column(String, primary_key=True)
    Name = Column(String, nullable=False)
    Time_Removed = Column(DateTime, nullable=False)

# Initialize database
def init_db():
    engine = create_engine("sqlite:///alliance_players.db")
    Base.metadata.create_all(engine)

# Database session helper
def get_session():
    engine = create_engine("sqlite:///alliance_players.db")
    Session = sessionmaker(bind=engine)
    return Session()

# Add an active player
def add_active_player(player_id, name):
    session = get_session()
    new_player = ActivePlayer(Player_ID=player_id, Name=name, Time_Added=datetime.now())
    session.add(new_player)
    session.commit()
    session.close()

# Remove an active player (move to former players)
def remove_active_player(player_id, name):
    session = get_session()
    active_player = session.query(ActivePlayer).filter_by(Player_ID=player_id).first()
    if active_player:
        session.delete(active_player)
        session.commit()
        former_player = FormerPlayer(Player_ID=player_id, Name=name, Time_Removed=datetime.now())
        session.add(former_player)
        session.commit()
    session.close()

# Ban a player (remove from active and add to banned)
def ban_player(player_id, name):
    session = get_session()
    active_player = session.query(ActivePlayer).filter_by(Player_ID=player_id).first()
    if active_player:
        session.delete(active_player)
        session.commit()
    
    banned_player = BannedPlayer(Player_ID=player_id, Name=name, Time_Banned=datetime.now())
    session.add(banned_player)
    session.commit()
    session.close()

# Remove all banned players
def remove_all_banned_players():
    session = get_session()
    session.query(BannedPlayer).delete()
    session.commit()
    session.close()

# Remove all former players
def remove_all_former_players():
    session = get_session()
    session.query(FormerPlayer).delete()
    session.commit()
    session.close()

# Fetch active players
def get_active_players():
    session = get_session()
    players = session.query(ActivePlayer).all()
    session.close()
    return pd.DataFrame([(p.Player_ID, p.Name, p.Time_Added) for p in players], columns=["Player ID", "Name", "Time Added"])

# Fetch banned players
def get_banned_players():
    session = get_session()
    players = session.query(BannedPlayer).all()
    session.close()
    return pd.DataFrame([(p.Player_ID, p.Name, p.Time_Banned) for p in players], columns=["Player ID", "Name", "Time Banned"])

# Fetch former players
def get_former_players():
    session = get_session()
    players = session.query(FormerPlayer).all()
    session.close()
    return pd.DataFrame([(p.Player_ID, p.Name, p.Time_Removed) for p in players], columns=["Player ID", "Name", "Time Removed"])

# Streamlit UI
st.title("Alliance Players Management")
init_db()

# Add a new active player
st.subheader("Add Active Player")
new_player_id = st.text_input("Player ID")
new_player_name = st.text_input("Player Name")
if st.button("Add Player"):
    if new_player_id and new_player_name:
        add_active_player(new_player_id, new_player_name)
        st.success(f"Player {new_player_name} (ID: {new_player_id}) added as an active player.")
    else:
        st.error("Please enter both Player ID and Name.")

# Remove an active player
st.subheader("Remove Active Player")
active_players = get_active_players()
if not active_players.empty:
    remove_player_id = st.selectbox("Select Player to Remove", active_players["Player ID"].tolist(), 
                                    format_func=lambda x: active_players[active_players["Player ID"] == x]["Name"].values[0])
    if st.button("Remove Player"):
        remove_active_player(remove_player_id, active_players[active_players["Player ID"] == remove_player_id]["Name"].values[0])
        st.success(f"Player {remove_player_id} has been moved to former players.")
else:
    st.warning("No active players available to remove.")

# Ban Player (Directly by Player ID and Name)
st.subheader("Ban Player")
ban_player_id = st.text_input("Enter Player ID to Ban")
ban_player_name = st.text_input("Enter Player Name")
if st.button("Ban Player"):
    if ban_player_id and ban_player_name:
        ban_player(ban_player_id, ban_player_name)
        st.success(f"Player {ban_player_name} (ID: {ban_player_id}) has been banned.")
    else:
        st.error("Please enter both Player ID and Name.")

# View Active Players
st.subheader("Active Players")
st.dataframe(get_active_players())

# View Banned Players
st.subheader("Banned Players")
st.dataframe(get_banned_players())

# Button to remove all banned players
if st.button("Remove All Banned Players"):
    remove_all_banned_players()
    st.success("All banned players have been removed!")

# View Former Players
st.subheader("Former Players")
st.dataframe(get_former_players())

# Button to remove all former players
if st.button("Remove All Former Players"):
    remove_all_former_players()
    st.success("All former players have been removed!")
