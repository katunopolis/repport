# PowerShell script to run API tests in Docker
# Usage: .\run_docker_tests.ps1 [test_type]
# test_type: all, health, paths, api (default: all)

# Define colors for output
$Green = "$([char]27)[32m"
$Red = "$([char]27)[31m"
$Blue = "$([char]27)[34m"
$Reset = "$([char]27)[0m"

# Print header
Write-Host "${Blue}=======================================${Reset}"
Write-Host "${Blue}     REPPORT API TESTING SUITE         ${Reset}"
Write-Host "${Blue}=======================================${Reset}"

# Determine which tests to run
$TestType = if ($args[0]) { $args[0] } else { "all" }

# Ensure containers are running
Write-Host "${Blue}Checking if Docker containers are running...${Reset}"
$ContainersRunning = (docker ps --filter "name=repport-backend" --format "{{.Names}}" | Measure-Object).Count

if ($ContainersRunning -eq 0) {
    Write-Host "${Red}Docker containers are not running.${Reset}"
    Write-Host "${Blue}Starting Docker containers...${Reset}"
    docker-compose up -d
    Write-Host "${Blue}Waiting for containers to initialize (15 seconds)...${Reset}"
    Start-Sleep -Seconds 15
} else {
    Write-Host "${Green}Docker containers already running.${Reset}"
}

# Function to run a test and check its success
function Run-Test {
    param (
        [string]$TestName,
        [string]$TestCommand
    )
    
    Write-Host "`n${Blue}Running $TestName tests...${Reset}"
    Write-Host "${Blue}----------------------------------------${Reset}"
    
    Invoke-Expression $TestCommand
    $Result = $LASTEXITCODE
    
    if ($Result -eq 0) {
        Write-Host "`n${Green}✓ $TestName tests passed${Reset}"
        return $true
    } else {
        Write-Host "`n${Red}✗ $TestName tests failed${Reset}"
        return $false
    }
}

# Keep track of test results
$PassedTests = 0
$TotalTests = 0

# Run health tests
if (($TestType -eq "all") -or ($TestType -eq "health")) {
    if (Run-Test "API Health" "python backend/scripts/tests/api_health_test.py") {
        $PassedTests++
    }
    $TotalTests++
}

# Run path analysis
if (($TestType -eq "all") -or ($TestType -eq "paths")) {
    if (Run-Test "API Path Analyzer" "python backend/scripts/tests/fix_api_paths.py") {
        $PassedTests++
    }
    $TotalTests++
}

# Run comprehensive API tests
if (($TestType -eq "all") -or ($TestType -eq "api")) {
    if (Run-Test "Comprehensive API" "python backend/scripts/tests/api_test.py") {
        $PassedTests++
    }
    $TotalTests++
}

# Print summary
Write-Host "`n${Blue}=======================================${Reset}"
Write-Host "${Blue}             TEST SUMMARY              ${Reset}"
Write-Host "${Blue}=======================================${Reset}"
Write-Host "Tests run: $TotalTests"
Write-Host "Tests passed: $PassedTests"

if ($PassedTests -eq $TotalTests) {
    Write-Host "${Green}All tests passed!${Reset}"
    exit 0
} else {
    Write-Host "${Red}Some tests failed.${Reset}"
    exit 1
} 