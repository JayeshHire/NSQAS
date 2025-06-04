from database.models import User, AIModels, Dataset, Subscription
from sqlalchemy import inspect

def inspect_models():
    print("\nDatabase Tables and Columns:")
    
    models = [User, AIModels, Dataset, Subscription]
    
    for model in models:
        print(f"\n{model.__tablename__}:")
        inspector = inspect(model)
        for column in inspector.columns:
            print(f"  - {column.name}: {column.type} (Primary Key: {column.primary_key}, Nullable: {column.nullable})")

if __name__ == "__main__":
    inspect_models() 