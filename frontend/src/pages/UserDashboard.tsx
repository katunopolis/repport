import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Typography, 
  Button, 
  Box,
  Paper,
  Divider,
  List,
  ListItem,
  ListItemText,
  Chip,
  IconButton,
  CircularProgress
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import AddIcon from '@mui/icons-material/Add';
import RefreshIcon from '@mui/icons-material/Refresh';
import LogoutIcon from '@mui/icons-material/Logout';
import { ticketsApi, Ticket, authApi } from '../api/api';

const UserDashboard: React.FC = () => {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  // Fetch tickets from API
  const fetchTickets = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await ticketsApi.getTickets();
      setTickets(data);
    } catch (err) {
      console.error('Error fetching tickets:', err);
      setError('Failed to load tickets. Please try again.');
      // Fallback to mock data for development/testing
      setTickets([
        { id: 1, title: "Can't login to my account", status: "open", created_at: "2025-05-15T10:00:00Z", created_by: "user@example.com", description: "" },
        { id: 2, title: "Need to reset my password", status: "closed", created_at: "2025-05-10T14:30:00Z", created_by: "user@example.com", description: "" },
        { id: 3, title: "Feature request: dark mode", status: "in_progress", created_at: "2025-05-18T09:15:00Z", created_by: "user@example.com", description: "" },
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTickets();
  }, []);

  const handleCreateTicket = () => {
    // TODO: Open ticket creation dialog or navigate to ticket creation page
    console.log('Create ticket clicked');
  };

  const handleLogout = async () => {
    setLoading(true);
    try {
      await authApi.logout();
      navigate('/');
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleTicketClick = (id: number) => {
    navigate(`/ticket/${id}`);
  };

  // Helper function to format date
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };

  // Helper function to get status color
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'open':
        return 'primary';
      case 'in_progress':
        return 'warning';
      case 'closed':
        return 'success';
      default:
        return 'default';
    }
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          My Support Tickets
        </Typography>
        <Box>
          <IconButton onClick={fetchTickets} disabled={loading} sx={{ mr: 1 }}>
            <RefreshIcon />
          </IconButton>
          <Button 
            variant="contained" 
            startIcon={<AddIcon />}
            onClick={handleCreateTicket}
            sx={{ mr: 1 }}
          >
            New Ticket
          </Button>
          <IconButton onClick={handleLogout} color="primary" disabled={loading}>
            <LogoutIcon />
          </IconButton>
        </Box>
      </Box>

      {error && (
        <Paper elevation={2} sx={{ p: 2, mb: 3, bgcolor: '#fdeded' }}>
          <Typography color="error">{error}</Typography>
        </Paper>
      )}

      <Paper elevation={2}>
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress />
          </Box>
        ) : (
          <List>
            {tickets.length === 0 ? (
              <ListItem>
                <ListItemText 
                  primary="No tickets found" 
                  secondary="Click the 'New Ticket' button to create a support request." 
                />
              </ListItem>
            ) : (
              tickets.map((ticket, index) => (
                <React.Fragment key={ticket.id}>
                  {index > 0 && <Divider />}
                  <ListItem 
                    button 
                    onClick={() => handleTicketClick(ticket.id)}
                    sx={{ py: 2 }}
                  >
                    <ListItemText 
                      primary={ticket.title} 
                      secondary={`Created on ${formatDate(ticket.created_at)}`} 
                    />
                    <Chip 
                      label={ticket.status.replace('_', ' ')}
                      color={getStatusColor(ticket.status) as any}
                      size="small"
                    />
                  </ListItem>
                </React.Fragment>
              ))
            )}
          </List>
        )}
      </Paper>
    </Container>
  );
};

export default UserDashboard; 