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

   - Open http://localhost:8000/docs in your browser
   - You should see the Swagger UI documentation

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

## Next Steps

After successful deployment:

1. Create a superuser account through the API
2. Set up the frontend application
3. Configure email settings with your Resend API key
4. Test all core functionality 