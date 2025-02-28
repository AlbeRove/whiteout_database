import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Setup the database and tables
Base = declarative_base()

class ActivePlayer(Base):
    __tablename__ = 'active_players'
    ID = Column(Integer, primary_key=True, autoincrement=True)
    Name = Column(String, nullable=False)
    Player_ID = Column(String, nullable=False, unique=True)
    Time_Added = Column(DateTime, nullable=False)

class BannedPlayer(Base):
    __tablename__ = 'banned_players'
    ID = Column(Integer, primary_key=True, autoincrement=True)
    Name = Column(String, nullable=False)
    Player_ID = Column(String, nullable=False, unique=True)
    Time_Banned = Column(DateTime, nullable=False)

# Initialize database
def init_db():
    engine = create_engine("sqlite:///alliance_players.db")
    Base.metadata.create_all(engine)

# Insert player into active players
def add_player(name, player_id):
    engine = create_engine("sqlite:///alliance_players.db")
    Session = sessionmaker(bind=engine)
    session = Session()
    new_player = ActivePlayer(Name=name, Player_ID=player_id, Time_Added=datetime.now())
    session.add(new_player)
    session.commit()
    session.close()

# Ban player (move from active to banned)
def ban_player(player_id):
    engine = create_engine("sqlite:///alliance_players.db")
    Session = sessionmaker(bind=engine)
    session = Session()
    
    player = session.query(ActivePlayer).filter_by(Player_ID=player_id).first()
    if player:
        # Move to banned players table
        banned_player = BannedPlayer(Name=player.Name, Player_ID=player.Player_ID, Time_Banned=datetime.now())
        session.add(banned_player)
        session.delete(player)
        session.commit()
    session.close()

# Fetch active players
def get_active_players():
    engine = create_engine("sqlite:///alliance_players.db")
    Session = sessionmaker(bind=engine)
    session = Session()
    players = session.query(ActivePlayer).all()
    session.close()
    return pd.DataFrame([(player.ID, player.Name, player.Player_ID, player.Time_Added) for player in players], 
                        columns=["ID", "Name", "Player ID", "Time Added"])

# Fetch banned players
def get_banned_players():
    engine = create_engine("sqlite:///alliance_players.db")
    Session = sessionmaker(bind=engine)
    session = Session()
    players = session.query(BannedPlayer).all()
    session.close()
    return pd.DataFrame([(player.ID, player.Name, player.Player_ID, player.Time_Banned) for player in players], 
                        columns=["ID", "Name", "Player ID", "Time Banned"])

# Streamlit UI
st.title("Alliance Players Management")
init_db()

# Add Player Form
st.subheader("Add Player")
name = st.text_input("Player Name")
player_id = st.text_input("Player ID")
if st.button("Add Player"):
    add_player(name, player_id)
    st.success(f"Player {name} added successfully!")

# Ban Player Form
st.subheader("Ban Player")
players_df = get_active_players()
player_id_to_ban = st.selectbox("Select Player to Ban", players_df["Player ID"].tolist() if not players_df.empty else [], 
                                format_func=lambda x: players_df[players_df["Player ID"] == x]["Name"].values[0] if not players_df.empty else "")
if st.button("Ban Player"):
    ban_player(player_id_to_ban)
    st.success(f"Player with ID {player_id_to_ban} has been banned!")

# View Active Players
st.subheader("Active Players")
st.dataframe(get_active_players())

# View Banned Players
st.subheader("Banned Players")
st.dataframe(get_banned_players())
