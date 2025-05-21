// Application configuration
const config = {
  // API URL - ensure it includes the /api/v1 prefix
  apiUrl: process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1',
  
  // Default request timeout in milliseconds
  requestTimeout: 10000,
  
  // Auth token storage key
  authTokenKey: 'auth_token',
  
  // User email storage key
  userEmailKey: 'user_email',
};

// Helper to get the authentication token
export const getAuthToken = (): string | null => {
  return localStorage.getItem(config.authTokenKey);
};

// Helper to set the authentication token
export const setAuthToken = (token: string): void => {
  localStorage.setItem(config.authTokenKey, token);
};

// Helper to remove the authentication token
export const removeAuthToken = (): void => {
  localStorage.removeItem(config.authTokenKey);
};

// Helper to get the user email
export const getUserEmail = (): string | null => {
  return localStorage.getItem(config.userEmailKey);
};

// Helper to set the user email
export const setUserEmail = (email: string): void => {
  localStorage.setItem(config.userEmailKey, email);
};

// Helper to remove the user email
export const removeUserEmail = (): void => {
  localStorage.removeItem(config.userEmailKey);
};

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

export default config; 