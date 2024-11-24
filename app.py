import streamlit as st
import sqlite3

# Database setup
conn = sqlite3.connect("youtube_links.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS links (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        youtube_link TEXT NOT NULL UNIQUE
    )
""")
conn.commit()

# Streamlit app
st.title("YouTube Link Collector")

# Input YouTube link
link = st.text_input("Enter a YouTube link:", "")

if st.button("Submit"):
    if link:
        try:
            cursor.execute("INSERT INTO links (youtube_link) VALUES (?)", (link,))
            conn.commit()
            st.success("Link added successfully!")
        except sqlite3.IntegrityError:
            st.warning("This link is already in the database.")
    else:
        st.error("Please enter a valid YouTube link.")

# Display stored links
st.subheader("Stored Links")
cursor.execute("SELECT youtube_link FROM links")
rows = cursor.fetchall()

for row in rows:
    st.write(row[0])
