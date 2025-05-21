# PowerShell script to run all API tests
# Usage: .\run_tests.ps1 

Write-Host "=== REPPORT API TESTING SUITE ==="
Write-Host "=================================="

# Check if Docker containers are running
Write-Host "Checking if Docker containers are running..."
$ContainersRunning = (docker ps --filter "name=repport-backend" --format "{{.Names}}" | Measure-Object).Count

if ($ContainersRunning -eq 0) {
    Write-Host "Docker containers are not running."
    Write-Host "Starting Docker containers..."
    docker-compose up -d
    Write-Host "Waiting for containers to initialize (15 seconds)..."
    Start-Sleep -Seconds 15
} else {
    Write-Host "Docker containers already running."
}

# Run the health tests
Write-Host "`nRunning API Health Tests..."
python backend/scripts/tests/api_health_test.py

# Run the path analyzer
Write-Host "`nRunning API Path Analyzer..."
python backend/scripts/tests/fix_api_paths.py

# Run the comprehensive API tests
Write-Host "`nRunning Comprehensive API Tests..."
python backend/scripts/tests/api_test.py

Write-Host "`nAll tests complete!" 