import json
import psycopg2
from app.core.security import get_password_hash
from datetime import datetime

def restore_users():
    # Database connection parameters
    db_params = {
        'dbname': 'repport',
        'user': 'repport',
        'password': 'repport',
        'host': 'db',
        'port': '5432'
    }

    try:
        # Connect to the database
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        # First, delete all existing users
        cur.execute("DELETE FROM users")

        # Read the backup data
        with open('all_users.json', 'r') as f:
            users_data = json.load(f)

        # Get current timestamp
        now = datetime.utcnow()

        # Insert each user
        for user_data in users_data:
            temp_password = "ChangeMe123!"
            hashed_password = get_password_hash(temp_password)
            
            cur.execute("""
                INSERT INTO users (email, hashed_password, is_active, is_superuser, is_verified, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                user_data['email'],
                hashed_password,
                user_data['is_active'],
                user_data['is_admin'],
                True,
                now,
                now
            ))

        # Commit the changes
        conn.commit()
        print("Users restored successfully!")
        print("All users can log in with password: ChangeMe123!")

    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    restore_users() 