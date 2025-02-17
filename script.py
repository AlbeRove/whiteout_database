import sqlite3
import streamlit as st
import pandas as pd

# Initialize database
def init_db():
    conn = sqlite3.connect("group_members.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contributions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER,
            date TEXT,
            contribution INTEGER,
            FOREIGN KEY(member_id) REFERENCES members(id)
        )
    ''')
    conn.commit()
    conn.close()

# Insert member
def add_member(name, role):
    conn = sqlite3.connect("group_members.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO members (name, role) VALUES (?, ?)", (name, role))
    conn.commit()
    conn.close()

# Insert contribution
def add_contribution(member_id, date, contribution):
    conn = sqlite3.connect("group_members.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO contributions (member_id, date, contribution) VALUES (?, ?, ?)", (member_id, date, contribution))
    conn.commit()
    conn.close()

# Fetch members
def get_members():
    conn = sqlite3.connect("group_members.db")
    df = pd.read_sql("SELECT * FROM members", conn)
    conn.close()
    return df

# Fetch contributions
def get_contributions():
    conn = sqlite3.connect("group_members.db")
    df = pd.read_sql("SELECT members.name, contributions.date, contributions.contribution FROM contributions JOIN members ON contributions.member_id = members.id", conn)
    conn.close()
    return df

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
date = st.date_input("Date")
contribution = st.number_input("Contribution", min_value=0, step=1)
if st.button("Add Contribution"):
    add_contribution(member_id, date, contribution)
    st.success("Contribution added successfully!")

# View Data
st.subheader("Members")
st.dataframe(get_members())

st.subheader("Contributions")
st.dataframe(get_contributions())
