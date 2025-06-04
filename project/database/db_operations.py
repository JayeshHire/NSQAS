from sqlalchemy.orm import Session
from . import models
from datetime import datetime, UTC
from typing import Optional, BinaryIO, List

def create_user(
    db: Session,
    username: str,
    email: str,
    password_hash: str,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    is_admin: bool = False
) -> models.User:
    """Create a new user in the database."""
    db_user = models.User(
        username=username,
        email=email,
        password_hash=password_hash,
        first_name=first_name,
        last_name=last_name,
        is_admin=is_admin,
        last_login=datetime.now(UTC)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_ai_model(
    db: Session,
    name: str,
    owner_id: int,
    version: str,
    description: str,
    model_data: bytes,
    model_name: str,
    model_size: int,
    is_public: bool = False,
    training_data_set: Optional[bytes] = None,
    training_data_set_metadata: Optional[dict] = None,
    target_field: Optional[str] = None
) -> models.AIModels:
    """Create a new AI model in the database."""
    db_model = models.AIModels(
        name=name,
        owner_id=owner_id,
        version=version,
        description=description,
        model_data=model_data,
        model_name=model_name,
        model_size=model_size,
        is_public=is_public,
        upload_date=datetime.now(UTC),
        training_data_set=training_data_set,
        training_data_set_metadata=training_data_set_metadata,
        target_field=target_field
    )
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model

def create_dataset(
    db: Session,
    name: str,
    owner_id: int,
    version: str,
    description: str,
    file_data: bytes,
    file_name: str,
    file_type: Optional[str],
    file_size: int,
    is_public: bool = False,
    dataset_metadata: Optional[dict] = None
) -> models.Dataset:
    """Create a new dataset in the database."""
    db_dataset = models.Dataset(
        name=name,
        owner_id=owner_id,
        version=version,
        description=description,
        file_data=file_data,
        file_name=file_name,
        file_type=file_type,
        file_size=file_size,
        is_public=is_public,
        upload_date=datetime.now(UTC),
        dataset_metadata=dataset_metadata
    )
    db.add(db_dataset)
    db.commit()
    db.refresh(db_dataset)
    return db_dataset

def create_subscription(
    db: Session,
    user_id: int,
    ai_model_id: int,
    dataset_id: int
) -> models.Subscription:
    """Create a new subscription in the database."""
    db_subscription = models.Subscription(
        user_id=user_id,
        ai_model_id=ai_model_id,
        dataset_id=dataset_id,
        subscription_date=datetime.now(UTC),
        is_active=True
    )
    db.add(db_subscription)
    db.commit()
    db.refresh(db_subscription)
    return db_subscription

def save_file_data(file: BinaryIO) -> tuple[bytes, int]:
    """Helper function to read file data and get size."""
    file_data = file.read()
    file_size = len(file_data)
    return file_data, file_size

# Get functions for each table
def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    """Get all users with pagination."""
    return db.query(models.User).offset(skip).limit(limit).all()

def get_user_by_id(db: Session, user_id: int) -> Optional[models.User]:
    """Get a specific user by ID."""
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Get a specific user by email."""
    return db.query(models.User).filter(models.User.email == email).first()

def get_all_ai_models(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    owner_id: Optional[int] = None,
    is_public: Optional[bool] = None
) -> List[models.AIModels]:
    """Get all AI models with optional filtering."""
    query = db.query(models.AIModels)
    if owner_id is not None:
        query = query.filter(models.AIModels.owner_id == owner_id)
    if is_public is not None:
        query = query.filter(models.AIModels.is_public == is_public)
    return query.offset(skip).limit(limit).all()

def get_ai_model_by_id(db: Session, model_id: int) -> Optional[models.AIModels]:
    """Get a specific AI model by ID."""
    try:
        
        # Explicitly specify the table and column for the ID comparison
        query = db.query(models.AIModels).filter(models.AIModels.id == int(model_id))
        # Execute query with explicit join if needed
        model = query.first()
        
        if model is None:
            # Try to debug why no model was found
            # Check if any models exist with similar IDs
            nearby_models = db.query(models.AIModels).all()
            
        return model
    except Exception as e:
        print(f"Error in get_ai_model_by_id: {str(e)}")
        db.rollback()  # Rollback any failed transaction
        raise

def get_all_datasets(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    owner_id: Optional[int] = None,
    is_public: Optional[bool] = None
) -> List[models.Dataset]:
    """Get all datasets with optional filtering."""
    query = db.query(models.Dataset)
    if owner_id is not None:
        query = query.filter(models.Dataset.owner_id == owner_id)
    if is_public is not None:
        query = query.filter(models.Dataset.is_public == is_public)
    return query.offset(skip).limit(limit).all()

def get_dataset_by_id(db: Session, dataset_id: int) -> Optional[models.Dataset]:
    """Get a specific dataset by ID."""
    return db.query(models.Dataset).filter(models.Dataset.id == dataset_id).first()

def get_all_subscriptions(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    user_id: Optional[int] = None,
    is_active: Optional[bool] = None
) -> List[models.Subscription]:
    """Get all subscriptions with optional filtering."""
    query = db.query(models.Subscription)
    if user_id is not None:
        query = query.filter(models.Subscription.user_id == user_id)
    if is_active is not None:
        query = query.filter(models.Subscription.is_active == is_active)
    return query.offset(skip).limit(limit).all()

def get_user_subscriptions(
    db: Session,
    user_id: int,
    is_active: Optional[bool] = None
) -> List[models.Subscription]:
    """Get all subscriptions for a specific user."""
    query = db.query(models.Subscription).filter(models.Subscription.user_id == user_id)
    if is_active is not None:
        query = query.filter(models.Subscription.is_active == is_active)
    return query.all()

def get_model_subscriptions(
    db: Session,
    model_id: int,
    is_active: Optional[bool] = None
) -> List[models.Subscription]:
    """Get all subscriptions for a specific AI model."""
    query = db.query(models.Subscription).filter(models.Subscription.ai_model_id == model_id)
    if is_active is not None:
        query = query.filter(models.Subscription.is_active == is_active)
    return query.all()

def get_user_datasets(db: Session, owner_id: int) -> List[models.Dataset]:
    """Get all datasets for a specific user."""
    return db.query(models.Dataset).filter(models.Dataset.owner_id == owner_id).all()

def update_dataset_visibility(db: Session, dataset_id: int, is_public: bool) -> Optional[models.Dataset]:
    """Update the visibility (public/private) status of a dataset."""
    try:
        # Start a new transaction
        db.begin_nested()  # Creates a savepoint
        
        # Lock the row for update
        dataset = (
            db.query(models.Dataset)
            .filter(models.Dataset.id == dataset_id)
            .with_for_update()  # This locks the row
            .first()
        )
        
        
        if dataset:
            dataset.is_public = is_public
            # Commit the nested transaction
            db.commit()
            # Refresh to get the latest state
            db.refresh(dataset)
            return dataset
        else:
            # Rollback the nested transaction if dataset not found
            db.rollback()
            return None
            
    except Exception as e:
        # Rollback on any error
        db.rollback()
        print(f"Error updating dataset {dataset_id}: {str(e)}")
        raise 

def delete_ai_model(db: Session, model_id: int) -> bool:
    """Delete an AI model from the database."""
    try:
        db.begin_nested()  # Creates a savepoint
        model = db.query(models.AIModels).filter(models.AIModels.id == model_id).first()
        if model:
            db.delete(model)
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        print(f"Error deleting model {model_id}: {str(e)}")
        raise

def update_ai_model(
    db: Session,
    model_id: int,
    model_data: bytes,
    model_name: str,
    model_size: int,
    training_data_set: Optional[bytes] = None,
    training_data_set_metadata: Optional[dict] = None,
    target_field: Optional[str] = None
) -> Optional[models.AIModels]:
    """Update an existing AI model in the database."""
    try:
        db.begin_nested()  # Creates a savepoint
        model = db.query(models.AIModels).filter(models.AIModels.id == model_id).with_for_update().first()
        if model:
            model.model_data = model_data
            model.model_name = model_name
            model.model_size = model_size
            model.target_field = target_field
            if training_data_set is not None:
                model.training_data_set = training_data_set
            if training_data_set_metadata is not None:
                model.training_data_set_metadata = training_data_set_metadata
            model.updated_at = datetime.now(UTC)
            db.commit()
            db.refresh(model)
            return model
        return None
    except Exception as e:
        db.rollback()
        print(f"Error updating model {model_id}: {str(e)}")
        raise 

def delete_dataset(db: Session, dataset_id: int) -> bool:
    """Delete a dataset from the database."""
    try:
        db.begin_nested()  # Creates a savepoint
        dataset = db.query(models.Dataset).filter(models.Dataset.id == dataset_id).first()
        if dataset:
            db.delete(dataset)
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        print(f"Error deleting dataset {dataset_id}: {str(e)}")
        raise

def update_dataset(
    db: Session,
    dataset_id: int,
    file_data: bytes,
    file_name: str,
    file_type: str,
    file_size: int,
    dataset_metadata: Optional[dict] = None,
    target_field: Optional[str] = None
) -> Optional[models.Dataset]:
    """Update an existing dataset in the database."""
    try:
        db.begin_nested()  # Creates a savepoint
        dataset = db.query(models.Dataset).filter(models.Dataset.id == dataset_id).with_for_update().first()
        if dataset:
            dataset.file_data = file_data
            dataset.file_name = file_name
            dataset.file_type = file_type
            dataset.file_size = file_size
            if dataset_metadata is not None:
                dataset.dataset_metadata = dataset_metadata
            dataset.updated_at = datetime.now(UTC)
            db.commit()
            db.refresh(dataset)
            return dataset
        return None
    except Exception as e:
        db.rollback()
        print(f"Error updating dataset {dataset_id}: {str(e)}")
        raise 

def get_necessity_scores(
    db: Session,
    owner_id: int,
    model_id: int
) -> List[models.NecessityScore]:
    """Get all necessity scores for a specific owner and model."""
    return db.query(models.NecessityScore).filter(
        models.NecessityScore.owner_id == owner_id,
        models.NecessityScore.model_id == model_id
    ).all() 

def create_necessity_score(
    db: Session,
    owner_id: int,
    model_id: int,
    feature_name: str,
    score: float
) -> models.NecessityScore:
    """Create a new necessity score in the database."""
    db_score = models.NecessityScore(
        owner_id=owner_id,
        model_id=model_id,
        feature_name=feature_name,
        score=score
    )
    db.add(db_score)
    db.commit()
    db.refresh(db_score)
    return db_score 

def create_selected_dataset(
    db: Session,
    model_id: int,
    model_name: str,
    dataset_id: int,
    dataset_name: str
) -> models.SelectedDataset:
    """Create a new selected dataset entry."""
    db_selected = models.SelectedDataset(
        model_id=model_id,
        model_name=model_name,
        dataset_id=dataset_id,
        dataset_name=dataset_name
    )
    db.add(db_selected)
    db.commit()
    db.refresh(db_selected)
    return db_selected

def get_selected_datasets(
    db: Session,
    model_id: Optional[int] = None
) -> List[models.SelectedDataset]:
    """Get all selected datasets, optionally filtered by model_id."""
    query = db.query(models.SelectedDataset)
    if model_id:
        query = query.filter(models.SelectedDataset.model_id == model_id)
    return query.all()

def update_selected_dataset(
    db: Session,
    selected_id: int,
    model_name: Optional[str] = None,
    dataset_name: Optional[str] = None
) -> Optional[models.SelectedDataset]:
    """Update an existing selected dataset entry."""
    try:
        db.begin_nested()
        selected = db.query(models.SelectedDataset).filter(
            models.SelectedDataset.id == selected_id
        ).with_for_update().first()
        
        if selected:
            if model_name:
                selected.model_name = model_name
            if dataset_name:
                selected.dataset_name = dataset_name
            selected.updated_at = datetime.now(UTC)
            db.commit()
            db.refresh(selected)
            return selected
        return None
    except Exception as e:
        db.rollback()
        print(f"Error updating selected dataset {selected_id}: {str(e)}")
        raise

def delete_selected_dataset(db: Session, selected_id: int) -> bool:
    """Delete a selected dataset entry."""
    try:
        db.begin_nested()
        selected = db.query(models.SelectedDataset).filter(
            models.SelectedDataset.id == selected_id
        ).first()
        if selected:
            db.delete(selected)
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        print(f"Error deleting selected dataset {selected_id}: {str(e)}")
        raise 