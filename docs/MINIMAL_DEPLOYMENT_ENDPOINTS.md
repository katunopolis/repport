# API Endpoints Documentation

This document serves as a comprehensive map of all API endpoints in the helpdesk system. Use this as a reference for developing frontend components, fixing broken functionality, or extending the system with new features.

All endpoints are prefixed with: `/api/v1`

## System Endpoints

| Method | Endpoint | Description | Parameters | Response | Status |
|--------|----------|-------------|------------|----------|--------|
| GET | `/health` | Health check endpoint | None | `status`, `version`, `api_prefix` | ✅ Implemented |
| GET | `/` | Root endpoint with API information | None | `message`, `docs_url`, `redoc_url`, `api_prefix` | ✅ Implemented |
| GET | `/api` | API version information | None | `message`, `status` | ✅ Implemented |
| GET | `{settings.API_V1_STR}` | API v1 endpoints listing | None | `message`, `endpoints`, `docs_url` | ✅ Implemented |
| GET | `{settings.API_V1_STR}/debug` | Debug endpoint for API access testing | None | `status`, `prefix` | ✅ Implemented |

## Authentication Endpoints

| Method | Endpoint | Description | Parameters | Response | Status |
|--------|----------|-------------|------------|----------|--------|
| POST | `/auth/login` | User login | `email`, `password` | `access_token`, `token_type` | ✅ Fixed |
| POST | `/logout` | User logout | None | `status`, `message` | ✅ Fixed |
| POST | `/auth/register` | User registration | `email`, `password` | `access_token`, `token_type` | ✅ Fixed |
| POST | `/auth/forgot-password` | Request password reset | `email` (in request body) | `message` | ✅ Implemented |
| POST | `/auth/reset-password` | Reset password | `token`, `new_password` (in request body) | `message` | ✅ Implemented |
| POST | `/verify/{token}` | Verify email | `token` (path) | `message` | ✅ Implemented |

## User Management Endpoints

| Method | Endpoint | Description | Parameters | Response | Status |
|--------|----------|-------------|------------|----------|--------|
| GET | `/users/` | Get all users (admin only) | None | Array of user objects | ✅ Fixed |
| POST | `/users/` | Create a user (admin only) | `email`, `password`, `is_active`, `is_superuser` | User object | ✅ Fixed |
| GET | `/users/me` | Get current user profile | None | User object | ✅ Fixed |
| PATCH | `/users/me` | Update user profile | `email`, `full_name`, etc. | Updated user object | ✅ Fixed |
| GET | `/users/{id}` | Get a specific user (admin only) | None | User object | ✅ Fixed |
| PATCH | `/users/{id}` | Update a user (admin only) | `is_active`, `is_superuser`, etc. | Updated user object | ✅ Fixed |
| DELETE | `/users/{id}` | Delete a user (admin only) | None | No content | ✅ Fixed |
| PATCH | `/users/{id}/promote` | Promote/demote user to/from admin | `is_superuser` (boolean) | Updated user object | ✅ Fixed |

## Ticket Endpoints

| Method | Endpoint | Description | Parameters | Response | Status |
|--------|----------|-------------|------------|----------|--------|
| GET | `/tickets/` | List all tickets | `skip` (optional), `limit` (optional) | Array of Ticket objects | ✅ Fixed |
| POST | `/tickets/` | Create a ticket | `title`, `description`, `created_by` | Ticket object | ✅ Implemented |
| GET | `/tickets/{ticket_id}` | Get specific ticket | `ticket_id` (path) | Ticket object | ✅ Implemented |
| POST | `/tickets/{ticket_id}/respond` | Respond to ticket | `ticket_id` (path), `response` (in request body) | `status`, `message` | ✅ Implemented |
| PUT | `/tickets/{ticket_id}/status` | Update ticket status | `ticket_id` (path), `status` (in request body) | `status`, `message` | ✅ Implemented |

## API Objects

### User Object

```json
{
  "id": 1,
  "email": "user@example.com",
  "is_active": true,
  "is_superuser": false,
  "is_verified": true,
  "full_name": "John Doe",
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

### Ticket Object

```json
{
  "id": 1,
  "title": "Help with login",
  "description": "I cannot login to my account",
  "status": "open",
  "created_by": "user@example.com",
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z",
  "response": null,
  "resolved_at": null
}
```

## Implementation Details

### Authentication Flow

1. **Login:** Frontend calls `/auth/login` with credentials
2. **Token Storage:** Frontend stores the returned JWT token in localStorage
3. **API Requests:** Frontend includes the token in the Authorization header of all requests
4. **Logout:** Frontend calls `/logout` and removes the token from localStorage

### User Management Flow

1. **View All Users:** Admin frontend calls `/users/` to get all users
2. **Create User:** Admin frontend calls `/users/` with user details
3. **Promote User to Admin:** Admin frontend calls PATCH `/users/{id}` with `{"is_superuser": true}`
4. **Deactivate User:** Admin frontend calls PATCH `/users/{id}` with `{"is_active": false}`
5. **Delete User:** Admin frontend calls DELETE `/users/{id}`

### Ticket Management Flow

1. **Create Ticket:** User submits form, frontend calls POST `/tickets/`
2. **List Tickets:** Frontend loads tickets via GET `/tickets/`
3. **View Ticket:** Frontend loads ticket details via GET `/tickets/{ticket_id}`
4. **Respond to Ticket:** Admin responds via POST `/tickets/{ticket_id}/respond` with response in request body
5. **Update Status:** Admin updates status via PUT `/tickets/{ticket_id}/status` with status in request body

## Common Issues and Solutions

1. **404 Not Found for Endpoints:**
   - Ensure the frontend is using the correct base URL with `/api/v1` prefix
   - Check that the endpoint path matches exactly what the backend expects
   - Verify the API router is correctly registered in the main.py file
   - Pay attention to trailing slashes:
     - Collection endpoints (like `/users/` or `/tickets/`) require a trailing slash
     - Nested resource endpoints don't need a trailing slash (like `/tickets/{id}/respond`)
     - The logout endpoint is a special case at `/logout` without the `/auth` prefix

2. **API Path Format Guidelines:**
   - Always use the complete path format: `/api/v1/resource/`
   - FastAPI routes are sensitive to trailing slashes
   - Consistent patterns:
     - Collection endpoints: `/api/v1/resources/` (with trailing slash)
     - Individual resources: `/api/v1/resources/{id}` (no trailing slash)
     - Actions on resources: `/api/v1/resources/{id}/action` (no trailing slash)

3. **Authentication Failures:**
   - Check that the token is properly stored in localStorage
   - Ensure the Authorization header is correctly formatted as `Bearer {token}`
   - Verify the token hasn't expired

4. **Permission Errors:**
   - Confirm the user has the appropriate role (e.g., is_superuser for admin endpoints)
   - Check that authenticated user dependencies are properly set up in the backend

5. **Email Features Not Working:**
   - For the minimal deployment, email functionality gracefully degrades if no Resend API key is provided
   - Emails will be logged but not sent when email configuration is missing
   - Check logs to see what would have been sent

6. **Error Handling:**
   - The API now returns consistent error responses with the following format:
     - HTTP errors: `{"detail": "Error message", "status_code": 404}`
     - Validation errors: `{"detail": [...], "status_code": 422, "message": "Validation error"}`
     - Server errors: `{"detail": "Internal server error", "status_code": 500}`
   - All errors are properly logged in the backend for debugging

7. **Health Monitoring:**
   - Use the `/health` endpoint to monitor the service status in production environments
   - Health checks return service status, version, and API prefix information

## Recent Fixes

1. **User Management Endpoints:**
   - Added DELETE `/users/{id}` endpoint to allow admin to delete users
   - Added PATCH `/users/{id}` endpoint to allow promoting users to admin
   - Fixed GET `/users/` endpoint to list all users for admin
   - Added POST `/users/` endpoint for admin to create new users

2. **Authentication Endpoints:**
   - Fixed POST `/logout` endpoint
   - Adjusted token URL in bearer transport for proper login flow
   - Updated forgot-password and reset-password to use Body parameters instead of query parameters

3. **Ticket Endpoints:**
   - Fixed ticket router by using a prefix to ensure consistent paths
   - Updated APIs to use SQLModel select instead of raw SQL for better model handling
   - Changed endpoints to use Body parameters instead of query parameters for better security

4. **API URL Structure Fixes:**
   - Corrected frontend API client to use the proper URLs with consistent format
   - Fixed logout endpoint to use `/logout` instead of `/auth/logout`
   - Added trailing slashes to collection endpoints like `/tickets/` and `/users/`
   - Ensured all endpoints follow FastAPI routing conventions

5. **Email Functionality:**
   - Added graceful degradation for missing email configuration
   - Implemented detailed logging when emails cannot be sent
   - Email services now work in the minimal deployment without requiring API keys

6. **System Monitoring and Debugging:**
   - Added `/health` endpoint for monitoring service status
   - Improved global exception handling for consistent error responses
   - Enhanced logging in various parts of the application
   - Added debug route to test API accessibility

## Adding New Endpoints

When adding new endpoints to the system:

1. Define the endpoint function in the appropriate API file
2. Update this documentation with the endpoint details
3. Update the frontend API client to use the new endpoint
4. Test the endpoint using the backend's auto-generated Swagger UI at `/docs`

Remember to maintain consistency with the existing API design patterns and error handling approaches. 

## Testing Endpoints

To systematically test the API endpoints, use the dedicated testing tools:

### API Test Suite

The project includes a comprehensive API test suite in `backend/scripts/tests/api_test.py` that validates all endpoints listed in this document.

To run the tests:

```bash
# From project root
python backend/scripts/tests/api_test.py
```

### Automated Testing Script

For a more streamlined testing experience, use the PowerShell script:

```powershell
# From project root
.\frontend\scripts\run_api_tests.ps1
```

This script orchestrates Docker containers and runs all API tests in a production-like environment.

### API Path Analyzer

If you're experiencing 404 errors or other routing issues, use the path analyzer tool:

```bash
# From project root
python backend/scripts/tests/fix_api_paths.py
```

This tool will:
1. Test all endpoints with different URL prefixes
2. Identify which URLs are working and which are failing
3. Suggest fixes for misconfigured routes

### Documentation

For detailed API testing documentation, refer to `backend/scripts/tests/API_TESTING.md`. 