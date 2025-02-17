import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

# Setup the database and tables
Base = declarative_base()

class Member(Base):
    __tablename__ = 'members'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)
    contributions = relationship("Contribution", backref="member", cascade="all, delete-orphan")

class Contribution(Base):
    __tablename__ = 'contributions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey('members.id'), nullable=False)
    date = Column(String, nullable=False)
    contribution = Column(Integer, nullable=False)

# Initialize database
def init_db():
    engine = create_engine("sqlite:///group_members.db")
    Base.metadata.create_all(engine)

# Insert member
def add_member(name, role):
    engine = create_engine("sqlite:///group_members.db")
    Session = sessionmaker(bind=engine)
    session = Session()
    new_member = Member(name=name, role=role)
    session.add(new_member)
    session.commit()
    session.close()

# Insert contribution
def add_contribution(member_id, date, contribution):
    engine = create_engine("sqlite:///group_members.db")
    Session = sessionmaker(bind=engine)
    session = Session()
    new_contribution = Contribution(member_id=member_id, date=date, contribution=contribution)
    session.add(new_contribution)
    session.commit()
    session.close()

# Fetch members
def get_members():
    engine = create_engine("sqlite:///group_members.db")
    Session = sessionmaker(bind=engine)
    session = Session()
    members = session.query(Member).all()
    session.close()
    return pd.DataFrame([(member.id, member.name, member.role) for member in members], columns=["id", "name", "role"])

# Fetch contributions
def get_contributions():
    engine = create_engine("sqlite:///group_members.db")
    Session = sessionmaker(bind=engine)
    session = Session()
    contributions = session.query(Contribution, Member.name).join(Member).all()
    session.close()
    return pd.DataFrame([(contribution.date, contribution.contribution, member_name) for contribution, member_name in contributions], columns=["date", "contribution", "member_name"])

# Streamlit UI
st.title("Group Members & Contributions")
init_db()

# Add Member
st.subheader("Add Member")
name = st.text_input("Name")
role = st.text_input("Role")
if st.button("Add Member"):
    add_member(name, role)
    st.success("Member added successfully!")

# Add Contribution
st.subheader("Add Contribution")
members_df = get_members()
member_id = st.selectbox("Select Member", members_df["id"].tolist() if not members_df.empty else [], format_func=lambda x: members_df[members_df.id == x].name.values[0] if not members_df.empty else "")
date = st.date_input("Date", min_value=datetime(2020, 1, 1), max_value=datetime.today())
contribution = st.number_input("Contribution", min_value=0, step=1)
if st.button("Add Contribution"):
    add_contribution(member_id, str(date), contribution)
    st.success("Contribution added successfully!")

# View Data
st.subheader("Members")
st.dataframe(get_members())

st.subheader("Contributions")
st.dataframe(get_contributions())
