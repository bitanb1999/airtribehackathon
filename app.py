import streamlit as st
import sqlite3
from youtube_transcript_api import YouTubeTranscriptApi
import openai

# Set up OpenAI API Key
openai.api_key = st.secrets["openai_key"]

# Database setup
conn = sqlite3.connect("youtube_links.db")
cursor = conn.cursor()

# Update schema to include summary if not already present
cursor.execute("""
    CREATE TABLE IF NOT EXISTS links (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        youtube_link TEXT NOT NULL UNIQUE,
        summary TEXT
    )
""")
conn.commit()

# Helper function to extract video ID from link
def extract_video_id(link):
    if "youtube.com" in link:
        return link.split("v=")[-1]
    elif "youtu.be" in link:
        return link.split("/")[-1]
    else:
        return None

# Helper function to summarize text using OpenAI API
def summarize_text(text):
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"Summarize this text:\n\n{text}",
            max_tokens=150
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"Error in summarization: {e}"

# Streamlit app
st.title("YouTube Link and Summary Collector")

# Input YouTube link
link = st.text_input("Enter a YouTube link:", "")

if st.button("Submit"):
    if link:
        video_id = extract_video_id(link)
        if video_id:
            try:
                # Fetch transcript
                transcript = YouTubeTranscriptApi.get_transcript(video_id)
                transcript_text = " ".join([entry['text'] for entry in transcript])

                # Generate summary
                summary = summarize_text(transcript_text)

                # Store link and summary in the database
                cursor.execute(
                    "INSERT OR IGNORE INTO links (youtube_link, summary) VALUES (?, ?)",
                    (link, summary)
                )
                conn.commit()
                st.success("Link and summary added successfully!")
                st.write(f"**Summary:** {summary}")
            except Exception as e:
                st.error(f"Error fetching or summarizing video: {e}")
        else:
            st.error("Invalid YouTube link.")
    else:
        st.error("Please enter a valid YouTube link.")

# Display stored links and summaries
st.subheader("Stored Links and Summaries")
cursor.execute("SELECT youtube_link, summary FROM links")
rows = cursor.fetchall()

for row in rows:
    st.write(f"**Link:** {row[0]}")
    st.write(f"**Summary:** {row[1]}")
    st.write("---")
