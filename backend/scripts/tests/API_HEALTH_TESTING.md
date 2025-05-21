# API Health Testing

This document describes how to use the API health testing tools to verify that the API endpoints are functioning correctly.

## API Health Tests

The API health tests check the basic functionality of the API:

1. **Health Endpoint Test**: Verifies that the `/health` endpoint returns the correct status and information
2. **Debug Endpoint Test**: Checks that the API debugging endpoint is accessible
3. **Error Handling Test**: Ensures that the API returns proper error responses for various situations

## Running the Tests

To run the API health tests:

```bash
# From project root
python backend/scripts/tests/api_health_test.py
```

Or with a custom API base URL:

```bash
# From project root
python backend/scripts/tests/api_health_test.py http://custom-api-url:8000
```

## Test Details

### Health Endpoint Test

This test verifies:
- The `/health` endpoint returns a 200 status code
- The response contains a "healthy" status
- The response includes version information
- The response includes the API prefix

### Debug Endpoint Test

This test verifies:
- The `/api/v1/debug` endpoint returns a 200 status code
- The response contains the expected status message
- The response includes the API prefix information

### Error Handling Test

This test verifies:
- Non-existent endpoints return a 404 status with appropriate error details
- Invalid requests to authenticated endpoints return proper validation errors

## Relationship to API Path Testing

The API health tests are complementary to the API path testing tools:

- **API Health Tests** (`api_health_test.py`): Focus on the basic health and error responses of the API
- **API Path Tests** (`fix_api_paths.py`): Diagnose issues with specific API paths and prefixes
- **Comprehensive API Tests** (`api_test.py`): Test all API endpoints and functionality

## Integration with CI/CD

These tests can be integrated into CI/CD pipelines to ensure that the API health is maintained after changes.

```yaml
# Example GitHub Actions workflow step
- name: Test API Health
  run: python backend/scripts/tests/api_health_test.py
```

## Next Steps

After running the health tests, use the more comprehensive test suites:

```bash
# Run API path diagnostics
python backend/scripts/tests/fix_api_paths.py

# Run comprehensive API tests
python backend/scripts/tests/api_test.py
``` 