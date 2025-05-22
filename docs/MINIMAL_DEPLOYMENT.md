# Minimal Viable Helpdesk: Quick Start Guide

This guide outlines the minimal setup required to get a basic helpdesk system up and running. We'll focus on core functionality first, then expand based on needs.

## Core Features (MVP)

1. **User Features**
   - Simple email-based login
   - Submit support requests
   - View own request history
   - Receive email notifications

2. **Admin Features**
   - View all support requests
   - Respond to requests
   - Mark requests as resolved
   - Basic request filtering

## Minimal Tech Stack

### Backend
- **FastAPI** - Core API framework
- **SQLite** - Simple file-based database (upgrade to PostgreSQL later)
- **FastAPI Users** - Basic email authentication
- **Python-dotenv** - Environment configuration
- **FastAPI-Mail** - Simple email sending
- **Resend** - Email service provider (free tier available)

### Frontend
- **React** - Core UI framework
- **Material UI** - Basic UI components
- **React Router** - Page navigation
- **Axios** - API communication

### Deployment
- **Docker** - Containerization
- **Docker Compose** - Local development
- **Railway** - Simple cloud deployment

## Project Structure (Minimal)

```
helpdesk-minimal/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py      # Email authentication
│   │   │   └── tickets.py   # Ticket endpoints
│   │   ├── models/
│   │   │   └── ticket.py    # Ticket model
│   │   └── main.py          # FastAPI app
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Login.jsx    # Login form
│   │   │   └── TicketForm.jsx # Request submission
│   │   ├── pages/
│   │   │   ├── UserDashboard.jsx
│   │   │   └── AdminDashboard.jsx
│   │   └── App.jsx
│   └── Dockerfile
└── docker-compose.yml
```

## Quick Start Steps

1. **Backend Setup**
```bash
# Create backend structure
mkdir -p backend/app/{api,models}
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install minimal dependencies
pip install fastapi uvicorn[standard] fastapi-users[sqlalchemy] python-dotenv sqlalchemy fastapi-mail resend

# Create requirements.txt
pip freeze > requirements.txt
```

2. **Frontend Setup**
```bash
# Create React app
npx create-react-app frontend
cd frontend

# Install minimal dependencies
npm install @mui/material @emotion/react @emotion/styled axios react-router-dom
```

3. **Basic Backend Implementation**

`backend/app/models/ticket.py`:
```python
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Ticket(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str
    status: str = "open"
    created_by: str  # email
    created_at: datetime = Field(default_factory=datetime.utcnow)
    response: Optional[str] = None
```

`backend/app/core/email.py`:
```python
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from typing import List
import os

conf = ConnectionConfig(
    MAIL_USERNAME = os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD"),
    MAIL_FROM = os.getenv("MAIL_FROM"),
    MAIL_PORT = 587,
    MAIL_SERVER = "smtp.resend.com",
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True
)

async def send_email(
    email_to: str,
    subject: str,
    body: str
):
    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        body=body,
        subtype="html"
    )
    
    fm = FastMail(conf)
    await fm.send_message(message)
```

`backend/app/api/tickets.py`:
```python
from fastapi import APIRouter, Depends, BackgroundTasks
from app.models.ticket import Ticket
from app.core.email import send_email
from typing import List

router = APIRouter()

@router.post("/tickets/", response_model=Ticket)
async def create_ticket(ticket: Ticket, background_tasks: BackgroundTasks):
    # Save ticket to database
    # ... implementation ...
    
    # Send notification email
    background_tasks.add_task(
        send_email,
        email_to=ticket.created_by,
        subject="Support Request Received",
        body=f"Your support request '{ticket.title}' has been received."
    )
    
    return ticket

@router.post("/tickets/{ticket_id}/respond")
async def respond_to_ticket(
    ticket_id: int,
    response: str,
    background_tasks: BackgroundTasks
):
    # Update ticket with response
    # ... implementation ...
    
    # Send response notification
    background_tasks.add_task(
        send_email,
        email_to=ticket.created_by,
        subject="Response to Your Support Request",
        body=f"Response to your request: {response}"
    )
    
    return {"status": "success"}
```

4. **Basic Frontend Implementation**

`frontend/src/pages/UserDashboard.jsx`:
```jsx
import React from 'react';
import { Container, Typography, Button } from '@mui/material';

export default function UserDashboard() {
  return (
    <Container>
      <Typography variant="h4">My Support Requests</Typography>
      <Button variant="contained" color="primary">
        New Request
      </Button>
      {/* Basic ticket list implementation */}
    </Container>
  );
}
```

5. **Docker Setup**

`docker-compose.yml`:
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./helpdesk.db
    volumes:
      - ./backend:/app

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
    depends_on:
      - backend
```

## Environment Variables

Add these to your `.env` file:
```env
MAIL_USERNAME=your_resend_username
MAIL_PASSWORD=your_resend_api_key
MAIL_FROM=support@yourdomain.com
```

## Next Steps After MVP

1. **Authentication Enhancement**
   - Add password reset
   - Implement email verification
   - Add session management
   - **Implement Social Login**
     - Google OAuth2 integration
     - X.com (Twitter) OAuth2 integration
     - Facebook OAuth2 integration
     - Passkey support for passwordless login
     - Combined authentication strategies

2. **Social Login Implementation Details**
   ```python
   # backend/app/core/auth.py
   from fastapi_users.authentication import OAuth2PasswordBearer
   from fastapi_users.integrations.google import GoogleOAuth2
   from fastapi_users.integrations.twitter import TwitterOAuth2
   from fastapi_users.integrations.facebook import FacebookOAuth2

   # OAuth2 configuration
   oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

   # Google OAuth2
   google_oauth_client = GoogleOAuth2(
       client_id=os.getenv("GOOGLE_CLIENT_ID"),
       client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
       redirect_uri=os.getenv("GOOGLE_REDIRECT_URI")
   )

   # X.com (Twitter) OAuth2
   twitter_oauth_client = TwitterOAuth2(
       client_id=os.getenv("TWITTER_CLIENT_ID"),
       client_secret=os.getenv("TWITTER_CLIENT_SECRET"),
       redirect_uri=os.getenv("TWITTER_REDIRECT_URI")
   )

   # Facebook OAuth2
   facebook_oauth_client = FacebookOAuth2(
       client_id=os.getenv("FACEBOOK_CLIENT_ID"),
       client_secret=os.getenv("FACEBOOK_CLIENT_SECRET"),
       redirect_uri=os.getenv("FACEBOOK_REDIRECT_URI")
   )
   ```

   Required environment variables:
   ```env
   # Google OAuth2
   GOOGLE_CLIENT_ID=your_google_client_id
   GOOGLE_CLIENT_SECRET=your_google_client_secret
   GOOGLE_REDIRECT_URI=http://localhost:3000/auth/google/callback

   # X.com (Twitter) OAuth2
   TWITTER_CLIENT_ID=your_twitter_client_id
   TWITTER_CLIENT_SECRET=your_twitter_client_secret
   TWITTER_REDIRECT_URI=http://localhost:3000/auth/twitter/callback

   # Facebook OAuth2
   FACEBOOK_CLIENT_ID=your_facebook_client_id
   FACEBOOK_CLIENT_SECRET=your_facebook_client_secret
   FACEBOOK_REDIRECT_URI=http://localhost:3000/auth/facebook/callback
   ```

   Frontend implementation:
   ```jsx
   // frontend/src/components/SocialLogin.jsx
   import React from 'react';
   import { Button, Stack } from '@mui/material';
   import GoogleIcon from '@mui/icons-material/Google';
   import TwitterIcon from '@mui/icons-material/Twitter';
   import FacebookIcon from '@mui/icons-material/Facebook';

   export default function SocialLogin() {
     const handleGoogleLogin = () => {
       window.location.href = '/api/auth/google/login';
     };

     const handleTwitterLogin = () => {
       window.location.href = '/api/auth/twitter/login';
     };

     const handleFacebookLogin = () => {
       window.location.href = '/api/auth/facebook/login';
     };

     return (
       <Stack spacing={2}>
         <Button
           variant="outlined"
           startIcon={<GoogleIcon />}
           onClick={handleGoogleLogin}
         >
           Continue with Google
         </Button>
         <Button
           variant="outlined"
           startIcon={<TwitterIcon />}
           onClick={handleTwitterLogin}
         >
           Continue with X.com
         </Button>
         <Button
           variant="outlined"
           startIcon={<FacebookIcon />}
           onClick={handleFacebookLogin}
         >
           Continue with Facebook
         </Button>
       </Stack>
     );
   }
   ```

3. **Passkey Support**
   - Implement WebAuthn for passwordless authentication
   - Support for biometric authentication
   - Cross-device authentication
   - Fallback to traditional methods

4. **Authentication Flow**
   - Combined authentication strategies
   - Seamless switching between methods
   - Account linking
   - Profile management

3. **Ticket Management**
   - Add ticket categories
   - Implement ticket status workflow
   - Add file attachments

4. **Admin Features**
   - Add user management
   - Implement ticket assignment
   - Add reporting dashboard

5. **Infrastructure**
   - Migrate to PostgreSQL
   - Add Redis for caching
   - Implement background jobs

## API Testing

To ensure API endpoints are functioning correctly, we've implemented a comprehensive testing strategy with dedicated scripts.

### Testing Scripts

1. **API Test Suite** (`backend/scripts/tests/api_test.py`)
   - Comprehensive endpoint testing
   - Authentication flow validation
   - User management functionality
   - Ticket creation and management
   - Detailed output with pass/fail status

2. **API Path Analyzer** (`backend/scripts/tests/fix_api_paths.py`)
   - Diagnostic tool for API routing issues
   - Tests endpoints with different prefixes
   - Identifies mis-configured routes
   - Suggests fixes for 404 errors

3. **Test Automation** (`frontend/scripts/run_api_tests.ps1`)
   - One-click testing in production-like environment
   - Docker container orchestration
   - Automatic test execution
   - Error reporting and debugging assistance

### Running API Tests

To test the API endpoints in your development environment:

```powershell
# From project root directory
.\frontend\scripts\run_api_tests.ps1
```

This script will:
1. Start Docker containers in production mode
2. Wait for services to initialize
3. Run the comprehensive API tests
4. Show backend logs if tests fail
5. Offer to run the path analyzer for diagnostics
6. Ask if you want to keep containers running

### Common API Issues

If you encounter 404 errors or other API issues:

1. **Check API Prefixes**: Ensure frontend config uses the correct `/api/v1` prefix
2. **Verify Router Registration**: Check that routers are properly included in main.py
3. **Examine Router Prefixes**: Be aware of double-prefixing when routers have their own prefixes
4. **Authentication Headers**: Validate that bearer tokens are correctly formatted and included

For detailed API testing documentation, refer to `backend/scripts/tests/API_TESTING.md`.

## API Route Configuration

When working with the API endpoints, there are two critical configuration points to ensure proper functionality:

### 1. Backend API Prefix

All API routes in the backend follow the `/api/v1` prefix structure. This is configured in `backend/app/core/config.py`:

```python
# API Settings
API_V1_STR: str = "/api/v1"
```

### 2. Authentication Routes

The authentication endpoints (login, logout, register) are configured in `backend/app/api/auth.py` and registered with:

```python
# Include FastAPI Users routers
router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth",
    tags=["auth"]
)
```

This creates endpoints like:
- `/api/v1/auth/login` - For user login
- `/api/v1/auth/logout` - For user logout
- `/api/v1/auth/register` - For user registration

### 3. Custom Endpoints for Admin Dashboard

To support proper functionality in the admin dashboard, we've added custom endpoints:

```python
# Custom logout endpoint
@router.post("/logout")
async def logout():
    return {"status": "success", "message": "Logged out successfully"}

# Password reset endpoints
@router.post("/auth/forgot-password")
async def forgot_password(
    email: str = Body(..., embed=True), 
    session: AsyncSession = Depends(get_session)
):
    # Implementation...

@router.post("/auth/reset-password")
async def reset_password(
    token: str = Body(..., embed=True), 
    new_password: str = Body(..., embed=True), 
    session: AsyncSession = Depends(get_session)
):
    # Implementation...
```

### 4. Ticket Endpoints

Ticket endpoints use a router prefix to organize all ticket-related endpoints:

```python
router = APIRouter(prefix="/tickets")

@router.post("/")  # Becomes /api/v1/tickets/
@router.get("/")   # Becomes /api/v1/tickets/
@router.get("/{ticket_id}")  # Becomes /api/v1/tickets/{ticket_id}

@router.post("/{ticket_id}/respond")
async def respond_to_ticket(
    ticket_id: int,
    background_tasks: BackgroundTasks,
    response: str = Body(..., embed=True),
    session: AsyncSession = Depends(get_session)
):
    # Implementation using SQLModel select...
    
@router.put("/{ticket_id}/status")
async def update_ticket_status(
    ticket_id: int,
    status: str = Body(..., embed=True),
    session: AsyncSession = Depends(get_session)
):
    # Implementation using SQLModel select...
```

The ticket endpoints now use:
- Proper Body parameters instead of query parameters for better security
- SQLModel select statements instead of raw SQL for better maintainability
- Model instances for proper ORM support

### 5. Frontend API Configuration

The frontend must include the correct API URL with the version prefix. This is configured in `frontend/src/config.ts`:

```typescript
// Application configuration
const config = {
  // API URL - use environment variable or default to localhost
  apiUrl: process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1',
  
  // Other configuration...
};
```

**Important**: Any changes to the API routing structure must be synchronized between backend and frontend to prevent 404 errors.

## Docker Deployment Troubleshooting

When deploying the application with Docker, you may encounter several common issues. Here are solutions to the most frequent problems:

### 1. Environment Variable Handling

**Issue**: Environment variables are not properly loaded in Docker containers.

**Solution**: 
- Use the `env_file` directive in `docker-compose.yml` to load variables from a `.env` file:
  ```yaml
  services:
    backend:
      build: ./backend
      env_file:
        - ./backend/.env
  ```
- For CORS origins that expect an array but are provided as a string, use this pattern in your `config.py`:
  ```python
  @property
  def BACKEND_CORS_ORIGINS(self) -> List[str]:
      """Get list of allowed origins from the string"""
      return self.BACKEND_CORS_ORIGINS_STR.split(",") if self.BACKEND_CORS_ORIGINS_STR else ["http://localhost:3000"]
  ```

### 2. SQLite with Async Support

**Issue**: SQLite requires special configuration for async operations.

**Solution**:
- Use the `aiosqlite` driver: `sqlite+aiosqlite:///./data/helpdesk.db`
- Add proper connection arguments:
  ```python
  engine = create_async_engine(
      DATABASE_URL, 
      connect_args={"check_same_thread": False, "timeout": 15},
      pool_pre_ping=True
  )
  ```
- Install required packages: `aiosqlite` and `greenlet`

### 3. Docker File Permissions

**Issue**: Container may not have write permissions to SQLite database.

**Solution**:
- Create a data directory in the Dockerfile:
  ```dockerfile
  RUN mkdir -p /app/data && chmod 777 /app/data
  ```
- Mount a volume for the data directory:
  ```yaml
  volumes:
    - ./backend:/app
    - ./backend/data:/app/data
  ```

### 4. Handling Missing API Keys

**Issue**: Application crashes when API keys are missing.

**Solution**:
- Add graceful fallbacks for external services:
  ```python
  # Initialize Resend with the API key from settings, gracefully handle missing key
  try:
      if settings.RESEND_API_KEY:
          resend = Resend(api_key=settings.RESEND_API_KEY)
          logger.info("Resend API client initialized successfully")
      else:
          resend = None
          logger.warning("Resend API key not found. Email functionality will be disabled.")
  except Exception as e:
      resend = None
      logger.warning(f"Failed to initialize Resend client: {str(e)}. Email functionality will be disabled.")
  ```
- Check for client availability before use:
  ```python
  async def send_email(email_to, subject, body, html=None):
      if not resend:
          logger.warning(f"Email not sent (Resend API key missing): {subject} to {email_to}")
          return
      # Send email...
  ```
- For the minimal deployment (MVP), email features will gracefully degrade:
  - If API keys are present, emails will be sent normally
  - If API keys are missing, detailed logs will show what would have been sent
  - Application functions normally without interruption
  - Users still get appropriate success messages in the UI

### 5. Library Version Compatibility

**Issue**: Library interfaces change between versions.

**Solution**:
- When using external libraries like FastAPI Users, ensure your implementation matches the version in `requirements.txt`
- For FastAPI Users, check the initialization pattern:
  ```python
  # For newer versions:
  fastapi_users = FastAPIUsers(get_user_db, [auth_backend], User, UserCreate, UserUpdate, UserDB)
  
  # For older versions:
  fastapi_users = FastAPIUsers(get_user_manager, [auth_backend])
  ```

## Development Guidelines

1. **Keep it Simple**
   - Start with basic features
   - Use simple solutions first
   - Avoid premature optimization

2. **Focus on Core Flow**
   - User submits request
   - Admin responds
   - User receives notification

3. **Progressive Enhancement**
   - Build features incrementally
   - Test each addition thoroughly
   - Document changes

## Deployment Checklist

- [ ] Set up development environment
- [ ] Implement basic authentication
- [ ] Create ticket submission flow
- [ ] Build admin dashboard
- [ ] Set up email notifications
- [ ] Verify API endpoint configuration 
  - Check auth routes (`/api/v1/auth/login`, `/api/v1/auth/register`)
  - Check ticket routes (`/api/v1/tickets`)
  - Check user routes (`/api/v1/users`, `/api/v1/users/me`)
- [ ] Deploy to Railway
- [ ] Test core functionality
- [ ] Document known issues

## Notes

- This minimal setup focuses on getting a working system quickly
- Use SQLite initially for simplicity
- Basic email notifications using Resend (free tier available)
- Simple UI without advanced features
- No complex workflows or automations
- Basic security measures only
- Social login and passkey support planned for future releases

Remember: This is a foundation to build upon. Add features and complexity as needed, based on user feedback and requirements.

## Future Enhancements

The following features are planned for future releases:

- Add password reset
  - **Status:** ✅ IMPLEMENTED
  - Password reset flow is now fully working with:
    - Request password reset page at `/forgot-password`
    - Backend endpoints for requesting reset tokens and setting new passwords
    - Email delivery of reset tokens (with development mode token display)
    - Client-side validation of password requirements
    - Security features like consistent responses and minimum password lengths

- **Implement Social Login** 