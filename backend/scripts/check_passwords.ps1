# PowerShell script to check password hashing in the Docker container

# Script location (assuming it's in the scripts folder)
$scriptPath = $PSScriptRoot
$backendPath = Split-Path -Parent $scriptPath

Write-Host "Starting password hash check process..."

# Copy the check script to the container
Write-Host "Copying check script to container..."
docker cp "$scriptPath/check_password_hashes.py" repport-backend-1:/app/check_password_hashes.py

# Execute the script in the container
Write-Host "Running check script..."
docker exec repport-backend-1 python /app/check_password_hashes.py

Write-Host "Password check complete." 