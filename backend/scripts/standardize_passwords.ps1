# PowerShell script to standardize password hashing in the Docker container

# Script location (assuming it's in the scripts folder)
$scriptPath = $PSScriptRoot
$backendPath = Split-Path -Parent $scriptPath

Write-Host "Starting password hash standardization process..."

# Copy the standardize script to the container
Write-Host "Copying standardization script to container..."
docker cp "$scriptPath/standardize_password_hashing.py" repport-backend-1:/app/standardize_password_hashing.py

# Execute the script in the container
Write-Host "Running standardization script..."
docker exec repport-backend-1 python /app/standardize_password_hashing.py

# Copy the results file back if it exists
Write-Host "Checking for password reset file..."
docker exec repport-backend-1 ls -la /app/reset_passwords.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "Copying password reset file from container..."
    docker cp repport-backend-1:/app/reset_passwords.txt "$scriptPath/reset_passwords.txt"
    Write-Host "Password reset file saved to: $scriptPath/reset_passwords.txt"
}

Write-Host "Password standardization complete." 