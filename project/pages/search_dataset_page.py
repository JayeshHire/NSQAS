import streamlit as st
import numpy as np
import pandas as pd
from database.database import get_db
from database.db_operations import (
    get_all_ai_models,
    get_user_by_email,
    get_necessity_scores,
    get_ai_model_by_id,
    get_dataset_by_id,
    create_selected_dataset
)
from database.models import SelectedDataset
from Datasetfilter.necessity_score_calc import NecessityScoreCalculator
import re
import time

def demo_function(dataset_id):
    st.session_state['dataset_id'] = dataset_id
    st.write("Demo function")
    print(f"Demo function, dataset_id: {dataset_id}")

@st.fragment
def choose_datasets(model_id: int):
    
    # Store the model_id in session state so we can access it after form submission
    st.session_state['current_model_id'] = model_id
    
    st.write("Choose datasets for your model")
    
    # Create form
    with st.form("choose_datasets"):
        dataset_id = st.text_input("Enter dataset ID")
        
        submitted_btn = st.form_submit_button("Submit")

        # if submitted_btn :
        #     st.session_state['dataset_id'] = dataset_id
        #     demo_function(dataset_id)

    # # Check if form was submitted
        if submitted_btn:
            try:
                db = next(get_db())
                # Convert dataset_id to integer
                dataset_id_int = int(dataset_id)
            #     
                # Get the dataset and model objects
                dataset = get_dataset_by_id(db, dataset_id_int)
                model = get_ai_model_by_id(db, model_id)
            #     
                if not dataset or not model:
                    st.error("Dataset or model not found!")
                    return
                  #   
                # Create the selected dataset using the proper function
                selected_dataset = create_selected_dataset(
                    db=db,
                    model_id=model_id,  # Use the raw model_id
                    model_name=model.name,
                    dataset_id=dataset_id_int,  # Use the converted dataset_id
                    dataset_name=dataset.name
                )
            #     
                if selected_dataset:
                    st.success(f"Dataset '{dataset.name}' selected successfully!")
                    st.toast("Dataset selected successfully!")
                    # Clear the form by removing it from session state
                    if 'choose_datasets' in st.session_state:
                        del st.session_state['choose_datasets']
                    st.rerun()
            #   
            except ValueError:
                st.error("Please enter a valid dataset ID (must be a number)")
            except Exception as e:
                st.error(f"Error selecting dataset: {str(e)}")
            finally:
                if 'db' in locals():
                    db.close()

def search_datasets():

    st.session_state['dataset_id'] = None
    with st.form(key="search_dataset_form"):
        st.title("Search datasets")

        db = next(get_db())
                
        # Check if user is logged in
        if not st.user.is_logged_in:
            st.error("You must be logged in to upload datasets.")
            return
            
        # Get current user's ID
        current_user = get_user_by_email(db, st.user.email)

        models = get_all_ai_models(db, owner_id=current_user.id)
        models_names = [f"{model.name} (version {model.version}) (id: {model.id})" for model in models]
        selected_model = st.selectbox("Select a model", 
                                    options=models_names, 
                                    index=0)
        submitted = st.form_submit_button("Search")

        if submitted:
            st.write("Search for datasets")
            model_id = re.search(r"\(id:\s*(\d+)\)", selected_model)

            NS = NecessityScoreCalculator(models[0].id)
            score_lst = NS.get_necessity_scores()
            
            score_lst.sort(key=lambda x: x[0], reverse=True)
            scores = [score[0]*100 for score in score_lst]
            dataset_ids = [score[1] for score in score_lst]
            dataset_names = [get_dataset_by_id(db, dataset_id).name for dataset_id in dataset_ids]
            dataset_accuracies = [get_dataset_by_id(db, dataset_id).accuracy for dataset_id in dataset_ids]
            dataset_upload_dates = [get_dataset_by_id(db, dataset_id).upload_date for dataset_id in dataset_ids]
            dataset_versions = [get_dataset_by_id(db, dataset_id).version for dataset_id in dataset_ids]
            dataset_descriptions = [get_dataset_by_id(db, dataset_id).description for dataset_id in dataset_ids]
            
            st.success("Search completed!")

            df = pd.DataFrame(
                {
                    "Sr. No.": np.arange(1, len(dataset_ids) + 1, 1),
                    "Dataset Id": dataset_ids,
                    "Dataset name": dataset_names,
                    "Description": dataset_descriptions,
                    "Version": dataset_versions,
                    "Upload Date": dataset_upload_dates,
                    "Accuracy": dataset_accuracies,
                    "Score": scores,
                }
            )

            edited_df = st.data_editor(
                df,
                column_config={
                    "Dataset name": st.column_config.TextColumn("Dataset Name"),
                    "Description": st.column_config.TextColumn("Description"),
                    "Version": st.column_config.TextColumn("Version"),
                    "Upload Date": st.column_config.DateColumn("Upload Date"),
                }
            )

    if submitted:
        model_id_int = model_id.string[model_id.span()[0]:model_id.span()[1]].strip("()").split(": ")[1]
        st.button("Select datasets", key="select_datasets", on_click=choose_datasets, args=(int(model_id_int),))

    if st.session_state['dataset_id']:
        print(f"dataset_id: {st.session_state['dataset_id']}")
