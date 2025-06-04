import streamlit as st
import pandas as pd
import numpy as np
from database.database import get_db
from database.db_operations import (
    get_selected_datasets,
    delete_selected_dataset,
    update_selected_dataset,
    get_dataset_by_id
)
import io

def delete_model_dataset(selected_id: int):
    try:
        db = next(get_db())
        if delete_selected_dataset(db, selected_id):
            st.success(f"Dataset selection deleted successfully!")
            st.rerun()
        else:
            st.error("Could not delete the dataset selection. Please try again.")
    except Exception as e:
        st.error(f"Error deleting dataset selection: {str(e)}")
    finally:
        if 'db' in locals():
            db.close()

def modify_model_dataset(row_data):
    try:
        db = next(get_db())
        with st.form(key=f"modify_form_{row_data['id']}"):
            st.write("### Modify Model and Dataset")
            modified_model_name = st.text_input("Model Name", value=row_data["model Name"])
            modified_dataset_name = st.text_input("Dataset Name", value=row_data["dataset Name"])
            
            if st.form_submit_button("Save Changes"):
                try:
                    updated = update_selected_dataset(
                        db=db,
                        selected_id=row_data['id'],
                        model_name=modified_model_name,
                        dataset_name=modified_dataset_name
                    )
                    if updated:
                        st.success(f"Successfully updated dataset selection!")
                        st.rerun()
                    else:
                        st.error("Could not update the dataset selection. Please try again.")
                except Exception as e:
                    st.error(f"Database error while updating: {str(e)}")
                return True
        return False
    except Exception as e:
        st.error(f"Error in modification form: {str(e)}")
    finally:
        if 'db' in locals():
            db.close()

def download_dataset_file(dataset_name: str, dataset_id: int):
    try:
        db = next(get_db())
        dataset = get_dataset_by_id(db, dataset_id)
        if dataset and dataset.file_data:
            # Create download button
            st.download_button(
                label="Download Dataset",
                data=dataset.file_data,
                file_name=dataset.file_name,
                mime="application/octet-stream"
            )
        else:
            st.error("Dataset file not found")
    except Exception as e:
        st.error(f"Error downloading dataset: {str(e)}")
    finally:
        if 'db' in locals():
            db.close()



def selected_datasets():
    st.write("## Your selected datasets for your model")

    try:
        # Get database session
        db = next(get_db())
        
        # Get all selected datasets
        selected_datasets_list = get_selected_datasets(db)
        
        if not selected_datasets_list:
            st.info("No datasets have been selected yet.")
            return

        # Convert to DataFrame
        df = pd.DataFrame([{
            "Sr. No.": idx + 1,
            "id": dataset.id,
            "model Id": dataset.model_id,
            "model Name": dataset.model_name,
            "dataset Id": dataset.dataset_id,
            "dataset Name": dataset.dataset_name,
            "action": "none"
        } for idx, dataset in enumerate(selected_datasets_list)])

        # Display the DataFrame without the ID column
        edited_df = st.data_editor(
            df,
            column_config={
                "Sr. No.": st.column_config.Column("Sr. No.", disabled=True),
                "model Id": st.column_config.Column("Model ID", disabled=True),
                "model Name": st.column_config.Column("Model Name", disabled=True),
                "dataset Id": st.column_config.Column("Dataset ID", disabled=True),
                "dataset Name": st.column_config.Column("Dataset Name", disabled=True),
                "action": st.column_config.SelectboxColumn(
                    "action",
                    width="medium",
                    default="none",
                    options=["none", "delete", "modify", "download dataset"]
                ),
            },
            hide_index=True,
            column_order=["Sr. No.", "model Id", "model Name", "dataset Id", "dataset Name", "action"]
        )

        # Handle actions for each row
        for idx, row in edited_df.iterrows():
            action = row["action"]
            if action != "none":
                with st.container():
                    if action == "delete":
                        delete_model_dataset(row["id"])
                    elif action == "modify":
                        modify_model_dataset(row)
                    elif action == "download dataset":
                        download_dataset_file(row["dataset Name"], row["dataset Id"])

    except Exception as e:
        st.error(f"Error loading selected datasets: {str(e)}")
        st.write("Full error details:", e)  # Add this line for debugging
    finally:
        if 'db' in locals():
            db.close()
