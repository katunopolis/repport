# API Testing Scripts

This directory contains scripts for testing the Repport API endpoints.

## Available Scripts

- **api_test.py**: Comprehensive test suite that validates all critical API endpoints
- **fix_api_paths.py**: Diagnostic tool that analyzes API paths and identifies issues
- **API_TESTING.md**: Detailed documentation about API testing and common issues

## Usage

### From the project root:

```bash
# Run the complete test suite
python backend/scripts/tests/api_test.py

# Run the API path analyzer
python backend/scripts/tests/fix_api_paths.py
```

### For a more automated experience:

```powershell
# From the project root
.\frontend\scripts\run_api_tests.ps1
```

## Purpose

These scripts help identify and fix issues with the API, particularly 404 errors that may occur when the frontend attempts to communicate with the backend.

The tests are particularly useful for:
- Ensuring all endpoints are properly configured
- Checking authentication flows
- Validating user and ticket management functions
- Diagnosing path prefix issues 