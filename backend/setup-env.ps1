# Set environment variables for Docker
$env:SECRET_KEY = "your-secret-key-here"
$env:RESEND_API_KEY = "your-resend-api-key-here"
$env:MAIL_FROM = "noreply@yourdomain.com"
$env:BACKEND_CORS_ORIGINS = "http://localhost:3000,http://localhost:8000"

# Create .env file
@"
# Security
SECRET_KEY=$env:SECRET_KEY

# Database
DATABASE_URL=sqlite+aiosqlite:///./data/helpdesk.db

# Email (Resend)
RESEND_API_KEY=$env:RESEND_API_KEY
MAIL_FROM=$env:MAIL_FROM

# CORS (comma-separated list of allowed origins)
BACKEND_CORS_ORIGINS=$env:BACKEND_CORS_ORIGINS
"@ | Out-File -FilePath .env -Encoding UTF8

Write-Host "Environment variables have been set and .env file has been created." 