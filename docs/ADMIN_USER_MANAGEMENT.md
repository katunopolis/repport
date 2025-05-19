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

### Accessing the AdminDashboard

1. Log in with an admin user account
2. Navigate to the Admin Dashboard (typically available in the navigation menu)
3. Select the "User Management" tab

### Creating a New User

1. Click the "Add User" button at the top of the User Management tab
2. Enter the user's email
3. Enter a password for the user
4. Toggle the "Admin User" switch if the user should have admin privileges
5. Click "Create" to add the user

### Editing a User

1. Find the user in the user list
2. Click the edit (pencil) icon for that user
3. You can modify:
   - Admin status (toggle to grant or revoke admin privileges)
   - Active status (toggle to activate or deactivate the user)
4. Click "Update" to save changes

### Deleting a User

1. Find the user in the user list 
2. Click the delete (trash) icon for that user
3. Confirm the deletion in the confirmation dialog

**Warning**: User deletion is permanent and cannot be undone.

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