# Frontend Scripts

This directory contains utility scripts for the Repport frontend.

## Available Scripts

- **run_api_tests.ps1**: PowerShell script to test API endpoints in a production-like Docker environment

## Usage

```powershell
# From the project root directory
.\frontend\scripts\run_api_tests.ps1
```

## What the API Test Script Does

1. Starts the Docker containers in production mode
2. Waits for services to initialize
3. Runs the comprehensive API tests located in backend/scripts/tests/api_test.py
4. If tests fail:
   - Shows backend logs for debugging
   - Offers to run the API path analyzer
5. Asks if you want to keep the containers running
6. Returns success/failure status code

## Best Practices

- Always run this script from the project root directory
- Use this script before committing changes to ensure API functionality
- If tests fail, use the API path analyzer to diagnose issues 