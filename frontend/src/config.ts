// Application configuration
const config = {
  // API URL - use environment variable or default to localhost
  apiUrl: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  
  // Default request timeout in milliseconds
  requestTimeout: 10000,
  
  // Auth token storage key
  authTokenKey: 'auth_token',
};

export default config; 