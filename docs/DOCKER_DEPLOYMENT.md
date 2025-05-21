# Docker Deployment Guide

This guide provides step-by-step instructions for deploying the helpdesk application using Docker.

## Prerequisites

1. Docker Desktop installed and running
2. Git repository cloned locally
3. `.env` file with required environment variables

## Environment Setup

Create a `.env` file in the `backend` directory with the following variables:

```env
# API Settings
SECRET_KEY=your_secret_key_here  # Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
PROJECT_NAME="Helpdesk API"

# Database Settings
DATABASE_URL=sqlite+aiosqlite:///./data/helpdesk.db
# Connection pool settings (for PostgreSQL, MySQL, etc.)
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=1800

# CORS Settings
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# Security Settings
ACCESS_TOKEN_EXPIRE_MINUTES=11520  # 8 days in minutes

# Development Settings
DEBUG=True
ENVIRONMENT=development

# Email Settings (Resend.com)
MAIL_USERNAME=resend
MAIL_PASSWORD=your_resend_api_key  # Get from Resend.com
MAIL_FROM=your_verified_email@example.com
MAIL_PORT=587
MAIL_SERVER=smtp.resend.com
```

For the minimal deployment (MVP), the email configuration is optional. The application will gracefully handle missing email configuration by logging messages instead of sending emails.

## Directory Setup

1. Create the data directory for SQLite:

```bash
mkdir -p backend/data
```

2. Ensure all required files are present:

```
helpdesk-minimal/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py
│   │   │   └── tickets.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   ├── email.py
│   │   │   └── security.py
│   │   ├── models/
│   │   │   ├── ticket.py
│   │   │   └── user.py
│   │   └── main.py
│   ├── data/  # For SQLite database
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env  # Your environment variables
├── docker-compose.yml
```

## Docker Configuration

### 1. Dockerfile

The `backend/Dockerfile` should include:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create directory for SQLite database and set permissions
RUN mkdir -p /app/data && chmod 777 /app/data

# Copy the rest of the application
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

### 2. Docker Compose

The `docker-compose.yml` should include:

```yaml
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env
    volumes:
      - ./backend:/app
      - ./backend/data:/app/data
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Deployment Steps

1. Ensure Docker Desktop is running

2. Build and start the containers:

```bash
docker-compose up --build
```

3. Verify the application is running:

   - Open http://localhost:8000/docs in your browser to see the Swagger UI documentation
   - Check the health endpoint at http://localhost:8000/health to verify the API is running correctly
   - The health endpoint should return something like:
   ```json
   {
     "status": "healthy", 
     "version": "1.0.0",
     "api_prefix": "/api/v1"
   }
   ```

4. To stop the application:

```bash
docker-compose down
```

## Troubleshooting

If you encounter issues, please refer to the "Docker Deployment Troubleshooting" section in the MINIMAL_DEPLOYMENT.md document.

Common issues include:

1. Docker Desktop not running
2. Environment variables not loaded properly
3. Issues with async SQLite driver
4. Folder permission problems
5. Library version incompatibilities

## Recent Improvements

The latest version of the helpdesk system includes several improvements for better reliability and security:

1. **Graceful Email Handling**: The application now works without requiring email configuration by logging messages instead of sending emails.

2. **Enhanced API Security**: API endpoints now use Body parameters instead of query parameters for better security and consistency.

3. **Improved ORM Usage**: Ticket endpoints have been updated to use SQLModel select statements instead of raw SQL for better maintainability and type safety.

4. **Secure Password Reset**: Password reset endpoints use secure body parameters to prevent sensitive information appearing in URLs or logs.

5. **API URL Consistency**: Fixed URL format consistency issues with trailing slashes and proper prefixes to eliminate 404 errors.

6. **Fixed Authentication**: Resolved bcrypt compatibility issues by pinning to a specific version and implementing required user manager methods.

7. **User Management Enhancement**: Added a dedicated endpoint for promoting/demoting users to/from admin status with proper error handling.

8. **Global Exception Handling**: Added consistent error response format for HTTP exceptions, validation errors, and server errors.

9. **Health Check Endpoint**: Added a `/health` endpoint for monitoring the application status in production environments.

10. **Database Connection Pooling**: Implemented connection pooling with configuration options to improve database performance and reliability.

11. **Enhanced Logging**: Added more detailed logging across the application for better debugging and monitoring.

## Monitoring and Health Checks

The application now includes a health check endpoint at `/health` that returns the current status, API version, and API prefix. This can be used for monitoring the application in production environments.

To check the health of the application:

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy", 
  "version": "1.0.0",
  "api_prefix": "/api/v1"
}
```

For comprehensive monitoring, you can use tools like Prometheus and Grafana to collect and visualize health check data, or integrate with cloud provider monitoring services.

## Troubleshooting Common 404 Errors

If you encounter 404 (Not Found) errors when accessing API endpoints, check the following:

1. **URL Format**: Ensure you're using the correct URL format with appropriate slashes:
   - Collection endpoints must include trailing slashes (e.g., `/api/v1/users/`)
   - Individual resources should not have trailing slashes (e.g., `/api/v1/users/{id}`)

2. **API Prefix**: All API endpoints must use the `/api/v1` prefix (e.g., `/api/v1/tickets/`)

3. **Special Case Endpoints**: Some endpoints have specific formats:
   - Logout: `/logout` (no `/auth` prefix)
   - Auth endpoints: `/auth/login`, `/auth/register`, etc.

4. **Debug with Tools**: Run the API path analyzer to diagnose routing issues:
   ```bash
   python backend/scripts/tests/fix_api_paths.py
   ```

5. **Check Docker Logs**: View backend logs to see what URLs are being requested:
   ```bash
   docker-compose logs backend | grep "HTTP" | grep "404"
   ```

## Next Steps

After successful deployment:

1. Create a superuser account through the API
2. Set up the frontend application
3. Configure email settings with your Resend API key
4. Test all core functionality with the API testing tools:
   ```powershell
   # From project root
   .\frontend\scripts\run_api_tests.ps1
   ```
   
   Or run tests manually:
   ```bash
   # Test API endpoints
   python backend/scripts/tests/api_test.py
   
   # Diagnose API routing issues if needed
   python backend/scripts/tests/fix_api_paths.py
   ```

5. For more details on testing, see `backend/scripts/tests/API_TESTING.md` 