import React from 'react';
import { 
  Container, 
  Typography, 
  Box, 
  Button, 
  Paper 
} from '@mui/material';
import { useNavigate } from 'react-router-dom';

const NotFoundPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <Container maxWidth="sm" sx={{ mt: 8, textAlign: 'center' }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h1" sx={{ mb: 2, fontSize: '6rem', fontWeight: 'bold', color: '#d32f2f' }}>
          404
        </Typography>
        
        <Typography variant="h4" sx={{ mb: 3 }}>
          Page Not Found
        </Typography>
        
        <Typography variant="body1" sx={{ mb: 4 }}>
          The page you are looking for doesn't exist or has been moved.
        </Typography>
        
        <Box>
          <Button 
            variant="contained" 
            color="primary" 
            onClick={() => navigate('/')}
            sx={{ mr: 2 }}
          >
            Go to Login
          </Button>
          
          <Button 
            variant="outlined" 
            onClick={() => navigate(-1)}
          >
            Go Back
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};

export default NotFoundPage; 