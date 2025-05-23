import sqlite3
import sys
import os

def check_schema():
    # Path to the database file
    db_path = "/app/data/helpdesk.db"
    
    print(f"Checking schema of database at: {db_path}")
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        return False
        
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("Tables in database:")
        for table in tables:
            print(f"  - {table[0]}")
            
        # Check ticket table schema
        if ('ticket',) in tables:
            print("\nTicket table schema:")
            cursor.execute("PRAGMA table_info(ticket)")
            columns = cursor.fetchall()
            
            for col in columns:
                print(f"  - {col[1]} ({col[2]}) {'PRIMARY KEY' if col[5] else ''}")
                
            # Check for is_public column
            column_names = [col[1] for col in columns]
            if "is_public" in column_names:
                print("\n✅ is_public column exists in ticket table")
            else:
                print("\n❌ is_public column DOES NOT exist in ticket table")
                
                # Try to add the column
                print("\nAttempting to add is_public column...")
                cursor.execute("ALTER TABLE ticket ADD COLUMN is_public BOOLEAN DEFAULT 0 NOT NULL")
                conn.commit()
                print("Column added successfully!")
                
                # Verify the column was added
                cursor.execute("PRAGMA table_info(ticket)")
                columns = cursor.fetchall()
                column_names = [col[1] for col in columns]
                if "is_public" in column_names:
                    print("✅ is_public column added and verified")
                else:
                    print("❌ Failed to add is_public column")
        else:
            print("Ticket table not found!")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = check_schema()
    sys.exit(0 if success else 1) 