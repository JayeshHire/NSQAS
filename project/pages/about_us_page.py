import streamlit as st
import time

about_sub_title = "## Know more about the NSQAS"

content = """
NSQAS (Necessity Scoring and Quality Assessment System) is created to help users to find relevant and quality information for training their ai models.
This is a web based application that helps users to discover and evaluate the quality of data sources for training their AI models.
The application provides a user-friendly interface for users to search for data sources, view their quality scores, and make informed decisions about which data sources to use.
The application is designed to be easy to use and accessible to users of all skill levels.
"""

def text_stream():
    markdown_text = f"{about_sub_title}"
    for word in markdown_text.split(" "):
        yield word + " "
        time.sleep(0.4)

def stream_text(text):
    st.write_stream(text_stream(text))

def justify_text(text):
    st.markdown(f"<div style='text-align: justify;'>{text}</div>", unsafe_allow_html=True)

@st.cache_data
def about_us():
    """
    This function displays the about us page.
    """
    st.title("Our Vision")
    st.write_stream(text_stream)
    st.markdown(f"<div style='text-align: justify;'>{content}</div>", unsafe_allow_html=True)