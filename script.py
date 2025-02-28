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

# Add a banned player
def ban_player(player_id, name):
    engine = create_engine("sqlite:///alliance_players.db")
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Check if player exists in active list and remove them
    active_player = session.query(ActivePlayer).filter_by(Player_ID=player_id).first()
    if active_player:
        session.delete(active_player)
        session.commit()
    
    # Add to banned list
    banned_player = BannedPlayer(Player_ID=player_id, Name=name, Time_Banned=datetime.now())
    session.add(banned_player)
    session.commit()
    session.close()

# Remove all banned players
def remove_all_banned_players():
    engine = create_engine("sqlite:///alliance_players.db")
    Session = sessionmaker(bind=engine)
    session = Session()
    session.query(BannedPlayer).delete()
    session.commit()
    session.close()

# Fetch active players
def get_active_players():
    engine = create_engine("sqlite:///alliance_players.db")
    Session = sessionmaker(bind=engine)
    session = Session()
    players = session.query(ActivePlayer).all()
    session.close()
    return pd.DataFrame([(player.Player_ID, player.Name, player.Time_Added) for player in players], 
                        columns=["Player ID", "Name", "Time Added"])

# Fetch banned players
def get_banned_players():
    engine = create_engine("sqlite:///alliance_players.db")
    Session = sessionmaker(bind=engine)
    session = Session()
    players = session.query(BannedPlayer).all()
    session.close()
    return pd.DataFrame([(player.Player_ID, player.Name, player.Time_Banned) for player in players], 
                        columns=["Player ID", "Name", "Time Banned"])

# Streamlit UI
st.title("Alliance Players Management")
init_db()

# View Active Players
st.subheader("Active Players")
st.dataframe(get_active_players())

# Ban Player (Directly by Player ID)
st.subheader("Ban Player (Directly by Player ID and Name)")
player_id_to_ban = st.text_input("Enter Player ID to Ban")
player_name_to_ban = st.text_input("Enter Player Name")
if st.button("Ban Player"):
    if player_id_to_ban and player_name_to_ban:
        ban_player(player_id_to_ban, player_name_to_ban)
        st.success(f"Player {player_name_to_ban} (ID: {player_id_to_ban}) has been banned.")
    else:
        st.error("Please enter both Player ID and Name.")

# View Banned Players
st.subheader("Banned Players")
st.dataframe(get_banned_players())

# Button to remove all banned players
if st.button("Remove All Banned Players"):
    remove_all_banned_players()
    st.success("All banned players have been removed!")
