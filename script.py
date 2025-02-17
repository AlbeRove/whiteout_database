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
    ID = Column(Integer, primary_key=True, autoincrement=True)
    Name = Column(String, nullable=False)
    Role = Column(String, nullable=False)
    Join_Date = Column(String, nullable=False)  # Join Date as String
    Status = Column(String, nullable=False)  # Status column
    contributions = relationship("Contribution", backref="member", cascade="all, delete-orphan")

class Contribution(Base):
    __tablename__ = 'contributions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey('members.ID'), nullable=False)
    date = Column(String, nullable=False)
    contribution = Column(Integer, nullable=False)

# Initialize database
def init_db():
    engine = create_engine("sqlite:///group_members.db")
    Base.metadata.create_all(engine)

# Insert member
def add_member(name, role, join_date, status):
    engine = create_engine("sqlite:///group_members.db")
    Session = sessionmaker(bind=engine)
    session = Session()
    join_date_str = join_date.strftime('%Y-%m-%d')  # Convert date to string format
    new_member = Member(Name=name, Role=role, Join_Date=join_date_str, Status=status)
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
    return pd.DataFrame([(member.ID, member.Name, member.Role, member.Join_Date, member.Status) for member in members], 
                        columns=["ID", "Name", "Role", "Join Date", "Status"])

# Fetch contributions with days of the week and total
def get_contributions():
    engine = create_engine("sqlite:///group_members.db")
    Session = sessionmaker(bind=engine)
    session = Session()
    contributions = session.query(Contribution, Member.Name).join(Member).all()
    session.close()
    
    # Prepare a DataFrame
    contribution_data = []
    for contribution, member_name in contributions:
        day_of_week = datetime.strptime(contribution.date, '%Y-%m-%d').strftime('%a')  # Get the day of the week (Mon, Tue, ...)
        contribution_data.append([member_name, day_of_week, contribution.date, contribution.contribution])
    
    # Create DataFrame
    df = pd.DataFrame(contribution_data, columns=["Member Name", "Day", "Date", "Contribution"])
    
    # Pivot the table to get contributions by day (MON, TUE, etc.)
    df_pivot = df.pivot_table(index=["Member Name"], columns="Day", values="Contribution", aggfunc="sum", fill_value=0)
    
    # Add Total column
    df_pivot["TOTAL"] = df_pivot.sum(axis=1)
    
    return df_pivot.reset_index()

# Streamlit UI
st.title("Group Members & Contributions")
init_db()

# Add Member
st.subheader("Add Member")
name = st.text_input("Name")
role = st.text_input("Role")
join_date = st.date_input("Join Date", min_value=datetime(2020, 1, 1), max_value=datetime.today())
status = st.selectbox("Status", ["Active", "Inactive"])
if st.button("Add Member"):
    add_member(name, role, join_date, status)
    st.success("Member added successfully!")

# Add Contribution
st.subheader("Add Contribution")
members_df = get_members()
member_id = st.selectbox("Select Member", members_df["ID"].tolist() if not members_df.empty else [], 
                         format_func=lambda x: members_df[members_df.ID == x].Name.values[0] if not members_df.empty else "")
date = st.date_input("Date", min_value=datetime(2020, 1, 1), max_value=datetime.today())
contribution = st.number_input("Contribution", min_value=0, step=1)
if st.button("Add Contribution"):
    add_contribution(member_id, str(date), contribution)
    st.success("Contribution added successfully!")

# View Data
st.subheader("Members")
st.dataframe(get_members())

st.subheader("Contributions by Day")
st.dataframe(get_contributions())
