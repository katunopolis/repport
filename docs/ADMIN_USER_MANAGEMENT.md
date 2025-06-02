# Admin User Management

This document details how to manage admin users in the helpdesk ticketing system.

## Overview

The system provides two ways to manage admin users:
1. Command-line scripts for creating admin users during initial setup or when direct database access is needed
2. User management interface in the AdminDashboard for day-to-day user administration

## 1. Command-Line Admin User Creation

We provide two scripts to create admin users from the command line:
- `backend/scripts/create_admin.sh` for Unix/Linux/macOS systems
- `backend/scripts/create_admin.ps1` for Windows systems

Both scripts connect to the running Docker container and execute the Python script that creates or updates admin users.

### Prerequisites

- Docker containers must be running (`docker-compose up`)
- The backend container named `repport-backend` must be accessible

### Using create_admin.sh (Unix/Linux/macOS)

```bash
# Navigate to the scripts directory
cd backend/scripts

# Make the script executable (first time only)
chmod +x create_admin.sh

# Create an admin user
./create_admin.sh admin@example.com password123
```

### Using create_admin.ps1 (Windows PowerShell)

```powershell
# Navigate to the scripts directory
cd backend\scripts

# Create an admin user
.\create_admin.ps1 -Email admin@example.com -Password password123
```

### Behind the Scenes

These shell scripts:
1. Determine their location in the file system
2. Create a Python package structure in the Docker container
3. Copy the `create_admin.py` script to the container
4. Execute the script with the provided email and password
5. The script checks if the user exists
   - If the user doesn't exist, it creates a new admin user
   - If the user exists but isn't an admin, it updates them to admin status
   - If the user already exists as an admin, it notifies you

## 2. AdminDashboard User Management

The Admin Dashboard provides a comprehensive user management interface that allows:
- Viewing all users in the system
- Creating new users (both admin and regular)
- Editing existing users (change role and status)
- Deleting users
- Changing your own password securely

### Accessing the AdminDashboard

1. Log in with an admin user account
2. Navigate to the Admin Dashboard (typically available in the navigation menu)
3. Select the "User Management" tab

### Changing Your Password

1. From the Admin Dashboard, click the "Change Password" button in the top navigation bar
2. Enter your current password in the "Current Password" field
3. Enter your new password in the "New Password" field (must be at least 8 characters)
4. Confirm your new password in the "Confirm New Password" field
5. Click "Change Password" to update your password

Note that this follows the same security requirements as regular user password changes:
- Current password verification is required
- New password must be at least 8 characters long
- Passwords are securely hashed using bcrypt

> **Technical Note**: As of v1.3.1, the password change implementation was updated to properly include authentication tokens with requests, fixing 401 Unauthorized errors that could occur when attempting to change passwords.

### Creating a New User

1. Click the "Add User" button at the top of the User Management tab
2. Enter the user's email
3. Enter a password for the user (must be at least 8 characters)
4. Toggle the "Admin User" switch if the user should have admin privileges
5. Click "Create" to add the user

### Editing a User

1. Find the user in the user list
2. Click the edit (pencil) icon for that user
3. You can modify:
   - Admin status (toggle to grant or revoke admin privileges)
   - Active status (toggle to activate or deactivate the user)
4. Click "Update" to save changes

### Promoting/Demoting Admin Status

The system now includes a dedicated API endpoint for managing user admin privileges:

```
PATCH /api/v1/users/{user_id}/promote
```

This endpoint accepts a JSON body with:
```json
{
  "is_superuser": true|false
}
```

Example using curl (Unix/Linux/macOS):
```bash
curl -X PATCH "http://localhost:8000/api/v1/users/3/promote" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"is_superuser": true}'
```

Example using PowerShell:
```powershell
$headers = @{
    "Authorization" = "Bearer YOUR_JWT_TOKEN"
    "Content-Type" = "application/json"
}
$body = @{
    "is_superuser" = $true
} | ConvertTo-Json

Invoke-RestMethod -Method PATCH -Uri "http://localhost:8000/api/v1/users/3/promote" -Headers $headers -Body $body
```

> **Technical Note**: User IDs are represented as strings in the frontend interface and API methods, but as integers in the backend. The API endpoints handle this conversion automatically.

The promote endpoint includes several important features:

- **Role-Based Access Control**: Only existing admin users can promote/demote other users
- **First User Exception**: The first user in the system is automatically granted admin privileges
- **Self-Protection**: Admins cannot demote themselves, preventing accidental loss of admin access
- **Audit Logging**: All promotion/demotion attempts are logged with the requesting user's information
- **Idempotent Operations**: Requesting the same role status multiple times is safe
- **Clear Error Messages**: Failed operations return descriptive error messages

The frontend uses this endpoint to reliably change user roles. Key improvements include:

- **Enhanced Logging**: Better visibility into role changes for audit purposes
- **Fixed Permission Validation**: Properly checks that only admins can change roles
- **Self-Protection Logic**: Prevents admins from accidentally demoting themselves
- **Improved Error Handling**: Clear error messages when operations fail

### Deleting a User

1. Find the user in the user list 
2. Click the delete (trash) icon for that user
3. Confirm the deletion in the confirmation dialog

**Warning**: User deletion is permanent and cannot be undone.

## 3. Error Handling and Validation

The system includes the following validations for user management:

### Password Requirements
- Passwords must be at least 8 characters long
- Additional password complexity requirements can be configured in `backend/app/api/auth.py` in the `validate_password` method

### Email Validation
- Emails must be in a valid format
- Emails must be unique in the system
- The system will prevent duplicate email registrations with a clear error message

### Self-Protection
- Admin users cannot demote themselves from admin status
- Admin users cannot delete their own accounts

## Security Considerations

- Admin users have full access to the system, including user management
- Create admin users only for trusted individuals
- Use strong passwords for admin accounts
- Consider implementing additional security measures like:
  - IP restriction for admin access
  - Multi-factor authentication (planned feature)
  - Admin action logging (planned feature)

## Troubleshooting

### Command-Line Scripts

- **Error**: "Backend container is not running"
  - Make sure Docker containers are running with `docker-compose up`
  - Check container name with `docker ps`

- **Error**: "Permission denied"
  - For `create_admin.sh`, make sure it's executable: `chmod +x create_admin.sh`

### AdminDashboard

- **Issue**: Can't see the User Management tab
  - Verify you're logged in with an admin account
  - Check browser console for errors
  - Try logging out and back in

- **Issue**: User creation fails
  - Ensure email is unique (not already in use)
  - Password must meet minimum requirements
  - Check browser console and backend logs for specific errors 

- **Issue**: "User already exists" error
  - The system prevents creating users with duplicate emails
  - Use a different email address or recover access to the existing account

For additional authentication troubleshooting, see [AUTH_TROUBLESHOOTING.md](./AUTH_TROUBLESHOOTING.md). 