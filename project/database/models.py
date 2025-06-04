from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, LargeBinary, ForeignKey, JSON, Float
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime, UTC
from .database import Base

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"

class AIModels(Base):
    __tablename__ = 'ai_models'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    version = Column(String(50), nullable=False)
    description = Column(Text)
    upload_date = Column(DateTime, default=lambda: datetime.now(UTC))
    is_public = Column(Boolean, default=False)
    model_data = Column(LargeBinary, nullable=False)  # Store the actual file content
    model_name = Column(String(255), nullable=False)  # Original filename
    model_size = Column(Integer)  # Size in bytes
    model_metadata = Column(JSON)  # Store additional model metadata as JSON
    training_data_set = Column(LargeBinary, nullable=False)
    training_data_set_metadata = Column(JSON)  # Store additional training data set metadata as JSON
    target_field = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    def __repr__(self):
        return f"<AIModel(name='{self.name}', version='{self.version}')>"

class Dataset(Base):
    __tablename__ = 'datasets'
    
    id = Column(Integer, primary_key=True, autoincrement=True)  # Maps to "Dataset Id"
    name = Column(String(255), nullable=False)  # Maps to "Dataset name"
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    description = Column(Text)  # Maps to "Description"
    version = Column(String(50), nullable=False)  # Maps to "Version"
    upload_date = Column(DateTime, nullable=False)  # Maps to "Upload Date"
    is_public = Column(Boolean, default=False)  # Maps to "visibility" (private/public)
    file_data = Column(LargeBinary, nullable=False)  # Store the actual file content
    file_name = Column(String(255), nullable=False)  # Original filename
    file_type = Column(String(50))  # File type/extension
    file_size = Column(Integer)  # Size in bytes
    dataset_metadata = Column(JSON)  # Store additional dataset metadata as JSON
    contamination = Column(Float, nullable=True)  # Store the contamination value
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    @hybrid_property
    def accuracy(self):
        """Calculate accuracy as (1 - contamination) * 100."""
        if self.contamination is None:
            return None
        return (1 - self.contamination) * 100

    def __repr__(self):
        return f"<Dataset(name='{self.name}', version='{self.version}')>"

class Subscription(Base):
    __tablename__ = 'subscriptions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    ai_model_id = Column(Integer, ForeignKey('ai_models.id'), nullable=False)
    dataset_id = Column(Integer, ForeignKey('datasets.id'), nullable=False)
    subscription_date = Column(DateTime, default=lambda: datetime.now(UTC))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    def __repr__(self):
        return f"<Subscription(user_id={self.user_id}, ai_model_id={self.ai_model_id}, dataset_id={self.dataset_id})>"

class NecessityScore(Base):
    __tablename__ = 'necessity_scores'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    model_id = Column(Integer, ForeignKey('ai_models.id'), nullable=False)
    feature_name = Column(String(255), nullable=False)
    score = Column(Float, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    def __repr__(self):
        return f"<NecessityScore(dataset_id={self.training_data_set_id}, feature='{self.feature_name}', score={self.score})>"

class SelectedDataset(Base):
    __tablename__ = 'selected_datasets'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    model_id = Column(Integer, ForeignKey('ai_models.id'), nullable=False)
    model_name = Column(String(255), nullable=False)
    dataset_id = Column(Integer, ForeignKey('datasets.id'), nullable=False)
    dataset_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    def __repr__(self):
        return f"<SelectedDataset(model='{self.model_name}', dataset='{self.dataset_name}')>"