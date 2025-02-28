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
    Player_ID = Column(String, primary_key=True)  # Use Player_ID as the primary key
    Name = Column(String, nullable=False)
    Time_Added = Column(DateTime, nullable=False)

class BannedPlayer(Base):
    __tablename__ = 'banned_players'
    Player_ID = Column(String, primary_key=True)  # Use Player_ID as the primary key
    Name = Column(String, nullable=False)
    Time_Banned = Column(DateTime, nullable=False)

class FormerPlayer(Base):
    __tablename__ = 'former_players'
    Player_ID = Column(String, primary_key=True)  # Use Player_ID as the primary key
    Name = Column(String, nullable=False)
    Time_Removed = Column(DateTime, nullable=False)

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
    
    # Try to fetch player from active players
    player = session.query(ActivePlayer).filter_by(Player_ID=player_id).first()
    if player:
        # Move to banned players table
        banned_player = BannedPlayer(Name=player.Name, Player_ID=player.Player_ID, Time_Banned=datetime.now())
        session.add(banned_player)
        session.delete(player)
        session.commit()
    else:
        # If player not found in active players, directly ban them
        banned_player = session.query(BannedPlayer).filter_by(Player_ID=player_id).first()
        if not banned_player:
            # Player is not already banned
            banned_player = BannedPlayer(Name="Unknown", Player_ID=player_id, Time_Banned=datetime.now())
            session.add(banned_player)
            session.commit()
    session.close()

# Remove player from active players and move to former players
def remove_player(player_id):
    engine = create_engine("sqlite:///alliance_players.db")
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Fetch the player and move them to former players
    player = session.query(ActivePlayer).filter_by(Player_ID=player_id).first()
    if player:
        # Add player to former players
        former_player = FormerPlayer(Name=player.Name, Player_ID=player.Player_ID, Time_Removed=datetime.now())
        session.add(former_player)
        # Remove from active players
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

# Fetch former players
def get_former_players():
    engine = create_engine("sqlite:///alliance_players.db")
    Session = sessionmaker(bind=engine)
    session = Session()
    players = session.query(FormerPlayer).all()
    session.close()
    return pd.DataFrame([(player.Player_ID, player.Name, player.Time_Removed) for player in players], 
                        columns=["Player ID", "Name", "Time Removed"])

# Get Player Name based on Player ID
def get_player_name_by_id(player_id):
    engine = create_engine("sqlite:///alliance_players.db")
    Session = sessionmaker(bind=engine)
    session = Session()
    player = session.query(ActivePlayer).filter_by(Player_ID=player_id).first()
    session.close()
    return player.Name if player else None

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
st.subheader("Ban Player (From Active Players)")
players_df = get_active_players()
player_id_to_ban = st.selectbox("Select Player to Ban", players_df["Player ID"].tolist() if not players_df.empty else [], 
                                format_func=lambda x: players_df[players_df["Player ID"] == x]["Name"].values[0] if not players_df.empty else "")
if st.button("Ban Player"):
    ban_player(player_id_to_ban)
    st.success(f"Player with ID {player_id_to_ban} has been banned!")

# Direct Ban Player Form (for non-active players)
st.subheader("Ban Player (Directly by Player ID)")
player_id_to_ban_direct = st.text_input("Enter Player ID to Ban")
player_name_direct = None
if player_id_to_ban_direct:
    player_name_direct = get_player_name_by_id(player_id_to_ban_direct)
if player_name_direct:
    st.write(f"Player Name: {player_name_direct}")
if st.button("Directly Ban Player"):
    if player_id_to_ban_direct:
        ban_player(player_id_to_ban_direct)
        st.success(f"Player with ID {player_id_to_ban_direct} has been banned!")

# Remove Player Form (From Active Players)
st.subheader("Remove Player (From Active Players Only)")
player_id_to_remove = st.selectbox("Select Player to Remove", players_df["Player ID"].tolist() if not players_df.empty else [],
                                   format_func=lambda x: players_df[players_df["Player ID"] == x]["Name"].values[0] if not players_df.empty else "")
if st.button("Remove Player"):
    remove_player(player_id_to_remove)
    st.success(f"Player with ID {player_id_to_remove} has been removed from Active Players!")

# View Active Players
st.subheader("Active Players")
st.dataframe(get_active_players())

# View Banned Players
st.subheader("Banned Players")
st.dataframe(get_banned_players())

# View Former Players
st.subheader("Former Players")
st.dataframe(get_former_players())
