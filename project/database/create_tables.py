from database.database import Base, engine
from database.models import User, AIModels, Dataset, Subscription

__all__ = ['User', 'AIModels', 'Dataset', 'Subscription']

def create_tables():
    """Create all database tables."""
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully!")
    except Exception as e:
        print(f"Error creating database tables: {e}")

if __name__ == "__main__":
    create_tables() 