import streamlit as st
import pandas as pd
import numpy as np
from enum import Enum
import time
import os
from forms import model_upload_form
from database.database import get_db
from database.db_operations import (
    create_ai_model, 
    save_file_data, 
    get_ai_model_by_id, 
    get_all_ai_models, 
    get_user_by_email,
    delete_ai_model,
    update_ai_model
)


@st.dialog("upload model")
def model_upload_handler():    
        with st.form("model_upload_form"):
            st.write("Upload new model")

            model_name = st.text_input("Model Name", key="model_name")
            description = st.text_input("Model Description", key="model_description")
            version = st.text_input("Version", key="model_version") 
            model_file = st.file_uploader(
                "upload model file (joblib or pickle)", 
                accept_multiple_files=False,
                key="model_file",
                type=["joblib", "pkl", "pickle"]
            )
            training_data_set = st.file_uploader(
                "upload training data (CSV or Excel)",
                accept_multiple_files=False,
                key="training_data",
                type=["csv", "xlsx", "xls"]
            )

            target_field = st.text_input("Target Field", key="target_field")

            submitted = st.form_submit_button("Submit")

            if submitted:
                if not all([model_name, description, version, model_file]):
                    st.error("Please fill in all required fields and upload a model file.")
                    return

                # Validate model file extension
                file_extension = os.path.splitext(model_file.name)[1].lower()
                allowed_extensions = ['.joblib', '.pkl', '.pickle']
                
                if file_extension not in allowed_extensions:
                    st.error(f"Invalid file type. Please upload a joblib or pickle file. Allowed extensions: {', '.join(allowed_extensions)}")
                    return

                try:
                    # Get model file data
                    model_data, model_size = save_file_data(model_file)
                    
                    # Process training dataset if provided
                    training_data_metadata = None
                    training_data = None
                    if training_data_set is not None:
                        try:
                            # Read the training data to extract metadata
                            if training_data_set.name.endswith('.csv'):
                                df = pd.read_csv(training_data_set)
                            else:  # Excel file
                                df = pd.read_excel(training_data_set)
                            
                            # Create metadata about the training data
                            training_data_metadata = {
                                'filename': training_data_set.name,
                                'columns': df.columns.tolist(),
                                'rows': len(df),
                                'column_types': {col: str(dtype) for col, dtype in df.dtypes.items()},
                                'missing_values': df.isnull().sum().to_dict()
                            }

                            if target_field not in df.columns:
                                st.error(f"Target field '{target_field}' not found in training data.")
                                return
                            
                            # Reset file pointer for saving
                            training_data_set.seek(0)
                            training_data, training_size = save_file_data(training_data_set)
                        except Exception as e:
                            st.error(f"Error processing training data: {str(e)}")
                            return
                    
                    # Get database session
                    db = next(get_db())

                    # Get current user's ID
                    if not st.user.is_logged_in:
                        st.error("You must be logged in to upload models.")
                        return
                        
                    current_user = get_user_by_email(db, st.user.email)
                    if not current_user:
                        st.error("User not found in database. Please try logging out and back in.")
                        return
                    
                    # Create AI model in database with current user's ID
                    model = create_ai_model(
                        db=db,
                        name=model_name,
                        owner_id=current_user.id,
                        version=version,
                        description=description,
                        model_data=model_data,
                        model_name=model_file.name,
                        model_size=model_size,
                        is_public=False,  # Default to private
                        training_data_set=training_data,
                        training_data_set_metadata=training_data_metadata,
                        target_field=target_field
                    )
                    
                    st.success(f"Model {model_name} (version {version}) uploaded successfully!")
                    if training_data_set:
                        st.success(f"Training dataset {training_data_set.name} uploaded and linked to the model.")
                    st.session_state["model_info"] = (model_name, description, version)
                    st.rerun()
                
                except Exception as e:
                    st.error(f"Error uploading model: {str(e)}")
                finally:
                    if 'db' in locals():
                        db.close()


def model_operation(loc: int):
    try:
        model_id = int(st.session_state["ops"].loc[loc]["Model Id"])  # Ensure model_id is an integer
        operation = st.session_state["ops"].loc[loc]["view"]

        
        def view_model(model_id: int):
            try:
                db = next(get_db())
                # Debug information
                st.write(f"Attempting to fetch model with ID: {model_id}")
                
                model = get_ai_model_by_id(db, model_id)

                if model:
                    st.subheader(f"Model Details: {model.name}")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Basic Information**")
                        st.write(f"- **Name:** {model.name}")
                        st.write(f"- **Version:** {model.version}")
                        st.write(f"- **Description:** {model.description}")
                        st.write(f"- **Upload Date:** {model.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                        st.write(f"- **Last Updated:** {model.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
                        
                    with col2:
                        st.write("**Technical Details**")
                        st.write(f"- **Model File:** {model.model_name}")
                        st.write(f"- **Model Size:** {model.model_size / 1024:.2f} KB")
                        if model.training_data_set_metadata:
                            st.write("**Training Dataset Information**")
                            st.write(f"- **Filename:** {model.training_data_set_metadata.get('filename', 'N/A')}")
                            st.write(f"- **Rows:** {model.training_data_set_metadata.get('rows', 'N/A')}")
                            st.write(f"- **Columns:** {len(model.training_data_set_metadata.get('columns', []))}")
                else:
                    st.error("Model not found!")
            except Exception as e:
                st.error(f"Error viewing model: {str(e)}")
            finally:
                if 'db' in locals():
                    db.close()

        def delete_model(model_id: int):
            try:
                if st.button("Confirm Delete", key=f"delete_{model_id}"):
                    db = next(get_db())
                    if delete_ai_model(db, model_id):
                        st.success("Model deleted successfully!")
                        st.rerun()
                    else:
                        st.error("Model not found or could not be deleted.")
            except Exception as e:
                st.error(f"Error deleting model: {str(e)}")
            finally:
                if 'db' in locals():
                    db.close()

        def reupload_model(model_id: int):
            try:
                db = next(get_db())
                model = get_ai_model_by_id(db, model_id)
                
                if not model:
                    st.error("Model not found!")
                    return
                    
                st.subheader(f"Reupload Model: {model.name}")
                
                with st.form(key=f"reupload_form_{model_id}"):
                    model_file = st.file_uploader(
                        "Upload new model file (joblib or pickle)",
                        accept_multiple_files=False,
                        key=f"reupload_model_file_{model_id}",
                        type=["joblib", "pkl", "pickle"]
                    )
                    
                    training_data_set = st.file_uploader(
                        "Upload new training data (optional)",
                        accept_multiple_files=False,
                        key=f"reupload_training_data_{model_id}",
                        type=["csv", "xlsx", "xls"]
                    )
                    
                    submitted = st.form_submit_button("Update Model")
                    
                    if submitted:
                        if not model_file:
                            st.error("Please upload a model file.")
                            return
                            
                        # Validate model file extension
                        file_extension = os.path.splitext(model_file.name)[1].lower()
                        allowed_extensions = ['.joblib', '.pkl', '.pickle']
                        
                        if file_extension not in allowed_extensions:
                            st.error(f"Invalid file type. Please upload a joblib or pickle file. Allowed extensions: {', '.join(allowed_extensions)}")
                            return
                            
                        try:
                            # Get model file data
                            model_data, model_size = save_file_data(model_file)
                            
                            # Process training dataset if provided
                            training_data = None
                            training_data_metadata = None
                            if training_data_set is not None:
                                try:
                                    # Read the training data to extract metadata
                                    if training_data_set.name.endswith('.csv'):
                                        df = pd.read_csv(training_data_set)
                                    else:  # Excel file
                                        df = pd.read_excel(training_data_set)
                                    
                                    # Create metadata about the training data
                                    training_data_metadata = {
                                        'filename': training_data_set.name,
                                        'columns': df.columns.tolist(),
                                        'rows': len(df),
                                        'column_types': {col: str(dtype) for col, dtype in df.dtypes.items()},
                                        'missing_values': df.isnull().sum().to_dict()
                                    }
                                    
                                    # Reset file pointer for saving
                                    training_data_set.seek(0)
                                    training_data, _ = save_file_data(training_data_set)
                                except Exception as e:
                                    st.error(f"Error processing training data: {str(e)}")
                                    return
                            
                            # Update the model in the database
                            updated_model = update_ai_model(
                                db=db,
                                model_id=model_id,
                                model_data=model_data,
                                model_name=model_file.name,
                                model_size=model_size,
                                training_data_set=training_data,
                                training_data_set_metadata=training_data_metadata,
                                target_field=model.target_field
                            )
                            
                            if updated_model:
                                st.success(f"Model {updated_model.name} updated successfully!")
                                if training_data_set:
                                    st.success(f"Training dataset {training_data_set.name} updated!")
                                st.rerun()
                            else:
                                st.error("Failed to update model.")
                                
                        except Exception as e:
                            st.error(f"Error updating model: {str(e)}")
                            
            except Exception as e:
                st.error(f"Error preparing reupload form: {str(e)}")
            finally:
                if 'db' in locals():
                    db.close()

        if operation == "view":
            view_model(model_id)
        elif operation == "delete":
            delete_model(model_id)
        elif operation == "reupload":
            reupload_model(model_id)

    except Exception as e:
        st.error(f"Error processing operation: {str(e)}")

def your_model():
    st.write("""
    ## Your Uploaded models
    """)

    # Get current user and their models
    try:
        db = next(get_db())
        
        if not st.user.is_logged_in:
            st.error("You must be logged in to view your models.")
            return
            
        current_user = get_user_by_email(db, st.user.email)
        if not current_user:
            st.error("User not found in database. Please try logging out and back in.")
            return
        
        # Get all models for the current user
        models = get_all_ai_models(db)
        user_models = [model for model in models if model.owner_id == current_user.id]
        
        if not user_models:
            st.info("You haven't uploaded any models yet.")
        else:
            # Convert models to DataFrame
            df = pd.DataFrame(
                {
                    "Sr. No.": range(1, len(user_models) + 1),
                    "Model Id": [model.id for model in user_models],
                    "Model Name": [model.name for model in user_models],
                    "Description": [model.description for model in user_models],
                    "Version": [model.version for model in user_models],
                    "Upload Date": [model.created_at.strftime("%Y-%m-%d") for model in user_models],
                    "train_dataset": [model.training_data_set_metadata.get('filename', 'No dataset') if model.training_data_set_metadata else 'No dataset' for model in user_models],
                    "view": [None for _ in user_models],  # Initialize with None
                }
            )

            edited_df = st.data_editor(
                df,
                column_config={
                    "Sr. No.": st.column_config.TextColumn("Sr. No.", disabled=True),
                    "Model Id": st.column_config.TextColumn("Model Id", disabled=True),
                    "Model Name": st.column_config.TextColumn("Model Name", disabled=True),
                    "Description": st.column_config.TextColumn("Description", disabled=True),
                    "Version": st.column_config.TextColumn("Version", disabled=True),
                    "Upload Date": st.column_config.TextColumn("Upload Date", disabled=True),
                    "train_dataset": st.column_config.TextColumn("train_dataset", disabled=True),
                    "view": st.column_config.SelectboxColumn(
                        "operations", 
                        help="View model details",
                        width="medium",
                        options=[None, "view", "delete", "reupload"],
                        default=None,
                        pinned=True
                    ),
                },
                hide_index=True,
            )

            st.session_state["ops"] = edited_df[["view", "Model Id"]]

            row_count = len(edited_df)
            for i in range(row_count):
                model_operation(i)

    except Exception as e:
        st.error(f"Error fetching models: {str(e)}")
    finally:
        if 'db' in locals():
            db.close()

    st.button("Upload a model", key="model_upload", on_click=model_upload_handler)

    
