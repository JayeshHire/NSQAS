import sqlite3
import os
from tabulate import tabulate

def view_database():
    # Connect to the database
    db_path = "C:/Users/jayes/source/final-year-project/streamlit-pro/project/project.db"
    print(f"Looking for database at: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"Database file not found at {db_path}")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    table_name = "datasets"
    print(f"\n=== Table: {table_name} ===")
    
    # Get table schema
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    print("\nSchema:")
    schema_headers = ["Column", "Type", "Nullable", "PK"]
    schema_data = [[col[1], col[2], "Yes" if col[3] == 0 else "No", "Yes" if col[5] == 1 else "No"] for col in columns]
    print(tabulate(schema_data, headers=schema_headers, tablefmt="grid"))
    
    # Get table data and calculate accuracy
    cursor.execute(f"SELECT id, name, contamination, CASE WHEN contamination IS NOT NULL THEN (1 - contamination) * 100 END as accuracy FROM {table_name}")
    rows = cursor.fetchall()
    if rows:
        print(f"\nData ({len(rows)} rows):")
        headers = ["id", "name", "contamination", "accuracy (%)"]
        print(tabulate(rows, headers=headers, tablefmt="grid", floatfmt=".2f"))
    else:
        print("\nNo data in table")

    conn.close()

if __name__ == "__main__":
    view_database() 