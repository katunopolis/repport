# Repport API Testing Guide

This document explains how to test the Repport API to ensure all endpoints are working correctly.

## About the API Testing Scripts

We've developed several scripts to help test and diagnose API issues:

1. **api_test.py** (in `backend/scripts/tests/`): A comprehensive test suite that checks all critical endpoints
2. **fix_api_paths.py** (in `backend/scripts/tests/`): A diagnostic tool that analyzes API path issues
3. **run_api_tests.ps1** (in `frontend/scripts/`): A PowerShell script to run tests in a production-like environment

## Running the Tests

### Option 1: Using the PowerShell Script (Recommended for Windows)

The easiest way to test the API is to use the PowerShell script from the project root directory:

```powershell
.\frontend\scripts\run_api_tests.ps1
```

This script will:
1. Start the Docker containers in production mode
2. Wait for services to initialize
3. Run the API tests
4. Show logs if tests fail
5. Offer to run the API path analyzer if tests fail
6. Ask if you want to keep containers running

### Option 2: Manual Testing

If you prefer to run tests manually:

1. Start the Docker containers:
   ```bash
   docker-compose up -d
   ```

2. Run the API tests:
   ```bash
   python backend/scripts/tests/api_test.py
   ```

3. If you're experiencing 404 errors, run the path analyzer:
   ```bash
   python backend/scripts/tests/fix_api_paths.py
   ```

4. Stop containers when done:
   ```bash
   docker-compose down
   ```

## Understanding Test Results

The test script will output detailed results for each endpoint test with the following format:

```
--- Test Name: ✅ PASS ---
URL: http://localhost:8000/api/v1/endpoint
Status code: 200
Response: {
  "key": "value"
}
```

Failed tests will be marked with ❌ FAIL.

At the end, a summary shows how many tests passed out of the total.

## Common API Issues and Fixes

Based on analysis of logs and testing, here are common issues and their fixes:

### 1. 404 Not Found Errors

If you see many 404 errors in the logs, it's typically due to one of these issues:

- **API Prefix Mismatch**: The frontend is using a different API prefix than the backend expects
  - **Fix**: Ensure the API prefix in frontend/src/config.ts matches the API_V1_STR in backend/app/core/config.py

- **Router Registration Issues**: The API routers aren't registered correctly
  - **Fix**: Check backend/app/main.py to ensure routers are properly included with the right prefix

- **Double Prefixing**: If your router already has a prefix defined (e.g., in tickets.py), the combined prefix might be wrong
  - **Fix**: If tickets.router has prefix="/tickets", and you include it with prefix="/api/v1", the endpoint will be "/api/v1/tickets"

### 2. Authentication Issues

- **JWT Token Issues**: If you can't login or get 401 for authenticated endpoints
  - **Fix**: Check the bearer_transport tokenUrl in auth.py matches your actual login endpoint

- **Admin Access Issues**: If admin-only endpoints fail
  - **Fix**: Ensure the user has is_superuser=True and the dependency check is working

### 3. Database Issues

- **Connection Errors**: If the API can't connect to the database
  - **Fix**: Ensure the DATABASE_URL in settings matches your environment
  - **Fix**: For Docker environments, ensure the database container is running and accessible

## Fixed Issues in This Update

The following issues have been addressed:

1. **API Prefix Consistency**: Updated all endpoints to use the consistent API_V1_STR prefix
2. **Router Path Improvements**: Added informational endpoints at API root paths
3. **Testing Tools**: Created comprehensive testing scripts to validate endpoints
4. **Diagnostics**: Added path analysis script to identify missing or misconfigured routes
5. **Script Organization**: Moved testing scripts to appropriate directories to keep the project tidy

## Running the Path Analyzer

The path analyzer (`backend/scripts/tests/fix_api_paths.py`) is useful when you're not sure what's wrong with the API routes. It will:

1. Test each endpoint with different prefixes
2. Report which combination works best
3. Suggest fixes for any failing endpoints

This is especially helpful when frontend components are seeing 404 errors.

## Next Steps

1. Add integration tests for specific workflow scenarios
2. Implement automated testing in CI/CD pipeline
3. Add performance tests for high-volume scenarios 