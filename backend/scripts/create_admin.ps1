# PowerShell script to create an admin user in the Docker container

# Check if arguments are provided
param(
    [Parameter(Mandatory=$true)][string]$Email,
    [Parameter(Mandatory=$true)][string]$Password
)

# Get the current script directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path

# Create __init__.py file to make scripts a proper package if it doesn't exist
New-Item -Path "$scriptPath/__init__.py" -ItemType File -Force | Out-Null

# Check if Docker container is running
$containerId = docker ps -q -f name=repport-backend

if (-not $containerId) {
    Write-Host "Backend container is not running. Please start the containers with 'docker-compose up'."
    exit 1
}

# Copy the script to the container
docker cp "$scriptPath/create_admin.py" ${containerId}:/app/scripts/
docker cp "$scriptPath/__init__.py" ${containerId}:/app/scripts/

# Run the command inside the container
Write-Host "Creating admin user $Email..."
docker exec $containerId python -m scripts.create_admin $Email $Password

Write-Host "Done!" 