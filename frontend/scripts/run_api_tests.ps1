# Script to test API endpoints in a production-like environment
# Usage: .\scripts\run_api_tests.ps1
# Run from the project root directory

Write-Host "Starting Repport API Test Suite" -ForegroundColor Cyan

# Get the script directory and project root
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent (Split-Path -Parent $scriptDir)

# Set working directory to project root
Set-Location $projectRoot

# 1. Run Docker Compose (production mode)
Write-Host "Starting Docker containers in production mode..." -ForegroundColor Yellow
docker-compose down
docker-compose up -d

# 2. Wait for services to start (give extra time for database initialization)
Write-Host "Waiting for services to initialize (15 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# 3. Run API tests
Write-Host "Running API tests..." -ForegroundColor Yellow
python backend/scripts/tests/api_test.py

# 4. Store test result
$testResult = $LASTEXITCODE

# 5. Show backend logs if tests failed
if ($testResult -ne 0) {
    Write-Host "Some tests failed. Showing backend logs for debugging:" -ForegroundColor Red
    docker-compose logs backend
    
    # Offer to run the API path analyzer
    $runAnalyzer = Read-Host "Would you like to run the API path analyzer to diagnose the issues? (y/n)"
    if ($runAnalyzer -eq "y") {
        Write-Host "Running API path analyzer..." -ForegroundColor Yellow
        python backend/scripts/tests/fix_api_paths.py
    }
}

# 6. Ask if user wants to keep containers running
$keepRunning = Read-Host "Do you want to keep the containers running? (y/n)"
if ($keepRunning -ne "y") {
    Write-Host "Stopping containers..." -ForegroundColor Yellow
    docker-compose down
}

# 7. Exit with the test result code
Write-Host "Test script completed." -ForegroundColor Cyan
exit $testResult 