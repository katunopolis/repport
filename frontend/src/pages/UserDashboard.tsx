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
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  Snackbar
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import AddIcon from '@mui/icons-material/Add';
import RefreshIcon from '@mui/icons-material/Refresh';
import LogoutIcon from '@mui/icons-material/Logout';
import { ticketsApi, Ticket, authApi, formatTicketId } from '../api/api';

const UserDashboard: React.FC = () => {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [newTicket, setNewTicket] = useState({ title: '', description: '' });
  const [createError, setCreateError] = useState<string | null>(null);
  const [createSuccess, setCreateSuccess] = useState(false);
  const navigate = useNavigate();

  // Fetch tickets from API
  const fetchTickets = async () => {
    setLoading(true);
    setError(null);
    try {
      console.debug('Fetching tickets...');
      const data = await ticketsApi.getTickets();
      console.debug('Tickets fetched:', data.length);
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
    setDialogOpen(true);
    setNewTicket({ title: '', description: '' });
    setCreateError(null);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
  };

  const handleSubmitTicket = async () => {
    if (!newTicket.title.trim() || !newTicket.description.trim()) {
      setCreateError('Please fill in all fields');
      return;
    }

    setLoading(true);
    setCreateError(null);
    
    try {
      console.debug('Creating new ticket with data:', newTicket);
      
      // Ensure we're explicitly including the status field
      const result = await ticketsApi.createTicket({
        title: newTicket.title.trim(),
        description: newTicket.description.trim(),
        status: 'open'
      });
      
      console.debug('Ticket created successfully:', result);
      setDialogOpen(false);
      setCreateSuccess(true);
      
      // Refresh ticket list
      fetchTickets();
    } catch (err: any) {
      console.error('Error creating ticket:', err);
      
      // More detailed error message
      if (err.response && err.response.data && err.response.data.detail) {
        setCreateError(`Failed to create ticket: ${err.response.data.detail}`);
      } else {
        setCreateError('Failed to create ticket. Please try again.');
      }
    } finally {
      setLoading(false);
    }
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
    if (!dateString) return "N/A";
    
    try {
      const date = new Date(dateString);
      // Check if date is valid
      if (isNaN(date.getTime())) {
        return "Invalid date";
      }
      return date.toLocaleDateString();
    } catch (error) {
      console.error("Error formatting date:", error);
      return "Invalid date";
    }
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
            disabled={loading}
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
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <Chip 
                            label={formatTicketId(ticket.id)} 
                            size="small" 
                            color="primary" 
                            sx={{ mr: 1.5, fontWeight: 'medium' }}
                          />
                          {ticket.title}
                        </Box>
                      }
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

      {/* Create Ticket Dialog */}
      <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Support Ticket</DialogTitle>
        <DialogContent>
          {createError && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {createError}
            </Alert>
          )}
          <TextField
            autoFocus
            margin="dense"
            id="title"
            label="Title"
            type="text"
            fullWidth
            variant="outlined"
            value={newTicket.title}
            onChange={(e) => setNewTicket({ ...newTicket, title: e.target.value })}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            id="description"
            label="Description"
            type="text"
            fullWidth
            multiline
            rows={4}
            variant="outlined"
            value={newTicket.description}
            onChange={(e) => setNewTicket({ ...newTicket, description: e.target.value })}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog} disabled={loading}>
            Cancel
          </Button>
          <Button 
            onClick={handleSubmitTicket} 
            variant="contained" 
            color="primary"
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : 'Submit'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Success notification */}
      <Snackbar
        open={createSuccess}
        autoHideDuration={6000}
        onClose={() => setCreateSuccess(false)}
        message="Ticket created successfully"
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      />
    </Container>
  );
};

export default UserDashboard; 