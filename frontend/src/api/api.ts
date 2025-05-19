import axios from 'axios';
import config from '../config';

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
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
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
    const response = await api.post('/auth/login', { email, password });
    return response.data;
  },
  
  register: async (email: string, password: string): Promise<AuthResponse> => {
    const response = await api.post('/auth/register', { email, password });
    return response.data;
  },
  
  logout: async (): Promise<void> => {
    await api.post('/auth/logout');
    localStorage.removeItem(config.authTokenKey);
  },
  
  getCurrentUser: async () => {
    const response = await api.get('/users/me');
    return response.data;
  },
};

export const ticketsApi = {
  getTickets: async (): Promise<Ticket[]> => {
    const response = await api.get('/tickets');
    return response.data;
  },
  
  getTicket: async (id: number): Promise<Ticket> => {
    const response = await api.get(`/tickets/${id}`);
    return response.data;
  },
  
  createTicket: async (ticket: Omit<Ticket, 'id' | 'created_at' | 'created_by'>): Promise<Ticket> => {
    const response = await api.post('/tickets', ticket);
    return response.data;
  },
  
  updateTicket: async (id: number, ticket: Partial<Ticket>): Promise<Ticket> => {
    const response = await api.patch(`/tickets/${id}`, ticket);
    return response.data;
  },
  
  respondToTicket: async (id: number, response: string): Promise<Ticket>