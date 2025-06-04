import streamlit as st
import pandas as pd
import numpy as np
from database.database import get_db
from database.db_operations import (
    create_dataset, 
    save_file_data, 
    get_all_datasets, 
    get_user_by_email, 
    get_user_datasets, 
    update_dataset_visibility,
    delete_dataset,
    update_dataset,
    get_dataset_by_id
)
from io import StringIO, BytesIO
from datetime import datetime
from database.models import Dataset
import os
import time


def is_valid_dataset_file(file) -> bool:
    """Check if the file is a valid CSV or Excel file."""
    if file is None:
        return False
    
    # Get file extension from the filename
    file_extension = file.name.lower().split('.')[-1]
    
    # List of allowed file extensions
    allowed_extensions = ['csv', 'xlsx', 'xls']
    
    return file_extension in allowed_extensions


@st.dialog("Upload dataset")
def dataset_upload_handler():
    with st.form("data_upload"):
        st.write("Upload new dataset")
        st.write("Supported file types: CSV, Excel (.xlsx, .xls)")
        
        dataset_name = st.text_input("Dataset Name", help="Enter dataset name")
        version = st.text_input("Dataset version", help="Enter the version of dataset")
        description = st.text_input("Description", help="Describe the dataset")
        dataset_file = st.file_uploader(
            "upload new dataset",
            accept_multiple_files=False,
            type=['csv', 'xlsx', 'xls']
        )

        submitted = st.form_submit_button("Submit")

        if submitted:
            
            if not all([dataset_name, version, description, dataset_file]):
                st.error("Please fill in all required fields and upload a dataset file.")
                return

            if not is_valid_dataset_file(dataset_file):
                st.error("Please upload a valid CSV or Excel file.")
                return

            try:
                # Get file data
                file_data, file_size = save_file_data(dataset_file)
                
                # Get database session
                db = next(get_db())
                
                # Check if user is logged in
                if not st.user.is_logged_in:
                    st.error("You must be logged in to upload datasets.")
                    return
                    
                # Get current user's ID
                current_user = get_user_by_email(db, st.user.email)
                if not current_user:
                    st.error("User not found in database. Please try logging out and back in.")
                    return
                
                # Try to read the file to validate its content
                try:
                    if dataset_file.name.lower().endswith('.csv'):
                        df = pd.read_csv(StringIO(dataset_file.getvalue().decode('utf-8')))
                    else:  # Excel file
                        df = pd.read_excel(BytesIO(dataset_file.getvalue()), sheet_name=0)
                    
                    # Get basic dataset statistics for metadata
                    dataset_metadata = {
                        "columns": df.columns.tolist(),
                        "rows": len(df),
                        "column_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
                        "missing_values": df.isnull().sum().to_dict()
                    }
                except Exception as e:
                    st.error(f"Error reading file: {str(e)}. Please make sure the file is properly formatted.")
                    return
                
                # Create dataset in database with current user's ID
                dataset = create_dataset(
                    db=db,
                    name=dataset_name,
                    owner_id=current_user.id,
                    version=version,
                    description=description,
                    file_data=file_data,
                    file_name=dataset_file.name,
                    file_type=dataset_file.type,
                    file_size=file_size,
                    dataset_metadata=dataset_metadata,
                    is_public=False  # Default to private
                )
                
                st.success(f"Dataset {dataset_name} (version {version}) uploaded successfully!")
                st.session_state["dataset-info"] = {
                    "Dataset Name": dataset_name,
                    "version": version,
                    "description": description
                }
                st.rerun()
            
            except Exception as e:
                st.error(f"Error uploading dataset: {str(e)}")
            finally:
                if 'db' in locals():
                    db.close()

def dataset_operations(loc):
    try:
        operation = st.session_state["dataset_df"].loc[loc]["view"]
        dataset_id = int(st.session_state["dataset_df"].loc[loc]["Dataset Id"])

        def view_dataset(dataset_id: int):
            try:
                db = next(get_db())
                dataset = get_dataset_by_id(db, dataset_id)
                
                if dataset:
                    st.subheader(f"Dataset Details: {dataset.name}")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Basic Information**")
                        st.write(f"- **Name:** {dataset.name}")
                        st.write(f"- **Version:** {dataset.version}")
                        st.write(f"- **Description:** {dataset.description}")
                        st.write(f"- **Upload Date:** {dataset.upload_date.strftime('%Y-%m-%d %H:%M:%S')}")
                        st.write(f"- **Last Updated:** {dataset.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
                        st.write(f"- **Visibility:** {'Public' if dataset.is_public else 'Private'}")
                        
                    with col2:
                        st.write("**Technical Details**")
                        st.write(f"- **File Name:** {dataset.file_name}")
                        st.write(f"- **File Size:** {dataset.file_size / 1024:.2f} KB")
                        st.write(f"- **File Type:** {dataset.file_type}")
                        if dataset.dataset_metadata:
                            st.write("**Dataset Statistics**")
                            st.write(f"- **Rows:** {dataset.dataset_metadata.get('rows', 'N/A')}")
                            st.write(f"- **Columns:** {len(dataset.dataset_metadata.get('columns', []))}")
                            if dataset.contamination is not None:
                                st.write(f"- **Contamination:** {dataset.contamination:.2%}")
                                st.write(f"- **Accuracy:** {dataset.accuracy:.2f}%")
                            else:
                                if st.button("Calculate Contamination", key=f"calc_contamination_{dataset_id}"):
                                    try:
                                        # Run the calculation in the background
                                        cmd = f"python calculate_contamination.py --dataset_id {dataset_id}"
                                        st.info("Starting contamination calculation. This may take a few moments...")
                                        os.system(cmd)
                                        st.success("Contamination calculation started. Please refresh the page in a few moments to see the results.")
                                    except Exception as e:
                                        st.error(f"Error starting contamination calculation: {str(e)}")
                else:
                    st.error("Dataset not found!")
            except Exception as e:
                st.error(f"Error viewing dataset: {str(e)}")
            finally:
                if 'db' in locals():
                    db.close()
        
        def delete_dataset_op(dataset_id: int):
            try:
                if st.button("Confirm Delete", key=f"delete_dataset_{dataset_id}"):
                    db = next(get_db())
                    if delete_dataset(db, dataset_id):
                        st.success("Dataset deleted successfully!")
                        st.rerun()
                    else:
                        st.error("Dataset not found or could not be deleted.")
            except Exception as e:
                st.error(f"Error deleting dataset: {str(e)}")
            finally:
                if 'db' in locals():
                    db.close()

        def reupload_dataset(dataset_id: int):
            try:
                db = next(get_db())
                dataset = get_dataset_by_id(db, dataset_id)
                
                if not dataset:
                    st.error("Dataset not found!")
                    return
                    
                st.subheader(f"Reupload Dataset: {dataset.name}")
                
                with st.form(key=f"reupload_form_{dataset_id}"):
                    dataset_file = st.file_uploader(
                        "Upload new dataset file",
                        accept_multiple_files=False,
                        key=f"reupload_dataset_file_{dataset_id}",
                        type=['csv', 'xlsx', 'xls']
                    )
                    
                    submitted = st.form_submit_button("Update Dataset")
                    
                    if submitted:
                        if not dataset_file:
                            st.error("Please upload a dataset file.")
                            return
                            
                        if not is_valid_dataset_file(dataset_file):
                            st.error("Please upload a valid CSV or Excel file.")
                            return
                            
                        try:
                            # Get file data
                            file_data, file_size = save_file_data(dataset_file)
                            
                            # Try to read the file to validate its content
                            try:
                                if dataset_file.name.lower().endswith('.csv'):
                                    df = pd.read_csv(StringIO(dataset_file.getvalue().decode('utf-8')))
                                else:  # Excel file
                                    df = pd.read_excel(BytesIO(dataset_file.getvalue()))
                                
                                # Get basic dataset statistics for metadata
                                dataset_metadata = {
                                    "columns": df.columns.tolist(),
                                    "rows": len(df),
                                    "column_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
                                    "missing_values": df.isnull().sum().to_dict()
                                }
                            except Exception as e:
                                st.error(f"Error reading file: {str(e)}. Please make sure the file is properly formatted.")
                                return
                            
                            # Update the dataset in the database
                            updated_dataset = update_dataset(
                                db=db,
                                dataset_id=dataset_id,
                                file_data=file_data,
                                file_name=dataset_file.name,
                                file_type=dataset_file.type,
                                file_size=file_size,
                                dataset_metadata=dataset_metadata
                            )
                            
                            if updated_dataset:
                                st.success(f"Dataset {updated_dataset.name} updated successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to update dataset.")
                                
                        except Exception as e:
                            st.error(f"Error updating dataset: {str(e)}")
                            
            except Exception as e:
                st.error(f"Error preparing reupload form: {str(e)}")
            finally:
                if 'db' in locals():
                    db.close()

        if operation == "view":
            view_dataset(dataset_id)
        elif operation == "delete":
            delete_dataset_op(dataset_id)
        elif operation == "reupload":
            reupload_dataset(dataset_id)

    except Exception as e:
        st.error(f"Error processing dataset operation: {str(e)}")

def dataset_visibility_change(loc):
    """Handle dataset visibility changes."""
    db = None
    try:
        if "dataset_df" not in st.session_state:
            st.error("No dataset information found in session state")
            return
            
        df = st.session_state["dataset_df"]
        if loc not in df.index:
            st.error(f"Invalid dataset index: {loc}")
            return
            
        visibility = df.loc[loc, "visibility"]
        dataset_id = int(df.loc[loc, "Dataset Id"])  # Ensure dataset_id is an integer
        
        # Get database session
        db = next(get_db())
        
        # Start a new transaction
        db.begin()
        
        try:
            # Update visibility in database
            is_public = visibility == "public"
            updated_dataset = update_dataset_visibility(db, dataset_id, is_public)
            
            if updated_dataset:
                status = "public" if is_public else "private"
                # Commit the transaction
                db.commit()
                st.toast(f"Successfully updated dataset {dataset_id} visibility to {status}")
            else:
                # Rollback if update failed
                db.rollback()
                st.error(f"Dataset with ID {dataset_id} not found in database")
                
        except Exception as e:
            # Rollback on any error
            db.rollback()
            raise
            
    except Exception as e:
        st.error(f"Error updating dataset visibility: {str(e)}")
        st.write("Full error details:", e)
    finally:
        if db:
            db.close()

def your_datasets():
    st.write("""
    ## Your Uploaded datasets
    """)

    try:
        # Get database session
        db = next(get_db())
        
        # Check if user is logged in
        if not st.user.is_logged_in:
            st.error("You must be logged in to view your datasets.")
            return
            
        # Get current user's ID
        current_user = get_user_by_email(db, st.user.email)
        if not current_user:
            st.error("User not found in database. Please try logging out and back in.")
            return

        # Get user's datasets
        datasets = get_user_datasets(db, current_user.id)
        
        if not datasets:
            st.info("You haven't uploaded any datasets yet.")
        else:
            # Convert datasets to DataFrame
            df = pd.DataFrame([{
                "Sr. No.": idx + 1,
                "Dataset Id": dataset.id,
                "Dataset name": dataset.name,
                "Description": dataset.description,
                "Version": dataset.version,
                "Upload Date": dataset.upload_date.strftime("%Y-%m-%d"),
                "view": None,
                "visibility": "public" if dataset.is_public else "private",
                "Contamination": f"{dataset.contamination:.2%}" if dataset.contamination is not None else "Not calculated",
                "Accuracy": f"{dataset.accuracy:.2f}%" if dataset.accuracy is not None else "Not calculated"
            } for idx, dataset in enumerate(datasets)])

            edited_df = st.data_editor(
                df,
                column_config={
                    "Sr. No.": st.column_config.TextColumn("Sr. No.", disabled=True),
                    "Dataset Id": st.column_config.TextColumn("Dataset Id", disabled=True),      
                    "Dataset name": st.column_config.TextColumn("Dataset Name", disabled=True),
                    "Description": st.column_config.TextColumn("Description", disabled=True),
                    "Version": st.column_config.TextColumn("Version", disabled=True),
                    "Upload Date": st.column_config.TextColumn("Upload Date", disabled=True),
                    "Contamination": st.column_config.TextColumn("Contamination", disabled=True),
                    "Accuracy": st.column_config.TextColumn("Accuracy", disabled=True),
                    "view": st.column_config.SelectboxColumn(
                        "operations",
                        help="View model details",
                        width="medium",
                        options=[None, "view", "delete", "reupload"],
                        default=None,
                        required=False
                    ),
                    "visibility": st.column_config.SelectboxColumn(
                        "visibility",
                        help="Edit who can see your data",
                        width="medium",
                        options=["public", "private"],
                        required=True
                    )
                },
                hide_index=True,
                key="dataset_editor"
            )

            # Store only necessary columns in session state
            st.session_state["dataset_df"] = edited_df[["Dataset Id", "view", "visibility"]]

            # Process any changes
            if edited_df is not None:
                for i in range(len(edited_df)):
                    current_visibility = edited_df.loc[i, "visibility"]
                    dataset_id = edited_df.loc[i, "Dataset Id"]
                    
                    # Check if this is a new change
                    if (
                        "previous_dataset_df" in st.session_state 
                        and i < len(st.session_state["previous_dataset_df"])
                        and st.session_state["previous_dataset_df"].loc[i, "visibility"] != current_visibility
                    ):
                        dataset_visibility_change(i)
                    
                    dataset_operations(i)

            # Store current state for next comparison
            st.session_state["previous_dataset_df"] = edited_df.copy()

    except Exception as e:
        st.error(f"Error loading datasets: {str(e)}")
        st.write("Full error details:", e)
    finally:
        if 'db' in locals():
            db.close()

    st.button("Upload a dataset", key="dataset_upload", on_click=dataset_upload_handler)

    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("Calculate accuracy", key="calc_all_contamination"):
            try:
                import subprocess
                st.info("Starting contamination calculation for all datasets. This may take a few moments...")

                project_path = os.getcwd()
                batch_prg = os.path.join(project_path, "batch", "calculate_contamination.py")
                venv_path = os.path.join(project_path, "..", ".venv", "Scripts", "python.exe")
                subprocess.run([venv_path, batch_prg])

                st.toast("Batch contamination calculation has ended. Please refresh the page in a few moments to see the results.")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"Error starting batch contamination calculation: {str(e)}")

def test():
    import os
    import subprocess
    project_path = os.getcwd()
    batch_prg = os.path.join(project_path, "batch", "calculate_contamination.py")
    venv_path = os.path.join(project_path, "..", ".venv", "Scripts", "python.exe")
    # print(venv_path)
    # print(batch_prg)
    subprocess.run([venv_path, batch_prg])
