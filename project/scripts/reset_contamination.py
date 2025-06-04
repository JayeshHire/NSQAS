import sqlite3
import os

def reset_contamination():
    # Connect to the database
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'project.db')
    print(f"Looking for database at: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"Database file not found at {db_path}")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Reset contamination values to NULL
    cursor.execute("UPDATE datasets SET contamination = NULL")
    conn.commit()
    
    # Verify the update
    cursor.execute("SELECT id, name, contamination FROM datasets")
    rows = cursor.fetchall()
    print(f"\nReset {len(rows)} datasets:")
    for row in rows:
        print(f"Dataset {row[0]} ({row[1]}): contamination = {row[2]}")
    
    conn.close()

if __name__ == "__main__":
    reset_contamination() 