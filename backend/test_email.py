import resend
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set API key
resend.api_key = os.getenv("MAIL_PASSWORD")  # Your Resend API key

def test_email():
    try:
        # Send a test email using Resend's default sender
        r = resend.Emails.send({
            "from": "onboarding@resend.dev",  # Using Resend's default sender
            "to": "raul.racotea@gmail.com",   # Your email address
            "subject": "Test Email from Helpdesk",
            "html": "<p>This is a test email from your <strong>Helpdesk application</strong>!</p>"
        })
        
        print("Email sent successfully!")
        print("Email ID:", r.get("id"))
        return True
    except Exception as e:
        print("Error sending email:", str(e))
        return False

if __name__ == "__main__":
    test_email() 