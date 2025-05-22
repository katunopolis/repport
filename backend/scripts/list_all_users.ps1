# PowerShell script to list all users in the Docker container

# Script location (assuming it's in the scripts folder)
$scriptPath = $PSScriptRoot
$backendPath = Split-Path -Parent $scriptPath

Write-Host "Starting user listing process..."

# Start the containers if they're not already running
$containers = docker ps --format "{{.Names}}" | Select-String "repport-backend-1"
if (!$containers) {
    Write-Host "Starting Docker containers..."
    cd ..
    docker-compose up -d
    cd $scriptPath
    Start-Sleep -Seconds 10  # Give containers time to start
}

# Copy the list script to the container
Write-Host "Copying list script to container..."
docker cp "$scriptPath/list_all_users.py" repport-backend-1:/app/list_all_users.py

# Execute the script in the container
Write-Host "Running list script..."
docker exec repport-backend-1 python /app/list_all_users.py

# Copy the results file back if it exists
Write-Host "Checking for results file..."
docker exec repport-backend-1 ls -la /app/all_users.json

if ($LASTEXITCODE -eq 0) {
    Write-Host "Copying results file from container..."
    docker cp repport-backend-1:/app/all_users.json "$scriptPath/all_users.json"
    Write-Host "Results file saved to: $scriptPath/all_users.json"
}

Write-Host "User listing complete." 