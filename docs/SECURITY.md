# Security Guidelines for Repport

This document outlines important security considerations for working with the Repport codebase.

## Environment Variables

All sensitive configuration including:
- Database credentials
- API keys
- Secret keys
- Passwords

Should be stored in environment variables, never hardcoded in the codebase.

### Setting Up Environment Variables

1. Create a `.env` file in the backend directory:
   ```
   # Core Settings
   ENVIRONMENT=development
   SECRET_KEY=your_generated_secret_key_here
   
   # Database Settings
   DATABASE_URL=sqlite+aiosqlite:///./data/helpdesk.db
   
   # Email Settings
   MAIL_PASSWORD=your_resend_api_key_here
   MAIL_FROM=noreply@yourdomain.com
   
   # CORS Settings
   BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8000
   
   # Test Settings (only for development)
   TEST_ADMIN_PASSWORD=test_password_only_for_tests
   TEST_USER_PASSWORD=test_password_only_for_tests
   DEFAULT_DEV_PASSWORD=development_only_password
   ```

2. Create a `.env.local` file in the frontend directory:
   ```
   REACT_APP_API_URL=http://localhost:8000/api/v1
   REACT_APP_AUTH_TOKEN_KEY=auth_token
   ```

3. **Never commit these .env files to your repository.**

## Testing Credentials

For testing purposes, use placeholder or dummy credentials. The testing framework reads actual test credentials from environment variables, so no real credentials should be in the code.

Example:
```python
# Good practice
admin_password = os.getenv("TEST_ADMIN_PASSWORD", "placeholder_password")

# Bad practice
admin_password = "actual_password123"  # Never do this!
```

## Production Considerations

1. Always generate strong, unique secret keys for production
2. Set the ENVIRONMENT variable to "production" to enable stricter security checks
3. Use a proper database (PostgreSQL) rather than SQLite
4. Enable HTTPS and proper security headers
5. Regularly rotate credentials

## Password Storage

All user passwords are stored using bcrypt with a cost factor of 12. Never store plaintext passwords anywhere in the codebase.

## Password Management

### Password Policy and Requirements
- Minimum password length: 8 characters
- Password reuse prevention: Users cannot change their password to their current password
- Secure storage: All passwords are stored using bcrypt with a cost factor of 12

### Password Changes
- Authenticated users can change their password using the `/api/v1/users/me/change-password` endpoint
- Current password verification is required before allowing password changes
- Password requirements include a minimum length of 8 characters
- Users cannot reuse their current password as their new password
- After changing a password, previous authentication tokens remain valid until they expire
- The web interface provides password change functionality:
  - Regular users: Via the "Change Password" button in the User Dashboard
  - Admin users: Via the "Change Password" button in the Admin Dashboard

### Password Reuse Prevention
As of v1.3.2, the system implements both server-side and client-side validation to prevent users from reusing their current password when changing passwords:

- **Server-side validation**: The backend API verifies that the new password hash is different from the current password hash
- **Client-side validation**: The user interface prevents submission if the new password matches the current password
- **Error handling**: Clear error messages are provided to guide users when password reuse is detected

### Password Resets
- Users who have forgotten their password can request a reset via the `/api/v1/auth/forgot-password` endpoint
- Reset tokens are securely generated and should be sent to the user's registered email
- Reset tokens are single-use and invalidated after password change

## Report Security Issues

If you discover any security issues, please report them to [security@example.com](mailto:security@example.com). 