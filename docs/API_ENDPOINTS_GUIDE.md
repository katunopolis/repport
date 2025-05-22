# API Endpoints Guide

This document provides a comprehensive guide to the API endpoints in the Repport system, including the fixes implemented to address inconsistencies and best practices for future development.

## API Structure

All API endpoints follow a consistent structure:

- **Base URL**: `http://localhost:8000/api/v1` (configurable via environment variables)
- **Collection Endpoints**: Include trailing slashes (e.g., `/tickets/`, `/users/`)
- **Resource Endpoints**: No trailing slashes (e.g., `/tickets/{id}`, `/users/{id}`)
- **Action Endpoints**: No trailing slashes (e.g., `/tickets/{id}/respond`, `/users/{id}/promote`)

> **New Enhancement**: The API now handles both trailing slash and non-trailing slash paths automatically. Either format will work for all endpoints.

## Authentication

### Login

```
POST /api/v1/auth/login
```

**Request Format**: Form data (not JSON)
```javascript
// Correct login format
const formData = new URLSearchParams();
formData.append('username', email);  // Note: field is 'username' even for email login
formData.append('password', password);

const response = await axios.post('/api/v1/auth/login', formData, {
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded'
  }
});
```

**Response Format**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error Handling**:
- 401 Unauthorized: If the email doesn't exist or the password is incorrect
- 422 Unprocessable Entity: If username or password is missing

> **IMPORTANT**: This endpoint has been fixed to properly validate passwords and return appropriate error messages for invalid credentials.

### Custom Signup

```
POST /api/v1/auth/signup
```

**Request Format**: JSON
```javascript
// Signup format
const userData = {
  "email": "user@example.com",
  "password": "securepassword"
};

const response = await axios.post('/api/v1/auth/signup', userData);
```

**Response Format**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "is_active": true,
    "is_superuser": false
  }
}
```

**Error Handling**:
- 400 Bad Request: If a user with the email already exists
- 400 Bad Request: If the password doesn't meet minimum requirements
- 422 Unprocessable Entity: If email or password is missing

### Token Authentication

Include the JWT token in the Authorization header for endpoints requiring authentication:

```javascript
const headers = {
  'Authorization': `Bearer ${token}`
};
const response = await axios.get('/api/v1/users/', { headers });
```

### Forgot Password

```
POST /api/v1/auth/forgot-password
```

**Request Format**: JSON
```javascript
// Request format
const userData = {
  "email": "user@example.com"
};

const response = await axios.post('/api/v1/auth/forgot-password', userData);
```

**Response Format**:
```json
{
  "message": "If an account exists with this email, you will receive a password reset link"
}
```

> **Note**: In development mode, the response may include the actual reset token for testing purposes:
> ```json
> {
>   "message": "Password reset token generated. In production, this would be emailed.",
>   "token": "random-token-string",
>   "_dev_note": "This token is only returned in development mode"
> }
> ```

**Error Handling**:
- For security reasons, this endpoint returns the same message regardless of whether the email exists

### Reset Password

```
POST /api/v1/auth/reset-password
```

**Request Format**: JSON
```javascript
// Reset password format
const resetData = {
  "token": "reset-token-from-email",
  "new_password": "newSecurePassword"
};

const response = await axios.post('/api/v1/auth/reset-password', resetData);
```

**Response Format**:
```json
{
  "message": "Password has been reset successfully"
}
```

**Error Handling**:
- 400 Bad Request: If the token is invalid or expired
- 400 Bad Request: If the new password doesn't meet minimum requirements (at least 8 characters)
- 422 Unprocessable Entity: If token or new_password is missing

### Change Password (Authenticated Users)

```
POST /api/v1/users/me/change-password
```

**Authentication**: Required

**Request Format**: JSON
```javascript
// Change password format
const changePasswordData = {
  "current_password": "yourCurrentPassword",
  "new_password": "yourNewSecurePassword"
};

// Authentication header required - fixed in v1.3.1
const response = await axios.post(getFullApiUrl('users/me/change-password'), changePasswordData, {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

> **IMPORTANT**: This endpoint requires a valid JWT token in the Authorization header. As of v1.3.1, the client implementation was updated to properly include authorization tokens in these requests.

**Response Format**:
```json
{
  "message": "Password changed successfully"
}
```

**Error Handling**:
- 401 Unauthorized: If authentication token is missing or invalid, or if the current password is incorrect
- 400 Bad Request: If the new password doesn't meet minimum requirements (at least 8 characters)
- 400 Bad Request: If the new password is the same as the current password
- 422 Unprocessable Entity: If current_password or new_password is missing

## Ticket Endpoints

### List All Tickets

```
GET /api/v1/tickets/
```

**Authentication**: Not required

**Response**: Array of ticket objects

### Get Specific Ticket

```
GET /api/v1/tickets/{id}
```

**Authentication**: Not required

**Response**: Ticket object

### Create Ticket

```
POST /api/v1/tickets/
```

**Authentication**: Not required

**Request Body**:
```json
{
  "title": "Ticket Title",
  "description": "Detailed description of the issue",
  "status": "open"
}
```

> **IMPORTANT**: The `status` field is required when creating tickets. Valid values are "open", "in_progress", or "closed". If not explicitly provided, use "open" as the default status.

**Response**: Created ticket object

### Respond to Ticket

```
POST /api/v1/tickets/{id}/respond
```

**Authentication**: Required

**Request Body**:
```json
{
  "response": "This is the response to the ticket"
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Response sent successfully"
}
```

### Solve Ticket (Admin Only)

```
PUT /api/v1/tickets/{id}/solve
```

**Authentication**: Required (Admin only)

**Request Body**:
```json
{
  "response": "This is the final response to close the ticket"
}
```

**Response**: Complete ticket object with updated status "closed"

This endpoint combines two operations:
1. Updates the ticket's response with the final message
2. Changes the ticket status to "closed"

Once a ticket is closed via the solve endpoint, no further responses can be added.

### Update Ticket Status

```
PUT /api/v1/tickets/{id}/status
```

**Authentication**: Required

**Request Body**:
```json
{
  "status": "in_progress" 
}
```

**Valid Status Values**: `open`, `in_progress`, `closed`

**Response**:
```json
{
  "status": "success",
  "message": "Ticket status updated to in_progress"
}
```

## User Endpoints

### Get Current User

```
GET /api/v1/users/me
```

**Authentication**: Required

**Response**: User object for the authenticated user

### List All Users

```
GET /api/v1/users/
```

**Authentication**: Required (Admin only)

**Response**: Array of user objects

### Get Specific User

```
GET /api/v1/users/{id}
```

**Authentication**: Required (Admin only)

**Response**: User object

### Create User

```
POST /api/v1/users/
```

**Authentication**: Required (Admin only)

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "is_active": true,
  "is_superuser": false,
  "is_verified": true
}
```

**Response**: Created user object

### Promote User to Admin

```
PATCH /api/v1/users/{id}/promote
```

**Authentication**: Required (Admin only)

**Request Body**:
```json
{
  "is_superuser": true
}
```

**Response**: Updated user object

### Delete User

```
DELETE /api/v1/users/{id}
```

**Authentication**: Required (Admin only)

**Response**: 204 No Content

## Error Handling

### Common HTTP Status Codes

- **200 OK**: Request successful
- **204 No Content**: Request successful, no content to return
- **400 Bad Request**: Invalid input
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Not enough permissions
- **404 Not Found**: Resource not found
- **422 Unprocessable Entity**: Validation error

### Error Response Format

```json
{
  "detail": "Error message",
  "status_code": 400,
  "message": "Detailed error description"
}
```

## Common API Issues and Solutions

1. **404 Not Found Errors**:
   - Ensure all API calls include the `/api/v1` prefix
   - ~~Verify collection endpoints have trailing slashes~~ The API now handles paths with or without trailing slashes automatically

2. **Authentication Errors (401 Unauthorized)**:
   - Check that login requests use form data format, not JSON
   - Include 'Content-Type': 'application/x-www-form-urlencoded' header for login
   - Ensure the JWT token is included in the Authorization header for authenticated endpoints

3. **Permission Errors (403 Forbidden)**:
   - Verify that the user has admin privileges for admin-only endpoints
   - Check that the user has `is_superuser=true` for admin operations

4. **Validation Errors (422 Unprocessable Entity)**:
   - Ensure request body matches the expected format
   - Check that all required fields are included

## Testing API Endpoints

Three test scripts are available to validate API functionality:

1. **API Health Test**:
```bash
python backend/scripts/tests/api_health_test.py
```
Tests basic API health endpoints and error handling.

2. **API Path Analyzer**:
```bash
python backend/scripts/tests/fix_api_paths.py
```
Diagnoses issues with API paths and identifies the correct prefixes.

3. **Comprehensive API Test**:
```bash
python backend/scripts/tests/api_test.py
```
Tests all API endpoints with authentication and data manipulation.

4. **Run All Tests** (PowerShell):
```bash
powershell -File backend/scripts/tests/run_tests.ps1
```
Runs all three tests in sequence.

## Best Practices for API Development

1. **Consistent Path Structure**:
   - Always use the `/api/v1` prefix
   - Collection endpoints must have trailing slashes
   - Resource and action endpoints should not have trailing slashes
   - **IMPORTANT UPDATE**: The API now handles both trailing slash and non-trailing slash paths via a custom middleware, so either format will work

2. **Authentication**:
   - Use JWT tokens for authentication
   - Include tokens in the Authorization header
   - Clearly document which endpoints require authentication

3. **Error Handling**:
   - Return appropriate HTTP status codes
   - Include detailed error messages in the response
   - Validate input before processing

4. **Documentation**:
   - Document all endpoints, parameters, and responses
   - Include examples for common operations
   - Update documentation when making changes

5. **Testing**:
   - Write automated tests for all endpoints
   - Test both successful operations and error cases
   - Verify authentication requirements

6. **Frontend API URL Construction**:
   - Use the provided helper function to construct proper API URLs:
   ```typescript
   import { getFullApiUrl } from '../config';
   
   // Use this helper for all API calls
   const response = await axios.post(getFullApiUrl('auth/login'), data);
   ```
   - This ensures all requests include the required `/api/v1` prefix
   - The helper handles edge cases such as missing slashes and different base URL formats
   - See `frontend/src/config.ts` for the full implementation

7. **Ticket Creation Best Practices**:
   - Always include all required fields when creating a ticket
   - The Ticket interface requires the following fields:
   ```typescript
   // When creating a ticket, provide these fields:
   {
     title: string;       // Required
     description: string; // Required
     status: string;      // Required - use 'open' as default
   }
   ```
   - Use the following pattern for ticket creation in the frontend:
   ```typescript
   await ticketsApi.createTicket({
     title: newTicket.title,
     description: newTicket.description,
     status: 'open'  // Always provide a default status
   });
   ```

8. **Ticket ID Formatting**:
   - Use the `formatTicketId` helper function for displaying ticket IDs
   - This formats IDs with the VR prefix and leading zeros: `VR000001`, `VR000002`, etc.
   - Example usage:
   ```typescript
   import { formatTicketId } from '../api/api';
   
   // In your component:
   <Chip label={formatTicketId(ticket.id)} />
   ```
   - This provides a consistent appearance across the application

9. **User Registration Flow**:
   - Direct users to the `/signup` route for account creation
   - Validate password requirements (minimum 8 characters)
   - Confirm passwords match before submitting
   - Upon successful registration, users are automatically logged in
   - Implementation is in `SignupPage.tsx`

## Implemented Fixes

The following issues were identified and fixed in the API:

1. **Inconsistent API Paths**: Standardized all paths to use the `/api/v1` prefix
2. **Authentication Format**: Ensured login requests use form data instead of JSON
3. **Trailing Slashes**: Added trailing slashes to all collection endpoints
4. **Error Responses**: Standardized error response format
5. **Documentation**: Created comprehensive API documentation
6. **Frontend API URL Construction**: Added a `getFullApiUrl` helper function to ensure all frontend API calls include the correct `/api/v1` prefix regardless of environment configuration
7. **Trailing Slash Handling**: Added a middleware to automatically handle both trailing slash and non-trailing slash versions of all API endpoints
8. **Ticket Creation**: Fixed ticket creation by ensuring the required `status` field is always included with a default value of "open"

These fixes have resolved the 404 errors and improved the overall API consistency and reliability.

## API Path Analyzer Results

The API Path Analyzer identified these endpoints with their status:

| Endpoint | Working Path | Auth Required | Notes |
|----------|--------------|--------------|-------|
| /auth/login | /api/v1/auth/login | No | 422 response is expected when no data provided |
| /tickets | /api/v1/tickets/ | No | Working correctly |
| /users | /api/v1/users/ | Yes | 401 response is expected as it requires auth |
| /tickets/1 | /api/v1/tickets/1 | No | Working correctly |
| /users/2 | /api/v1/users/2 | Yes | 401 response is expected as it requires auth |
| /logout | /api/v1/logout | No | 405 response indicates method not allowed (POST only) |
| /tickets/4 | /api/v1/tickets/4 | No | Working correctly | 

## New Middleware for Trailing Slash Handling

The API now includes a custom `TrailingSlashMiddleware` that automatically handles requests with or without trailing slashes. This means:

1. If you request a path like `/api/v1/tickets` (no trailing slash), it will be handled correctly
2. If you request a path like `/api/v1/tickets/` (with trailing slash), it will also be handled correctly
3. The middleware automatically tries both versions when a 404 is encountered

This ensures maximum compatibility and makes the API more robust to different client implementations.

### Implementation Details

The middleware works as follows:
1. First tries the path as provided in the request
2. If a 404 is returned, tries the alternative path (adding or removing trailing slash)
3. Returns the response from whichever path works

This means your frontend client can use either format consistently without worrying about 404 errors.

### Duplicate Endpoint Handlers

For critical endpoints, we've also added explicit duplicate handlers with and without trailing slashes:

```python
@router.get("/users")
async def list_users(...):
    # Original implementation

@router.get("/users/")
async def list_users_with_slash(...):
    return await list_users(...)
```

This ensures consistent behavior across all endpoints and prevents any issues with authentication during redirects.

## Frontend Configuration

The frontend configuration has been updated to use this new flexibility:

```typescript
// Helper to ensure all API calls have the correct prefix
export const getFullApiUrl = (endpoint: string): string => {
  // Add /api/v1 prefix if it's not already included
  const base = config.apiUrl.endsWith('/api/v1') 
    ? config.apiUrl 
    : `${config.apiUrl}/api/v1`;
  
  // Remove leading slash from endpoint if present
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint.substring(1) : endpoint;
  
  // Note: The backend handles both trailing slash and non-trailing slash paths identically
  // so we don't need to worry about adding/removing trailing slashes here
  return `${base}/${cleanEndpoint}`;
};
```

This means frontend developers don't need to worry about adding or removing trailing slashes when making API calls. 

## User Management

### Current User

```
GET /api/v1/users/me
```

**Authentication**: Required

**Response**: Current user object

### List All Users

```
GET /api/v1/users/
```

**Authentication**: Required (Admin only)

**Response**: Array of user objects

### Get User

```
GET /api/v1/users/{id}
```

**Authentication**: Required (Admin only)

**Response**: User object

> **Note**: User IDs are represented as strings in the frontend interface and API methods

### Create User

```
POST /api/v1/users/
```

**Authentication**: Required (Admin only)

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "is_active": true,
  "is_superuser": false,
  "is_verified": true
}
```

**Response**: Created user object 