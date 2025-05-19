import React, { useState } from 'react';
import { 
  Container, 
  Paper, 
  Typography, 
  TextField, 
  Button, 
  Box,
  Grid,
  Link,
  CircularProgress,
  Alert
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { authApi } from '../api/api';
import config from '../config';

const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await authApi.login(email, password);
      
      // Save token to localStorage
      localStorage.setItem(config.authTokenKey, response.access_token);
      
      // Check if user is admin (in a real app this would be determined by user role)
      if (email.includes('admin')) {
        navigate('/admin');
      } else {
        navigate('/dashboard');
      }
    } catch (err: any) {
      console.error('Login error:', err);
      if (err.response && err.response.status === 401) {
        setError('Invalid email or password. Please try again.');
      } else {
        setError('Login failed. Please try again later.');
        
        // For development only: navigate even when API is not available
        console.warn('DEV MODE: Navigating despite login failure');
        if (email.includes('admin')) {
          navigate('/admin');
        } else {
          navigate('/dashboard');
        }
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="sm" sx={{ mt: 8 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h4" component="h1" align="center" gutterBottom>
          Helpdesk Login
        </Typography>
        
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        
        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
          <TextField
            label="Email"
            type="email"
            fullWidth
            margin="normal"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            disabled={loading}
          />
          
          <TextField
            label="Password"
            type="password"
            fullWidth
            margin="normal"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            disabled={loading}
          />
          
          <Button
            type="submit"
            fullWidth
            variant="contained"
            color="primary"
            sx={{ mt: 3, mb: 2 }}
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : 'Sign In'}
          </Button>
          
          <Grid container justifyContent="space-between">
            <Grid item>
              <Link href="#" variant="body2">
                Forgot password?
              </Link>
            </Grid>
            <Grid item>
              <Link href="#" variant="body2">
                Don't have an account? Sign Up
              </Link>
            </Grid>
          </Grid>
        </Box>
      </Paper>
    </Container>
  );
};

export default LoginPage; 