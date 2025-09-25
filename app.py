import streamlit as st
import json
import os
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk

# Ensure the VADER lexicon is downloaded
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except nltk.downloader.DownloadError:
    nltk.download('vader_lexicon')

# Initialize the sentiment analyzer
sia = SentimentIntensityAnalyzer()

DATA_FILE = "posts.json"

# --- Data Persistence Functions ---
def load_posts():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_posts(posts):
    with open(DATA_FILE, "w") as f:
        json.dump(posts, f, indent=4)

# --- App Logic ---
if 'posts' not in st.session_state:
    st.session_state.posts = load_posts()

st.title("Mental Health-Aware Community Forum")

# --- Create a new post ---
st.header("Create a New Post")
with st.form(key="new_post_form", clear_on_submit=True):
    post_title = st.text_input("Post Title")
    post_content = st.text_area("What's on your mind?")
    submit_button = st.form_submit_button(label="Post")

    if submit_button:
        if post_title and post_content:
            new_post = {"title": post_title, "content": post_content, "replies": []}
            st.session_state.posts.append(new_post)
            save_posts(st.session_state.posts)
            st.success("Your post has been submitted!")
        else:
            st.warning("Please fill in both the title and content.")

# --- Display existing posts and handle replies ---
st.header("Community Feed")
if not st.session_state.posts:
    st.write("No posts yet. Be the first to start a conversation!")
else:
    for index, post in enumerate(reversed(st.session_state.posts)):
        st.subheader(post["title"])
        st.write(post["content"])

        # --- UI IMPROVEMENT IS HERE ---
        # Display existing replies inside an expander
        if post["replies"]:
            with st.expander(f"View replies ({len(post['replies'])})"):
                for reply in post["replies"]:
                    st.info(f"💬 {reply}")
        # --- END OF UI IMPROVEMENT ---

        with st.form(key=f"reply_form_{index}", clear_on_submit=True):
            reply_content = st.text_input("Write a reply...", placeholder="Be kind and respectful.")
            reply_submit = st.form_submit_button("Reply")

            if reply_submit and reply_content:
                sentiment_scores = sia.polarity_scores(reply_content)
                if sentiment_scores['compound'] >= -0.05:
                    original_post_index = len(st.session_state.posts) - 1 - index
                    st.session_state.posts[original_post_index]["replies"].append(reply_content)
                    save_posts(st.session_state.posts)
                    st.success("Your reply was posted!")
                    st.rerun()
                else:
                    st.error("Your comment was flagged as potentially negative and was not posted. Please try again. ❤️")
        
        st.markdown("---")