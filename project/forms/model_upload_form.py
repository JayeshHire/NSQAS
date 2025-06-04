import streamlit as st


def model_form():

    st.write("Upload new model")
                # if "model_name" not in st.session_state:
                #     st.session_state["model_name"] = "" 
    model_name = st.text_input("Model Name")
    description = st.text_input("Model Description")
    version = st.text_input("Version") 
    model_file = st.file_uploader(
        "upload model joblib file", 
        accept_multiple_files=False
    )
    training_data_set = st.file_uploader(
        "upload training data",
        accept_multiple_files=False
    )

    submitted = st.button("Submit")

    if submitted:
        st.session_state["model_info"] = (model_name, description, version)