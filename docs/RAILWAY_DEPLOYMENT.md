# Railway Deployment Guide for Repport

This document outlines the comprehensive plan for migrating the Repport application from a development environment to a production-ready deployment on Railway, including upgrading from SQLite to PostgreSQL and implementing HTTPS.

## Table of Contents

1. [Migration Overview](#migration-overview)
2. [PostgreSQL Migration](#postgresql-migration)
3. [HTTPS Implementation](#https-implementation)
4. [Railway Setup](#railway-setup)
5. [Deployment Process](#deployment-process)
6. [Post-Deployment Verification](#post-deployment-verification)
7. [Monitoring and Maintenance](#monitoring-and-maintenance)
8. [Email Service Implementation](#email-service-implementation)

## Migration Overview

The migration process will include the following high-level steps:

1. Setting up PostgreSQL database
2. Adapting the application for PostgreSQL
3. Implementing HTTPS security
4. Configuring Railway services
5. Deploying the application
6. Setting up monitoring and logging

## PostgreSQL Migration

### 1. Update Database Configuration

Update `app/core/config.py` to handle PostgreSQL connection strings:

```python
# app/core/config.py
from pydantic import BaseSettings, Field, PostgresDsn, validator
from typing import Optional, Dict, Any, List, Union

class Settings(BaseSettings):
    PROJECT_NAME: str = "Repport Helpdesk"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    BACKEND_CORS_ORIGINS: List[str] = ["https://repport-app.up.railway.app"]
    
    # Database settings
    POSTGRES_SERVER: str = Field(..., env="POSTGRES_SERVER")
    POSTGRES_USER: str = Field(..., env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(..., env="POSTGRES_PASSWORD")
    POSTGRES_DB: str = Field(..., env="POSTGRES_DB")
    DATABASE_URI: Optional[PostgresDsn] = None
    
    @validator("DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

### 2. Update Database Engine Configuration

Modify `app/core/database.py` to include best practices for PostgreSQL:

```python
# app/core/database.py
from sqlmodel import create_engine, SQLModel, Session
from app.core.config import settings
import time
from sqlalchemy.exc import OperationalError

# Configure PostgreSQL engine with appropriate connection settings
engine = create_engine(
    str(settings.DATABASE_URI),
    pool_pre_ping=True,  # Verify connections before using them
    pool_recycle=300,    # Recycle connections after 5 minutes
    pool_size=10,        # Connection pool size
    max_overflow=20,     # Allow up to 20 overflows
    echo=False           # Set to True for SQL query logging
)

# Connection retry logic for startup
async def init_db(max_retries=5, retry_delay=5):
    """Initialize database with retry logic"""
    for attempt in range(max_retries):
        try:
            # Create DB tables
            SQLModel.metadata.create_all(engine)
            print(f"Database initialized successfully on attempt {attempt + 1}")
            return
        except OperationalError as e:
            if attempt < max_retries - 1:
                print(f"Database connection failed: {e}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                raise Exception(f"Failed to connect to database after {max_retries} attempts") from e

def get_session():
    """Get database session"""
    with Session(engine) as session:
        yield session
```

### 3. Update Requirements

Add PostgreSQL dependencies to `requirements.txt`:

```
fastapi>=0.95.0
uvicorn[standard]>=0.21.1
sqlmodel>=0.0.8
pydantic>=1.10.7
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
psycopg2-binary>=2.9.6  # PostgreSQL driver
alembic>=1.10.3        # Database migrations
python-dotenv>=1.0.0
```

### 4. Database Migration Setup

Create migration scripts using Alembic:

```bash
# Install Alembic
pip install alembic

# Initialize Alembic
alembic init migrations

# Configure alembic.ini to use your PostgreSQL connection
# Update migrations/env.py to work with SQLModel
```

Example update for `migrations/env.py`:

```python
# ...
from app.core.config import settings
from app.models import *  # Import all models
from sqlmodel import SQLModel

# ...
config.set_main_option("sqlalchemy.url", str(settings.DATABASE_URI))
target_metadata = SQLModel.metadata
# ...
```

### 5. Testing PostgreSQL Locally

Use Docker to test with PostgreSQL before deploying:

```yaml
# docker-compose.yml
services:
  db:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=repport
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
    environment:
      - POSTGRES_SERVER=db
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=repport
      - SECRET_KEY=your-secret-key-here
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
    volumes:
      - ./frontend:/app:ro
      - /app/node_modules
    environment:
      - REACT_APP_API_URL=http://localhost:8000

volumes:
  postgres_data:
```

### 6. Data Migration Script

Create a script to migrate existing data from SQLite to PostgreSQL:

```python
# backend/scripts/migrate_to_postgres.py
import sqlite3
import psycopg2
from psycopg2.extras import execute_values
import os
from dotenv import load_dotenv

load_dotenv()

# SQLite connection
sqlite_conn = sqlite3.connect("./data/repport.db")
sqlite_cursor = sqlite_conn.cursor()

# PostgreSQL connection
pg_conn = psycopg2.connect(
    host=os.getenv("POSTGRES_SERVER"),
    database=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD")
)
pg_cursor = pg_conn.cursor()

# Migrate users
sqlite_cursor.execute("SELECT id, email, hashed_password, is_active, is_superuser, created_at FROM user")
users = sqlite_cursor.fetchall()

execute_values(
    pg_cursor,
    "INSERT INTO user (id, email, hashed_password, is_active, is_superuser, created_at) VALUES %s",
    users
)

# Migrate tickets
sqlite_cursor.execute("SELECT id, title, description, status, is_public, created_at, created_by FROM ticket")
tickets = sqlite_cursor.fetchall()

execute_values(
    pg_cursor,
    "INSERT INTO ticket (id, title, description, status, is_public, created_at, created_by) VALUES %s",
    tickets
)

# Migrate ticket responses
sqlite_cursor.execute("SELECT id, ticket_id, response, responded_at, responded_by FROM ticket_response")
responses = sqlite_cursor.fetchall()

execute_values(
    pg_cursor,
    "INSERT INTO ticket_response (id, ticket_id, response, responded_at, responded_by) VALUES %s",
    responses
)

# Commit and close connections
pg_conn.commit()
pg_cursor.close()
pg_conn.close()
sqlite_cursor.close()
sqlite_conn.close()

print("Migration completed successfully")
```

## HTTPS Implementation

### 1. Update Frontend Configuration

Modify the frontend API client to always use HTTPS in production:

```typescript
// src/config.ts
const isDevelopment = process.env.NODE_ENV === 'development';

export const config = {
  apiUrl: isDevelopment 
    ? 'http://localhost:8000/api/v1' 
    : 'https://repport-api.up.railway.app/api/v1',
  
  // Add other environment-specific configurations
  useHttps: !isDevelopment,
  appName: 'Repport Helpdesk',
};
```

### 2. Configure Backend CORS for HTTPS

Update CORS settings to work with HTTPS:

```python
# app/core/config.py
BACKEND_CORS_ORIGINS: List[str] = [
    "https://repport-app.up.railway.app",
    "http://localhost:3000",  # Development only
]
```

### 3. Update JWT Cookie Settings

If using cookies for JWT storage, ensure they're secure:

```python
# In your authentication route
@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), response: Response = None):
    # Auth logic...
    
    # Set cookie with secure flag
    if response and settings.USE_SECURE_COOKIES:
        response.set_cookie(
            key="token",
            value=f"Bearer {access_token}",
            httponly=True,
            secure=True,  # Only send over HTTPS
            samesite="lax",
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    return {"access_token": access_token, "token_type": "bearer"}
```

## Railway Setup

Railway provides PostgreSQL as a service and handles HTTPS automatically. Here's how to set up the project:

### 1. Create `railway.json` Configuration

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "echo Building the app!"
  },
  "deploy": {
    "startCommand": "cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### 2. Create `railway.toml` for Multi-Service Configuration

```toml
[build]
builder = "nixpacks"

[[services]]
name = "backend"
dockerfile = "backend/Dockerfile"
[services.build]
command = "echo Building backend!"
[services.deploy]
command = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
healthcheck = "/health"
healthcheck_timeout_seconds = 10
restarts = "on-failure"
port = "$PORT"

[[services]]
name = "frontend"
dockerfile = "frontend/Dockerfile"
[services.build]
command = "echo Building frontend!"
[services.deploy]
restarts = "on-failure"
port = 80
internal_port = 80
```

### 3. Update Dockerfiles for Railway Compatibility

Backend Dockerfile:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Use PORT environment variable provided by Railway
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

Frontend Dockerfile:

```dockerfile
FROM node:18-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
# Set the API URL to our Railway backend
ENV REACT_APP_API_URL=https://repport-api.up.railway.app/api/v1
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### 4. Configure `nginx.conf` for SPA Routing

```nginx
server {
    listen 80;
    
    location / {
        root /usr/share/nginx/html;
        index index.html index.htm;
        try_files $uri $uri/ /index.html;
    }
    
    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico)$ {
        root /usr/share/nginx/html;
        expires 1y;
        add_header Cache-Control "public, max-age=31536000";
    }
    
    # Error handling
    error_page 500 502 503 504 /50x.html;
    location = /50x.html {
        root /usr/share/nginx/html;
    }
}
```

## Deployment Process

### 1. Initial Railway Setup

1. Create a Railway account at https://railway.app/
2. Install Railway CLI:
   ```bash
   npm i -g @railway/cli
   ```
3. Login to Railway:
   ```bash
   railway login
   ```
4. Initialize Railway project:
   ```bash
   railway init
   ```

### 2. Set Up PostgreSQL on Railway

1. Add a PostgreSQL database to your project:
   ```bash
   railway add
   ```
   Select "PostgreSQL" from the list of available plugins.

2. Get connection info:
   ```bash
   railway connect
   ```

3. Set the database connection variables as environment variables in Railway:
   ```bash
   railway variables set \
     POSTGRES_SERVER="$PGHOST" \
     POSTGRES_USER="$PGUSER" \
     POSTGRES_PASSWORD="$PGPASSWORD" \
     POSTGRES_DB="$PGDATABASE"
   ```

### 3. Set Other Environment Variables

Set all required environment variables for your application:

```bash
railway variables set \
  SECRET_KEY="your-secure-secret-key" \
  ENVIRONMENT="production" \
  BACKEND_CORS_ORIGINS="https://repport-app.up.railway.app"
```

### 4. Deploy Backend and Frontend

Deploy using Railway CLI:

```bash
# Link to your Railway project
railway link

# Deploy project
railway up
```

Alternatively, set up GitHub integration for continuous deployment:

1. Connect your GitHub repository to Railway
2. Configure automatic deployments on push to main branch
3. Set up deployment triggers and webhooks

### 5. Configure Domain Names

1. Setup custom domains in Railway dashboard:
   - `api.yourdomain.com` for backend
   - `app.yourdomain.com` for frontend

2. Update your DNS records to point to Railway's nameservers or use CNAME records:
   ```
   api.yourdomain.com CNAME yourdomain.up.railway.app
   app.yourdomain.com CNAME yourdomain.up.railway.app
   ```

3. Railway will automatically provision SSL certificates via Let's Encrypt

## Post-Deployment Verification

### 1. Check HTTP to HTTPS Redirects

Verify that all HTTP requests are redirected to HTTPS:

```bash
curl -I http://api.yourdomain.com
# Should show a 301 redirect to https://api.yourdomain.com
```

### 2. Test API Endpoints

Run comprehensive tests against the deployed API:

```bash
# Adjust the script path as needed
python backend/scripts/tests/api_test.py https://api.yourdomain.com
```

### 3. Verify Database Connectivity

Create a database check endpoint and test it:

```python
@app.get("/health/db")
async def db_health_check(session: Session = Depends(get_session)):
    try:
        # Execute a simple query
        result = session.exec("SELECT 1").first()
        return {"status": "database connection healthy", "result": result}
    except Exception as e:
        return {"status": "database connection error", "error": str(e)}
```

### 4. Check Frontend-Backend Integration

Test the entire application flow:
1. User registration
2. Login
3. Create tickets
4. Admin responses
5. Public/private ticket toggles

## Monitoring and Maintenance

### 1. Setup Basic Monitoring

Add logging to your FastAPI application:

```python
# app/core/logging.py
import logging
import sys
from typing import List
from pydantic import BaseSettings

class LoggingSettings(BaseSettings):
    LOGGING_LEVEL: str = "INFO"
    LOGGING_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

logging_settings = LoggingSettings()

def setup_logging():
    # Configure root logger
    logging.basicConfig(
        level=logging_settings.LOGGING_LEVEL,
        format=logging_settings.LOGGING_FORMAT,
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    
    # Set levels for specific loggers
    loggers = [
        "uvicorn",
        "uvicorn.access",
        "uvicorn.error",
        "fastapi",
        "sqlalchemy.engine",
    ]
    
    for logger_name in loggers:
        logging.getLogger(logger_name).setLevel(logging.INFO)
    
    # Return root logger
    return logging.getLogger("app")

logger = setup_logging()
```

### 2. Database Backups

Set up regular database backups using Railway CLI or pgdump:

```bash
# Backup script
#!/bin/bash
BACKUP_DIR="/path/to/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/repport_backup_$TIMESTAMP.sql"

# Get database connection details from Railway
eval $(railway variables export)

# Run backup
PGPASSWORD=$PGPASSWORD pg_dump -h $PGHOST -U $PGUSER -d $PGDATABASE > $BACKUP_FILE

# Compress backup
gzip $BACKUP_FILE

echo "Backup completed: ${BACKUP_FILE}.gz"
```

### 3. Continuous Integration

Set up GitHub Actions for CI/CD:

```yaml
# .github/workflows/deploy.yml
name: Deploy to Railway

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Install Railway CLI
      run: npm i -g @railway/cli
    
    - name: Deploy to Railway
      run: railway up
      env:
        RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

### 4. Implement Health Check Monitoring

Add a comprehensive health check endpoint:

```python
@app.get("/health/full")
async def full_health_check(session: Session = Depends(get_session)):
    health = {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }
    
    # Check database
    try:
        result = session.exec("SELECT 1").first()
        health["checks"]["database"] = {"status": "healthy"}
    except Exception as e:
        health["checks"]["database"] = {"status": "unhealthy", "error": str(e)}
        health["status"] = "degraded"
    
    # Check disk space
    try:
        total, used, free = shutil.disk_usage("/")
        percent_used = (used / total) * 100
        health["checks"]["disk"] = {
            "status": "healthy" if percent_used < 90 else "warning",
            "percent_used": percent_used,
            "free_gb": free / (1024**3)
        }
    except Exception as e:
        health["checks"]["disk"] = {"status": "unknown", "error": str(e)}
    
    # Overall status
    if any(check.get("status") == "unhealthy" for check in health["checks"].values()):
        health["status"] = "unhealthy"
        return JSONResponse(content=health, status_code=500)
    
    return health
```

## Email Service Implementation

Implementing a reliable email service is essential for features like user registration confirmation, password resets, and ticket notifications. This chapter outlines how to integrate email functionality into the Repport application.

### 1. Email Service Options

Several options are available for email delivery:

1. **Railway SendGrid Integration** - Easy setup with Railway's marketplace
2. **External SMTP Provider** - Services like SendGrid, Mailgun, or Amazon SES
3. **Self-hosted SMTP Server** - Not recommended for production use due to deliverability challenges

For this guide, we'll use an external SMTP provider approach, which offers better deliverability and is usable with any hosting platform.

### 2. Backend Email Integration

#### Update Configuration

Add email settings to `app/core/config.py`:

```python
# app/core/config.py
class Settings(BaseSettings):
    # Existing settings...
    
    # Email settings
    MAIL_USERNAME: str = Field(..., env="MAIL_USERNAME")
    MAIL_PASSWORD: str = Field(..., env="MAIL_PASSWORD")
    MAIL_FROM: str = Field(..., env="MAIL_FROM")
    MAIL_FROM_NAME: str = Field(default="Repport Support", env="MAIL_FROM_NAME")
    MAIL_SERVER: str = Field(..., env="MAIL_SERVER")
    MAIL_PORT: int = Field(default=587, env="MAIL_PORT")
    MAIL_TLS: bool = Field(default=True, env="MAIL_TLS")
    MAIL_SSL: bool = Field(default=False, env="MAIL_SSL")
    MAIL_USE_CREDENTIALS: bool = Field(default=True, env="MAIL_USE_CREDENTIALS")
    
    # Optional testing settings
    MAIL_TEST_USER: str = Field(default="test@example.com", env="MAIL_TEST_USER")
```

#### Create Email Utility Module

Create `app/core/email.py`:

```python
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
from jinja2 import Environment, select_autoescape, FileSystemLoader

from app.core.config import settings

# Configure FastMail
mail_config = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_TLS=settings.MAIL_TLS,
    MAIL_SSL=settings.MAIL_SSL,
    USE_CREDENTIALS=settings.MAIL_USE_CREDENTIALS,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    TEMPLATE_FOLDER=Path(__file__).parent.parent / "templates" / "email"
)

# Initialize FastMail
fastmail = FastMail(mail_config)

# Initialize template engine
templates_path = Path(__file__).parent.parent / "templates" / "email"
jinja_env = Environment(
    loader=FileSystemLoader(templates_path),
    autoescape=select_autoescape(['html', 'xml'])
)

async def send_email(
    email_to: List[EmailStr],
    subject: str,
    template_name: str,
    background_tasks: Optional[BackgroundTasks] = None,
    **template_data: Any
) -> None:
    """Send an email using a template.
    
    Args:
        email_to: List of recipient email addresses
        subject: Email subject
        template_name: Name of the template file (without extension)
        background_tasks: Optional BackgroundTasks for async sending
        template_data: Data to render in the template
    """
    # Load and render HTML template
    html_template = jinja_env.get_template(f"{template_name}.html")
    html_content = html_template.render(**template_data)
    
    # Load and render text template (fallback)
    try:
        text_template = jinja_env.get_template(f"{template_name}.txt")
        text_content = text_template.render(**template_data)
    except:
        # If no text template exists, use a simple fallback
        text_content = f"Please view this email in an HTML compatible email client.\n\nSubject: {subject}"
    
    # Create message
    message = MessageSchema(
        subject=subject,
        recipients=email_to,
        body=html_content,
        subtype="html",
        alternative_body=text_content
    )
    
    # Send email (in background if background_tasks provided)
    if background_tasks:
        background_tasks.add_task(fastmail.send_message, message)
        logging.info(f"Email queued to {', '.join(email_to)}: {subject}")
    else:
        await fastmail.send_message(message)
        logging.info(f"Email sent to {', '.join(email_to)}: {subject}")
```

#### Create Email Templates

Create template directory structure:

```
backend/
└── app/
    └── templates/
        └── email/
            ├── password_reset.html
            ├── password_reset.txt
            ├── ticket_notification.html
            └── ticket_notification.txt
```

Example HTML template (`password_reset.html`):

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Password Reset</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background-color: #1976d2; color: white; padding: 10px 20px; }
        .content { padding: 20px; border: 1px solid #ddd; }
        .button { display: inline-block; padding: 10px 20px; background-color: #1976d2; color: white; 
                 text-decoration: none; border-radius: 4px; }
        .footer { margin-top: 20px; font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Repport Password Reset</h1>
        </div>
        <div class="content">
            <p>Hello,</p>
            <p>We received a request to reset your password. If you didn't make this request, you can ignore this email.</p>
            <p>To reset your password, click the button below:</p>
            <p><a href="{{ reset_url }}" class="button">Reset Password</a></p>
            <p>Or copy and paste this link into your browser:</p>
            <p>{{ reset_url }}</p>
            <p>This link will expire in 24 hours.</p>
        </div>
        <div class="footer">
            <p>Repport Helpdesk System</p>
            <p>If you need further assistance, please contact support.</p>
        </div>
    </div>
</body>
</html>
```

### 3. Implement Password Reset Flow

Update the authentication endpoints to include email functionality:

```python
# app/api/auth.py

# Add these imports
from fastapi import BackgroundTasks
from app.core.email import send_email
import secrets
from datetime import datetime, timedelta

# Add to router
@router.post("/forgot-password", status_code=200)
async def forgot_password(
    email: EmailStr,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session)
):
    """Request a password reset link"""
    # Find user
    user = session.exec(select(User).where(User.email == email)).first()
    
    # Always return success even if user doesn't exist (security best practice)
    if not user:
        return {"message": "If an account exists with this email, you will receive a password reset link"}
    
    # Generate secure token
    token = secrets.token_urlsafe(32)
    
    # Store token with expiration time (24 hours)
    token_expiry = datetime.utcnow() + timedelta(hours=24)
    
    # Either update existing reset token or create new entry
    # This would require a PasswordReset model in your database
    
    # Generate reset URL for frontend
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    
    # Send email
    await send_email(
        email_to=[email],
        subject="Reset Your Repport Password",
        template_name="password_reset",
        background_tasks=background_tasks,
        reset_url=reset_url,
        user_email=email
    )
    
    return {"message": "If an account exists with this email, you will receive a password reset link"}
```

### 4. Configure Environment Variables

Add the following variables to your Railway project:

```bash
railway variables set \
  MAIL_USERNAME="your-smtp-username" \
  MAIL_PASSWORD="your-smtp-password" \
  MAIL_FROM="noreply@yourdomain.com" \
  MAIL_FROM_NAME="Repport Support" \
  MAIL_SERVER="smtp.yourprovider.com" \
  MAIL_PORT="587" \
  MAIL_TLS="true" \
  MAIL_SSL="false" \
  FRONTEND_URL="https://repport-app.up.railway.app"
```

### 5. Update Dependencies

Add FastAPI Mail to your `requirements.txt`:

```
# Add to existing requirements
fastapi-mail>=1.2.0
jinja2>=3.1.2
```

### 6. Implement Ticket Notifications

Add notification emails for ticket events:

```python
# app/api/tickets.py

# Add imports
from fastapi import BackgroundTasks
from app.core.email import send_email

# Update ticket response endpoint
@router.post("/{ticket_id}/respond", response_model=Ticket)
async def respond_to_ticket(
    ticket_id: int,
    response_data: TicketResponseCreate,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    # Existing logic...
    
    # Get ticket creator email
    creator = session.get(User, ticket.created_by)
    
    # Send notification email
    if creator and creator.email:
        await send_email(
            email_to=[creator.email],
            subject=f"New Response to Your Ticket: {ticket.title}",
            template_name="ticket_notification",
            background_tasks=background_tasks,
            ticket_title=ticket.title,
            ticket_id=ticket.id,
            response_text=response_data.response,
            ticket_url=f"{settings.FRONTEND_URL}/ticket/{ticket.id}"
        )
    
    return ticket
```

### 7. Testing Email Functionality

Create a simple test endpoint:

```python
# For development only - remove in production
@router.post("/test-email", status_code=200)
async def test_email(
    background_tasks: BackgroundTasks,
    test_email: EmailStr = Query(default=None)
):
    """Test email sending - for development use only"""
    if settings.ENVIRONMENT != "development":
        raise HTTPException(status_code=403, detail="Test endpoints disabled in production")
    
    recipient = test_email or settings.MAIL_TEST_USER
    
    await send_email(
        email_to=[recipient],
        subject="Test Email from Repport",
        template_name="test_email",
        background_tasks=background_tasks,
        app_name=settings.PROJECT_NAME,
        test_message="This is a test email to verify the email configuration."
    )
    
    return {"message": f"Test email sent to {recipient}"}
```

### 8. Email Best Practices

1. **Always Use Background Tasks**: Send emails asynchronously to avoid blocking API responses
2. **Include Text Alternatives**: Provide text versions for all HTML emails for compatibility
3. **Handle Delivery Failures**: Log email errors and implement retry strategies
4. **Rate Limiting**: Avoid sending too many emails too quickly to prevent being marked as spam
5. **Monitor Deliverability**: Regularly check spam scores and delivery rates
6. **Secure Credentials**: Never hardcode email credentials in your code
7. **Test Across Email Clients**: Ensure templates work in various email clients
8. **Include Unsubscribe Options**: Allow users to manage notification preferences

By following these steps, you'll have a robust email system integrated with your Repport application, enabling important features like password resets and notifications.

## Conclusion

This document provides a comprehensive plan for migrating the Repport application from a development environment to a production-ready deployment on Railway. By following these steps, you'll upgrade from SQLite to PostgreSQL, implement HTTPS security, and configure your application for a robust cloud deployment.

The migration will improve scalability, security, and reliability, making the application suitable for production use. After completing this migration, regularly monitor the application's health, perform database backups, and keep dependencies updated to maintain a secure and reliable system. 