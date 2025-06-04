import streamlit as st
import time

welcome_message = """
# Welcome to NSQAS

### Find appropriate data set and data provider for your model.
"""

# @st.cache_data
def stream_welcome():

    for word in welcome_message.split(" "):
        yield word + " "
        time.sleep(0.2)

# @st.cache_data
def stream_welcome_call():
    st.write_stream(stream_welcome)

stream_welcome_call()

def model_form_func():

    @st.dialog("enter your model details")
    def model_form():
        with st.form("model info form"):
            st.file_uploader("upload the joblib ai model file")
            st.file_uploader("upload the data set file")
            st.form_submit_button()

    model_form()

st.button("Fill model info", 
          key="model-info-btn", 
          help="fill the information for the model", 
          on_click=model_form_func
          )

