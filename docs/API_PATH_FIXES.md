# API Path Fixes Documentation

This document outlines the API path fixes implemented to resolve the 404 errors and ensure consistent API access.

## API Path Structure

All API endpoints should follow this structure:

- **Base URL**: `http://localhost:8000/api/v1` (configurable via environment variables)
- **Collection Endpoints**: Must include trailing slashes (e.g., `/tickets/`, `/users/`)
- **Resource Endpoints**: No trailing slashes (e.g., `/tickets/{id}`, `/users/{id}`)
- **Action Endpoints**: No trailing slashes (e.g., `/tickets/{id}/respond`, `/users/{id}/promote`)

> **New Enhancement**: The API now handles both trailing slash and non-trailing slash paths automatically. Either format will work for all endpoints.

## Fixed Endpoints

| Endpoint | Method | Description | Fixed Path | Auth Required | Notes |
|----------|--------|-------------|------------|--------------|-------|
| Login | POST | User login via form data | `/api/v1/auth/login` | No | Form-encoded data required |
| Register | POST | Create new user | `/api/v1/auth/register` | No | |
| Logout | POST | User logout | `/api/v1/logout` | No | |
| Forgot Password | POST | Request password reset | `/api/v1/auth/forgot-password` | No | |
| Reset Password | POST | Reset password with token | `/api/v1/auth/reset-password` | No | |
| Current User | GET | Get current user profile | `/api/v1/users/me` | Yes | Bearer token |
| List Tickets | GET | Get all tickets | `/api/v1/tickets/` | No | |
| Get Ticket | GET | Get specific ticket | `/api/v1/tickets/{id}` | No | |
| Create Ticket | POST | Create new ticket | `/api/v1/tickets/` | No | |
| Respond to Ticket | POST | Add response to ticket | `/api/v1/tickets/{id}/respond` | No | |
| Solve Ticket | PUT | Respond and close ticket | `/api/v1/tickets/{id}/solve` | Yes | Admin only |
| Update Ticket Status | PUT | Change ticket status | `/api/v1/tickets/{id}/status` | No | |
| List Users | GET | Get all users (admin) | `/api/v1/users/` | Yes | Admin token required |
| Get User | GET | Get specific user (admin) | `/api/v1/users/{id}` | Yes | Admin token required |
| Create User | POST | Create new user (admin) | `/api/v1/users/` | Yes | Admin token required |
| Update User | PATCH | Update user (admin) | `/api/v1/users/{id}` | Yes | Admin token required |
| Promote User | PATCH | Change admin status | `/api/v1/users/{id}/promote` | Yes | Admin token required |
| Delete User | DELETE | Remove user (admin) | `/api/v1/users/{id}` | Yes | Admin token required |

## Authentication Formats

1. **Login Request**: Must use form data format
   ```javascript
   const formData = new URLSearchParams();
   formData.append('username', email);
   formData.append('password', password);
   
   const response = await axios.post('/api/v1/auth/login', formData, {
     headers: {
       'Content-Type': 'application/x-www-form-urlencoded'
     }
   });
   ```

2. **Bearer Token Authentication**: Include in request headers
   ```javascript
   const headers = {
     'Authorization': `Bearer ${token}`
   };
   const response = await axios.get('/api/v1/users/', { headers });
   ```

## Admin API Authentication Fixes

To address issues with admin-only endpoints and authentication persistence through redirects:

1. **Explicit Authentication Headers**: For all admin endpoints, always explicitly include the authentication token in the request headers:
   ```typescript
   const token = localStorage.getItem(config.authTokenKey);
   const response = await axios.get(getFullApiUrl('users/'), {
     headers: {
       Authorization: `Bearer ${token}`
     }
   });
   ```

2. **Backend Route Duplication**: Both trailing slash and non-trailing slash versions of admin routes are now supported:
   - `/api/v1/users` - Original route
   - `/api/v1/users/` - Duplicate route that calls the original handler
   
   This prevents 307 redirects that can sometimes lose authentication headers.

3. **Authentication Verification**: All admin routes now consistently verify:
   - That the user is authenticated (valid token)
   - That the user has admin privileges (`is_superuser=true`)

## Frontend API Client Improvements

To ensure that all API requests correctly include the `/api/v1` prefix, we've implemented the following improvements:

1. **Helper Function**: Created a utility function in `frontend/src/config.ts` to construct proper API URLs:
   ```typescript
   // Helper to ensure all API calls have the correct prefix
   export const getFullApiUrl = (endpoint: string): string => {
     // Add /api/v1 prefix if it's not already included
     const base = config.apiUrl.endsWith('/api/v1') 
       ? config.apiUrl 
       : `${config.apiUrl}/api/v1`;
     
     // Remove leading slash from endpoint if present
     const cleanEndpoint = endpoint.startsWith('/') ? endpoint.substring(1) : endpoint;
     
     return `${base}/${cleanEndpoint}`;
   };
   ```

2. **Standardized API Calls**: Updated all API functions to use this helper:
   ```typescript
   // Before
   const response = await api.post('/auth/login', formData, {...});
   
   // After
   const response = await axios.post(getFullApiUrl('auth/login'), formData, {...});
   ```

3. **Direct axios Usage**: Switched from using the pre-configured axios instance to direct axios calls with the full URL:
   ```typescript
   // Before (potentially problematic if baseURL isn't correct)
   logout: async (): Promise<void> => {
     await api.post('/logout');
     localStorage.removeItem(config.authTokenKey);
   },
   
   // After (explicitly uses the helper to ensure correct path)
   logout: async (): Promise<void> => {
     await axios.post(getFullApiUrl('logout'));
     localStorage.removeItem(config.authTokenKey);
   },
   ```

This approach ensures that all API calls will consistently include the `/api/v1` prefix, even if there are configuration issues or environment variables are not properly set.

## Common Issues & Solutions

1. **404 Not Found Errors**:
   - Ensure all API calls include the `/api/v1` prefix
   - ~~Check that collection endpoints have trailing slashes~~ The API now handles both formats with or without trailing slashes

2. **Authentication Errors (401 Unauthorized)**:
   - Most user management endpoints require admin authentication
   - For login, use form data format not JSON 
   - Include 'Content-Type': 'application/x-www-form-urlencoded' header for login
   - For authenticated endpoints, include the Bearer token in Authorization header

3. **Permission Errors (403 Forbidden)**:
   - Certain endpoints require admin privileges
   - Check that the user has `is_superuser=true` for admin-only endpoints

4. **Validation Errors (422 Unprocessable Entity)**:
   - Body parameters should use the format specified in the API documentation
   - For endpoints expecting embed=true format, use `{ parameter: value }`
   - When creating tickets, always include the required `status` field (use "open" as default)

5. **Method Not Allowed (405)**:
   - Check that you're using the correct HTTP method for the endpoint
   - The logout endpoint only accepts POST requests

6. **Redirect Issues (307 Temporary Redirect)**:
   - Some API frameworks redirect from paths without trailing slashes to paths with trailing slashes
   - Authentication headers may be lost during these redirects
   - Always use the exact path format specified in the documentation
   - For admin endpoints, explicitly set the Authorization header in every request

## Authentication Flow

1. **User Login**:
   - Send POST request to `/api/v1/auth/login` with form-encoded username/password
   - Receive JWT token in response
   - Store token in localStorage or secure cookie

2. **Authenticated Requests**:
   - Include token in Authorization header as `Bearer {token}`
   - For admin-only endpoints, ensure the user has admin privileges

3. **Token Expiration**:
   - JWT tokens expire after 1 hour
   - When token expires, re-authenticate by logging in again

## Frontend Date Handling

To prevent "Invalid Date" errors in the frontend:

1. **Safe Date Formatting**:
   ```typescript
   const formatDate = (dateString: string) => {
     if (!dateString) return "N/A";
     
     try {
       const date = new Date(dateString);
       // Check if date is valid
       if (isNaN(date.getTime())) {
         return "Invalid date";
       }
       return date.toLocaleString();
     } catch (error) {
       console.error("Error formatting date:", error);
       return "Invalid date";
     }
   };
   ```

2. **Common Date Issues**:
   - Missing date properties in API responses
   - Invalid date formats 
   - Timezone inconsistencies
   - `null` or `undefined` values

3. **Date Display Standards**:
   - Use `toLocaleDateString()` for date-only display
   - Use `toLocaleString()` for date and time display
   - Always handle potential invalid dates with try/catch

## Testing API Endpoints

Use the API path analyzer to diagnose issues:
```bash
python backend/scripts/tests/fix_api_paths.py
```

Run the comprehensive API test suite:
```bash
python backend/scripts/tests/api_test.py
```

Run the health tests:
```bash
python backend/scripts/tests/api_health_test.py
```

## Important Notes on 401/403 Responses

When the API path analyzer shows 401 responses for endpoints like `/api/v1/users/` and `/api/v1/users/{id}`, this is expected behavior for these protected endpoints. The 401 response indicates that authentication is required, not that the endpoint is broken.

To fix these issues:
1. Ensure proper login first
2. Use the JWT token with all user management requests
3. Make sure the user has admin privileges for admin-only endpoints 

## Backend API Improvements

### Trailing Slash Middleware

We've implemented a `TrailingSlashMiddleware` in the FastAPI application that automatically handles both trailing slash and non-trailing slash versions of all paths:

```python
class TrailingSlashMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Check if already handled to prevent recursion
        if request.scope.get("_trailing_slash_handled", False):
            return await call_next(request)
            
        # Process request normally first
        response = await call_next(request)
        
        # If 404, try alternative path
        if response.status_code == 404:
            path = request.url.path
            
            # Try adding/removing trailing slash
            if path.endswith('/'):
                request.scope["path"] = path[:-1]
            else:
                request.scope["path"] = f"{path}/"
                
            # Mark as handled and try again
            request.scope["_trailing_slash_handled"] = True
            response = await call_next(request)
                
        return response
```

This middleware ensures that if a client requests a path with or without a trailing slash, the server will attempt both formats and return the working version.

### Duplicate Endpoint Handlers

For critical endpoints, we've also added explicit duplicate handlers with and without trailing slashes:

```python
@router.get("/{ticket_id}")
async def get_ticket(...):
    # Original implementation

@router.get("/{ticket_id}/")
async def get_ticket_with_slash(...):
    return await get_ticket(...)
```

This approach provides several advantages:
1. **No Redirection**: Prevents 307 temporary redirects that can lose authentication headers
2. **Consistent Behavior**: Ensures both URL formats work exactly the same way
3. **Belt and Suspenders**: Even if the middleware fails, explicit endpoints will still work

### Frontend Integration

The frontend API client has been updated to use a consistent format, leveraging this new flexibility:

```typescript
// Helper function now doesn't need to worry about trailing slashes
export const getFullApiUrl = (endpoint: string): string => {
  // Base URL handling
  const base = config.apiUrl.endsWith('/api/v1') 
    ? config.apiUrl 
    : `${config.apiUrl}/api/v1`;
  
  // Clean endpoint
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint.substring(1) : endpoint;
  
  // Note: The backend handles both trailing slash and non-trailing slash paths identically
  return `${base}/${cleanEndpoint}`;
};
```

This ensures maximum compatibility between the frontend and backend regardless of trailing slashes.

## Recent Fixes (v1.1)

### 1. Login with Bad Password Fix

Previously, login attempts with incorrect passwords were sometimes still successful. We've fixed this issue by:

1. **Custom Login Handler**: Implemented a custom login endpoint that properly validates passwords
2. **Explicit Error Messages**: Now returns appropriate 401 Unauthorized responses with clear error messages
3. **Improved Security**: Ensures that only valid credentials can authenticate

Implementation:
```python
@router.post("/auth/login")
async def custom_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session)
):
    # Find user by email
    result = await session.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()
    
    # Check if user exists and is active
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    # Verify password
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
```

### 2. Admin User Role Management Fix 

The endpoint for promoting and demoting users to admin roles has been fixed:

1. **Enhanced Error Handling**: Added comprehensive logging and better error messages
2. **Frontend Integration**: Implemented proper API client methods in the frontend
3. **Security Checks**: Added validation to prevent admins from demoting themselves
4. **Edge Cases**: Improved handling of invalid user IDs and permission checks

Implementation:
```typescript
// Frontend API client
promoteUser: async (id: number, isAdmin: boolean): Promise<User> => {
  const token = getAuthToken();
  console.debug(`Setting user ${id} admin status to: ${isAdmin}`);
  const response = await axios.patch(getFullApiUrl(`users/${id}/promote`), 
    { is_superuser: isAdmin }, 
    {
      headers: {
        Authorization: `Bearer ${token}`
      }
    }
  );
  return response.data;
}
```

### 3. Forgot Password Implementation

A complete password reset flow has been implemented:

1. **Two-Step Process**: Request password reset token, then reset password with token
2. **Security Features**:
   - Same response message regardless of email existence (prevents email enumeration)
   - Token validation and minimum password length check
   - Password confirmation match validation in the frontend
3. **Developer Experience**: Development mode includes reset tokens in the response
4. **User Experience**: Clear feedback and error messages throughout the process

New endpoints:
```
POST /api/v1/auth/forgot-password  # Request reset token
POST /api/v1/auth/reset-password    # Reset password with token
```

### 4. User ID Type Consistency Fix

Fixed type inconsistency between frontend User interface and API methods:

1. **Type Standardization**: Updated all API methods to consistently use string type for user IDs
2. **Frontend/Backend Consistency**: Ensured alignment between frontend TypeScript types and backend data types
3. **Docker Build Fix**: Resolved TypeScript build errors in the Docker container

## Password Hashing Standardization (v1.2)

We've standardized all password hashing to use the same secure bcrypt algorithm throughout the system:

1. **Consistent Hashing**: All passwords now use bcrypt ($2b$) with standard security parameters
2. **Fixed Authentication Issues**: Previous login problems were caused by inconsistent hashing methods  
3. **Security Improvements**: Standardized on a single, strong hashing algorithm (bcrypt with 12 rounds)
4. **Password Reset**: Users with non-bcrypt hashes had their passwords reset (see admin for temporary credentials)

This standardization ensures that:
- Password verification works reliably for all users
- Security checks are consistent across the system
- Future password changes maintain the same secure format

If users experience login issues following this update, they may need to use the password reset functionality. 