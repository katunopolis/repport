import axios from 'axios';
import config, { getFullApiUrl, getAuthToken, removeAuthToken, removeUserEmail } from '../config';

// Create axios instance with default config
const api = axios.create({
  baseURL: config.apiUrl,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: config.requestTimeout,
});

// Add request interceptor for authentication
api.interceptors.request.use(
  (config) => {
    const token = getAuthToken();
    if (token) {
      // Log token for debugging
      console.debug('Using auth token:', token.substring(0, 10) + '...');
      config.headers.Authorization = `Bearer ${token}`;
    } else {
      console.debug('No auth token found');
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for debugging
api.interceptors.response.use(
  (response) => {
    console.debug(`API response [${response.status}]:`, response.config.url);
    return response;
  },
  (error) => {
    if (error.response) {
      console.error(`API error [${error.response.status}]:`, error.config.url, error.response.data);
      // Handle 401 errors
      if (error.response.status === 401) {
        console.warn('Authentication error - token may be invalid or expired');
      }
    } else if (error.request) {
      console.error('API request failed (no response):', error.config.url);
    } else {
      console.error('API request error:', error.message);
    }
    return Promise.reject(error);
  }
);

// Define interfaces for API data
export interface Ticket {
  id: number;
  title: string;
  description: string;
  status: 'open' | 'in_progress' | 'closed';
  created_by: string;
  created_at: string;
  response?: string;
}

// Helper function to format ticket ID with VR prefix
export const formatTicketId = (id: number): string => {
  return `VR${id.toString().padStart(6, '0')}`;
};

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface User {
  id: string;
  email: string;
  is_active: boolean;
  is_superuser: boolean;
  is_verified: boolean;
  created_at: string;
}

// API methods
export const authApi = {
  login: async (email: string, password: string): Promise<AuthResponse> => {
    // Create form data for login - FastAPIUsers expects form data not JSON
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);
    
    const response = await axios.post(getFullApiUrl('auth/login'), formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    });
    return response.data;
  },
  
  register: async (email: string, password: string): Promise<AuthResponse> => {
    try {
      // Use our custom signup endpoint instead of the FastAPI Users endpoint
      console.debug('Calling custom signup endpoint with', { email });
      const response = await axios.post(getFullApiUrl('auth/signup'), { 
        email, 
        password 
      });
      
      console.debug('Signup successful, token received');
      return response.data;
    } catch (error: any) {
      console.error('Registration error:', error);
      throw error;
    }
  },
  
  logout: async (): Promise<void> => {
    // Always explicitly include auth token to prevent auth issues
    const token = getAuthToken();
    try {
      await axios.post(getFullApiUrl('auth/logout'), {}, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      console.debug('Logout API call successful');
    } catch (error) {
      console.log('Logout endpoint error - this is expected for JWT tokens');
      // Continue with logout even if server endpoint fails
    } finally {
      // Always remove the token and user email from local storage regardless of server response
      removeAuthToken();
      removeUserEmail();
      console.debug('Token and user email removed from storage after logout');
    }
  },
  
  forgotPassword: async (email: string): Promise<{ message: string }> => {
    // Use body parameter with embed=true
    const response = await axios.post(getFullApiUrl('auth/forgot-password'), { email });
    return response.data;
  },
  
  resetPassword: async (token: string, new_password: string): Promise<{ message: string }> => {
    // Use body parameters with embed=true
    const response = await axios.post(getFullApiUrl('auth/reset-password'), { token, new_password });
    return response.data;
  },
  
  getCurrentUser: async () => {
    const response = await axios.get(getFullApiUrl('users/me'));
    return response.data;
  },
};

export const ticketsApi = {
  getTickets: async (): Promise<Ticket[]> => {
    // Always explicitly include auth token to prevent auth issues during redirects
    const token = getAuthToken();
    if (!token) {
      console.error('No authentication token found when trying to get tickets');
      throw new Error('Authentication required');
    }
    
    try {
      const response = await axios.get(getFullApiUrl('tickets'), {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      return response.data;
    } catch (error: any) {
      console.error('Failed to fetch tickets:', error.message);
      throw error;
    }
  },
  
  getTicket: async (id: number): Promise<Ticket> => {
    // Always explicitly include auth token to prevent auth issues during redirects
    const token = getAuthToken();
    if (!token) {
      console.error('No authentication token found when trying to get ticket');
      throw new Error('Authentication required');
    }
    
    try {
      const response = await axios.get(getFullApiUrl(`tickets/${id}`), {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      return response.data;
    } catch (error: any) {
      console.error(`Failed to fetch ticket ${id}:`, error.message);
      throw error;
    }
  },
  
  createTicket: async (ticket: Omit<Ticket, 'id' | 'created_at' | 'created_by'>): Promise<Ticket> => {
    // Always explicitly include auth token to prevent auth issues during redirects
    const token = getAuthToken();
    if (!token) {
      console.error('No authentication token found when trying to create ticket');
      throw new Error('Authentication required');
    }
    
    try {
      console.debug('Creating ticket with data:', ticket);
      const response = await axios.post(getFullApiUrl('tickets'), ticket, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      console.debug('Ticket created successfully');
      return response.data;
    } catch (error: any) {
      console.error('Failed to create ticket:', error.message);
      throw error;
    }
  },
  
  updateTicket: async (id: number, ticket: Partial<Ticket>): Promise<Ticket> => {
    // Always explicitly include auth token to prevent auth issues during redirects
    const token = getAuthToken();
    const response = await axios.patch(getFullApiUrl(`tickets/${id}`), ticket, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    return response.data;
  },
  
  respondToTicket: async (id: number, response: string): Promise<Ticket> => {
    // Always explicitly include auth token to prevent auth issues during redirects
    const token = getAuthToken();
    const data = { response };
    const resp = await axios.post(getFullApiUrl(`tickets/${id}/respond`), data, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    return resp.data;
  },
  
  updateTicketStatus: async (id: number, status: 'open' | 'in_progress' | 'closed'): Promise<{ status: string; message: string }> => {
    // Always explicitly include auth token to prevent auth issues during redirects
    const token = getAuthToken();
    const data = { status };
    const response = await axios.put(getFullApiUrl(`tickets/${id}/status`), data, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    return response.data;
  },
  
  solveTicket: async (id: number, finalResponse: string): Promise<Ticket> => {
    // Always explicitly include auth token to prevent auth issues during redirects
    const token = getAuthToken();
    const data = { 
      status: 'closed', 
      response: finalResponse 
    };
    
    try {
      console.debug('Solving ticket with final response:', finalResponse);
      const response = await axios.put(getFullApiUrl(`tickets/${id}/solve`), data, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      console.debug('Ticket solved successfully');
      return response.data;
    } catch (error: any) {
      console.error(`Failed to solve ticket ${id}:`, error.message);
      throw error;
    }
  },
};

export const userApi = {
  // Get all users (admin only)
  getUsers: async (): Promise<User[]> => {
    // Always explicitly include auth token for admin operations
    const token = getAuthToken();
    const response = await axios.get(getFullApiUrl('users/'), {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    return response.data;
  },
  
  // Get a specific user by ID (admin only)
  getUser: async (id: string): Promise<User> => {
    // Always explicitly include auth token for admin operations
    const token = getAuthToken();
    const response = await axios.get(getFullApiUrl(`users/${id}`), {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    return response.data;
  },
  
  // Create a new user (admin only)
  createUser: async (email: string, password: string, is_superuser: boolean = false): Promise<User> => {
    // Always explicitly include auth token for admin operations
    const token = getAuthToken();
    const response = await axios.post(getFullApiUrl('users/'), { 
      email, 
      password,
      is_superuser,
      is_active: true,
      is_verified: true
    }, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    return response.data;
  },
  
  // Update user properties (admin only)
  updateUser: async (id: string, userData: Partial<User>): Promise<User> => {
    // Always explicitly include auth token for admin operations
    const token = getAuthToken();
    const response = await axios.patch(getFullApiUrl(`users/${id}`), userData, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    return response.data;
  },
  
  // Promote or demote user to/from admin (admin only)
  promoteUser: async (id: string, isAdmin: boolean): Promise<User> => {
    // Always explicitly include auth token for admin operations
    const token = getAuthToken();
    const response = await axios.patch(getFullApiUrl(`users/${id}/promote`), { is_superuser: isAdmin }, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    return response.data;
  },
  
  // Delete a user (admin only)
  deleteUser: async (id: string): Promise<void> => {
    // Always explicitly include auth token for admin operations
    const token = getAuthToken();
    await axios.delete(getFullApiUrl(`users/${id}`), {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
  },
};

export default api; 