from resend import Resend
from app.core.config import settings
import os
from dotenv import load_dotenv
import logging

load_dotenv()

# Setup logging
logger = logging.getLogger(__name__)

# Initialize Resend with the API key from settings, gracefully handle missing key
if settings.RESEND_API_KEY:
    resend = Resend(api_key=settings.RESEND_API_KEY)
    logger.info("Resend API client initialized successfully")
else:
    resend = None
    logger.warning("Resend API key not found. Email functionality will be disabled.")

async def send_email(
    email_to: str,
    subject: str,
    body: str,
    html: str = None
) -> None:
    """
    Send an email using Resend.
    
    Args:
        email_to: Recipient email address
        subject: Email subject
        body: Plain text email body
        html: HTML email body (optional)
    """
    if not resend:
        logger.warning(f"Email not sent (Resend API key missing): {subject} to {email_to}")
        return
        
    try:
        params = {
            "from": settings.MAIL_FROM or "onboarding@resend.dev",
            "to": email_to,
            "subject": subject,
            "text": body
        }
        
        if html:
            params["html"] = html
            
        r = resend.emails.send(params)
        logger.info(f"Email sent: {subject} to {email_to}")
        return r
    except Exception as e:
        # Log the error but don't raise it to prevent API failures
        logger.error(f"Failed to send email: {str(e)}")
        # Don't raise the exception to prevent API failures
        return None

async def send_ticket_created_notification(email_to: str, ticket_title: str):
    subject = "Support Request Received"
    body = f"We have received your support request: {ticket_title}. We will review your request and get back to you soon."
    html = f"""
    <html>
        <body>
            <h2>Your support request has been received</h2>
            <p>We have received your support request: <strong>{ticket_title}</strong></p>
            <p>We will review your request and get back to you soon.</p>
        </body>
    </html>
    """
    return await send_email(email_to, subject, body, html)

async def send_ticket_response_notification(email_to: str, ticket_title: str, response: str):
    subject = "Response to Your Support Request"
    body = f"Your request: {ticket_title}\nResponse: {response}"
    html = f"""
    <html>
        <body>
            <h2>Response to your support request</h2>
            <p>Your request: <strong>{ticket_title}</strong></p>
            <p>Response: {response}</p>
        </body>
    </html>
    """
    return await send_email(email_to, subject, body, html) 