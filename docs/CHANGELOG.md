# Changelog

All notable changes to the Repport project will be documented in this file.

## [1.3.2] - 2025-05-22

### Security
- **Password Policy**: Enhanced password security by preventing users from reusing their current password when changing passwords
- Added both server-side and client-side validation to enforce this new password policy
- Updated documentation to reflect these security improvements

### Implementation Details
- Added check in backend API endpoint to validate new password is different from current password
- Added client-side validation in both regular user and admin user interfaces
- Updated error handling to provide clear feedback when password reuse is attempted

### Documentation
- Updated `API_ENDPOINTS_GUIDE.md` with information about the new error case
- Added password reuse prevention to `AUTH_TROUBLESHOOTING.md` troubleshooting guide
- Updated `SECURITY.md` with the new password policy requirements

## [1.3.1] - 2025-05-22

### Fixed
- **Authentication**: Fixed 401 Unauthorized errors when changing passwords by properly including authentication tokens in requests
- **API Client**: Updated `changePassword` and `getCurrentUser` methods in the frontend API client to explicitly include auth tokens in requests
- **Security**: Improved consistency in authentication handling across all secure API endpoints

### Documentation
- Added technical notes about authentication requirements for the password change feature
- Updated troubleshooting guide with information about the authentication fix
- Updated API documentation to clarify authentication requirements for password-related endpoints 