import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_URL = "http://localhost:8000"

def test_password_reset():
    # Step 1: Request password reset
    email = "raul.racotea@gmail.com"  # Replace with a valid email
    response = requests.post(f"{BASE_URL}/auth/forgot-password", json={"email": email})
    print("Forgot Password Response:", response.json())

    # Step 2: Simulate receiving the reset token (in a real scenario, this would come from the email)
    # For testing, we'll assume the token is known or retrieved from the database
    reset_token = "your_reset_token_here"  # Replace with the actual token

    # Step 3: Reset the password
    new_password = "new_password123"
    response = requests.post(f"{BASE_URL}/auth/reset-password", json={"token": reset_token, "new_password": new_password})
    print("Reset Password Response:", response.json())

if __name__ == "__main__":
    test_password_reset() 