# Password Policy and Security

This document outlines the password policies and security measures implemented in the Repport application.

## Password Requirements

All passwords in the Repport system must meet the following criteria:

1. **Minimum Length**: Passwords must be at least 8 characters long
2. **Password Reuse**: Users cannot reuse their current password when changing passwords (added in v1.3.2)

## Password Change Workflow

The password change process follows these steps:

1. User navigates to the password change dialog from their dashboard
2. User enters their current password (required for verification)
3. User enters their new password and confirmation
4. System validates that:
   - Current password is correct
   - New password meets minimum length requirements
   - New password is different from current password
   - New password and confirmation match
5. If all validation passes, the password is updated

## Validation Implementation

### Client-Side Validation

The frontend implements these checks in the password change dialogs:

```typescript
// Check if new password is the same as current password
if (newPassword === currentPassword) {
  setPwdChangeError('New password cannot be the same as your current password');
  return;
}
```

### Server-Side Validation

The backend enforces these password requirements in the API:

```python
# Prevent reusing the same password
if verify_password(new_password, current_user.hashed_password):
    logger.warning(f"Password change failed: New password is same as current password for user ID {current_user.id}")
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="New password cannot be the same as your current password",
    )
```

## Error Messages

When password validation fails, users see one of these specific error messages:

| Validation Failure | Error Message |
|-------------------|---------------|
| Missing fields | "All fields are required" |
| Passwords don't match | "New passwords do not match" |
| Too short | "New password must be at least 8 characters long" |
| Same as current | "New password cannot be the same as your current password" |
| Current password incorrect | "Current password is incorrect" |

## Password Storage

All passwords are securely stored using bcrypt with a cost factor of 12. This provides a good balance between security and performance.

## Password Reset vs Password Change

There are two distinct flows for updating passwords:

1. **Password Change**: For authenticated users who know their current password
   - Requires current password verification
   - Enforces all password policy rules including reuse prevention
   
2. **Password Reset**: For users who have forgotten their password
   - Requires a valid reset token (typically sent via email)
   - Does not enforce the password reuse prevention (since they don't know their current password)
   - Still enforces minimum length requirements

## Security Considerations

These password policies help protect against:

1. Weak passwords
2. Password reuse attacks
3. Unauthorized password changes
4. Brute force attempts

## Changelog

**v1.3.2**
- Added password reuse prevention to strengthen security
- Implemented both client-side and server-side validation
- Updated documentation to reflect new requirements 