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
   - Error message: "LOGIN_BAD_CREDENTIALS"
   - Solution: Check that you're using the correct email and password

2. **Account is inactive**
   - Error message: "LOGIN_USER_NOT_VERIFIED"
   - Solution: Contact an administrator to activate your account

3. **JWT token issues**
   - If the login API returns a token but subsequent requests fail with 401 errors
   - Solution: Ensure you're correctly including the token in the Authorization header as "Bearer {token}"

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