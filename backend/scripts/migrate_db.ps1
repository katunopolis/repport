# PowerShell script to migrate data from SQLite to PostgreSQL

# Get the script directory
$scriptPath = $PSScriptRoot
$backendPath = Split-Path -Parent $scriptPath

Write-Host "Starting database migration process..."

# Check if Docker containers are running
$dbContainer = docker ps -q -f name=repport-db
$backendContainer = docker ps -q -f name=repport-backend

if (!$dbContainer -or !$backendContainer) {
    Write-Host "Starting Docker containers..."
    docker-compose up -d
    Start-Sleep -Seconds 10  # Give containers time to start
}

# Copy the migration script to the backend container
Write-Host "Copying migration script to container..."
docker cp "$scriptPath/migrate_to_postgres.py" repport-backend-1:/app/scripts/

# Run the migration script
Write-Host "Running migration script..."
docker exec repport-backend-1 python -m scripts.migrate_to_postgres

Write-Host "Migration process complete!" 