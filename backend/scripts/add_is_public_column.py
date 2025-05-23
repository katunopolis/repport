import os
import sys
import asyncio
import sqlite3
from pathlib import Path

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

async def add_is_public_column():
    # Use the absolute path to the database file in the container
    db_path = "/app/data/helpdesk.db"
    
    print(f"Attempting to add is_public column to ticket table in database: {db_path}")
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the column already exists
        cursor.execute("PRAGMA table_info(ticket)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        if "is_public" not in column_names:
            print("Adding is_public column to ticket table...")
            # Add the is_public column with a default value of FALSE (0)
            cursor.execute("ALTER TABLE ticket ADD COLUMN is_public BOOLEAN DEFAULT 0 NOT NULL")
            conn.commit()
            print("Column added successfully!")
        else:
            print("is_public column already exists. No changes needed.")
        
        # Verify the column exists
        cursor.execute("PRAGMA table_info(ticket)")
        columns = cursor.fetchall()
        print("Current ticket table schema:")
        for column in columns:
            print(f"  {column[1]} ({column[2]})")
        
        conn.close()
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(add_is_public_column()) 