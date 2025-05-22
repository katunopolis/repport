# Authentication Troubleshooting Guide

This document provides solutions to common authentication issues in the Repport application.

## Common Issues and Solutions

### User Registration Fails

#### Symptom: Registration returns 400 or 500 errors

**Possible causes and solutions:**

1. **User already exists**
   - Error message: "A user with this email already exists"
   - Solution: Use a different email address or recover the existing account

2. **Password validation fails**
   - Error message: "Password should be at least 8 characters"
   - Solution: Use a password with at least 8 characters

3. **Missing required fields**
   - Error message: "Email and password are required"
   - Solution: Ensure both email and password fields are provided

4. **JWT token generation fails**
   - Error message: "User created but unable to generate login token"
   - Solution: This is a server-side issue. The user account was created successfully, but you'll need to log in manually.

### Login Issues

#### Symptom: Login returns 401 Unauthorized

**Possible causes and solutions:**

1. **Incorrect credentials**
   - Error message: "Invalid email or password"
   - Solution: Check that you're using the correct email and password
   - Note: This has been fixed to properly validate passwords and return appropriate error messages

2. **Account is inactive**
   - Error message: "Invalid email or password"
   - Solution: Contact an administrator to activate your account

3. **JWT token issues**
   - If the login API returns a token but subsequent requests fail with 401 errors
   - Solution: Ensure you're correctly including the token in the Authorization header as "Bearer {token}"

### Password Reset Issues

#### Symptom: Unable to reset password

**Possible causes and solutions:**

1. **Invalid or expired token**
   - Error message: "Invalid or expired reset token"
   - Solution: Request a new password reset token
   
2. **Password requirements not met**
   - Error message: "Password must be at least 8 characters long"
   - Solution: Choose a password that is at least 8 characters long
   
3. **Password mismatch**
   - Error message: Client-side validation prevents submission
   - Solution: Ensure the new password and confirm password fields match

### Password Change Issues

#### Symptom: Unable to change password when logged in

**Possible causes and solutions:**

1. **Current password incorrect**
   - Error message: "Current password is incorrect"
   - Solution: Enter the correct current password for verification
   
2. **Password requirements not met**
   - Error message: "New password must be at least 8 characters long"
   - Solution: Choose a new password that is at least 8 characters long
   
3. **Password mismatch**
   - Error message: Client-side validation prevents submission
   - Solution: Ensure the new password and confirm password fields match

4. **Same password reuse**
   - Error message: "New password cannot be the same as your current password"
   - Solution: Choose a password different from your current one

5. **Session expired**
   - If changing password fails with authorization errors
   - Solution: Log out and log back in before trying to change your password

6. **Authentication token not included**
   - Error message: "401 Unauthorized" in API response
   - Technical details: Fixed in v1.3.1 to properly include authentication tokens in password change requests
   - Solution: Update to the latest version of the application

### Admin Role Management Issues

#### Symptom: Unable to promote/demote user to admin role

**Possible causes and solutions:**

1. **Insufficient permissions**
   - Error message: "Not enough permissions"
   - Solution: Only users with admin privileges can change user roles
   
2. **Self-demotion attempt**
   - Error message: "Cannot demote yourself from admin status"
   - Solution: Admins cannot demote themselves to prevent accidental lockouts
   
3. **Missing required fields**
   - Error message: "is_superuser is required"
   - Solution: Ensure the request includes the is_superuser field

## Technical Implementation Notes

### JWT Token Handling

When implementing JWT authentication:

1. The `write_token()` method from `JWTStrategy` is an async coroutine and must be awaited:

```python
# Correct implementation
strategy = auth_backend.get_strategy()
access_token = await strategy.write_token(user)

# Incorrect implementation (will cause errors)
strategy = auth_backend.get_strategy()
access_token = strategy.write_token(user)  # Missing await
```

2. The `write_token()` method expects a user object, not a dictionary:

```python
# Correct implementation
access_token = await strategy.write_token(user)

# Incorrect implementation (will cause errors)
access_token = await strategy.write_token({"id": user.id, "email": user.email})
```

### User Creation

For proper user creation:

1. Always check for existing users before creation to avoid database integrity errors:

```python
result = await session.execute(select(User).where(User.email == email))
existing_user = result.scalar_one_or_none()
if existing_user:
    # Handle duplicate user
```

2. Use `UserCreate` model to ensure all required fields are present:

```python
user_create = UserCreate(email=email, password=password)
user = await user_manager.create(user_create, safe=True)
```

3. Set `safe=True` when creating users to prevent privilege escalation vulnerabilities

## Reference Documentation

For more detailed information, refer to:

- [FastAPI Users Documentation](https://fastapi-users.github.io/fastapi-users/10.3/)
- [JWT Authentication in FastAPI](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)
- [API Endpoints Guide](./API_ENDPOINTS_GUIDE.md)

## Password Reset After System Update

If you're unable to log in after the v1.2 update, your account may have been affected by our password hashing standardization:

1. A system-wide update was performed to standardize all user passwords to use secure bcrypt hashing
2. Users with non-standard password hashes had their passwords automatically reset
3. Only system administrators have access to the temporary passwords

### What to do if you can't log in:

1. **First try**: Contact your system administrator who may have a temporary password for your account
2. **Alternative**: Use the "Forgot Password" feature on the login page to reset your password
3. **For administrators**: A file named `reset_passwords.txt` was generated during the update with temporary credentials for affected users

### Technical background:

The system previously used multiple password hashing algorithms (bcrypt and argon2), which caused inconsistent authentication behavior. We've standardized on bcrypt ($2b$) with 12 rounds to ensure consistent security and reliable authentication for all users. 