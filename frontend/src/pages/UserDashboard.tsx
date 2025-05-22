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
import LockIcon from '@mui/icons-material/Lock';
import { ticketsApi, Ticket, authApi, formatTicketId } from '../api/api';

const UserDashboard: React.FC = () => {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [newTicket, setNewTicket] = useState({ title: '', description: '' });
  const [createError, setCreateError] = useState<string | null>(null);
  const [createSuccess, setCreateSuccess] = useState(false);
  const [pwdDialogOpen, setPwdDialogOpen] = useState(false);
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [pwdChangeError, setPwdChangeError] = useState<string | null>(null);
  const [pwdChangeSuccess, setPwdChangeSuccess] = useState(false);
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

  // Password change handlers
  const handleOpenPasswordDialog = () => {
    setPwdDialogOpen(true);
    setCurrentPassword('');
    setNewPassword('');
    setConfirmPassword('');
    setPwdChangeError(null);
  };

  const handleClosePasswordDialog = () => {
    setPwdDialogOpen(false);
  };

  const handlePasswordChange = async () => {
    // Reset error state
    setPwdChangeError(null);
    
    // Validate inputs
    if (!currentPassword || !newPassword || !confirmPassword) {
      setPwdChangeError('All fields are required');
      return;
    }
    
    // Check if new passwords match
    if (newPassword !== confirmPassword) {
      setPwdChangeError('New passwords do not match');
      return;
    }
    
    // Check password length
    if (newPassword.length < 8) {
      setPwdChangeError('New password must be at least 8 characters long');
      return;
    }
    
    // Check if new password is the same as current password
    if (newPassword === currentPassword) {
      setPwdChangeError('New password cannot be the same as your current password');
      return;
    }
    
    setLoading(true);
    
    try {
      const response = await authApi.changePassword(currentPassword, newPassword);
      setPwdChangeSuccess(true);
      setPwdDialogOpen(false);
    } catch (err: any) {
      console.error('Password change error:', err);
      if (err.response && err.response.data && err.response.data.detail) {
        setPwdChangeError(err.response.data.detail);
      } else {
        setPwdChangeError('Failed to change password. Please try again.');
      }
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
          <Button
            variant="outlined"
            startIcon={<LockIcon />}
            onClick={handleOpenPasswordDialog}
            sx={{ mr: 1 }}
            disabled={loading}
          >
            Change Password
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
            label="Title"
            fullWidth
            margin="normal"
            required
            value={newTicket.title}
            onChange={(e) => setNewTicket({...newTicket, title: e.target.value})}
            disabled={loading}
          />
          <TextField
            label="Description"
            fullWidth
            margin="normal"
            required
            multiline
            rows={4}
            value={newTicket.description}
            onChange={(e) => setNewTicket({...newTicket, description: e.target.value})}
            disabled={loading}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog} disabled={loading}>
            Cancel
          </Button>
          <Button 
            onClick={handleSubmitTicket} 
            color="primary" 
            variant="contained" 
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : 'Submit Ticket'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Password Change Dialog */}
      <Dialog open={pwdDialogOpen} onClose={handleClosePasswordDialog} maxWidth="sm" fullWidth>
        <DialogTitle>Change Password</DialogTitle>
        <DialogContent>
          {pwdChangeError && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {pwdChangeError}
            </Alert>
          )}
          <TextField
            label="Current Password"
            type="password"
            fullWidth
            margin="normal"
            required
            value={currentPassword}
            onChange={(e) => setCurrentPassword(e.target.value)}
            disabled={loading}
          />
          <TextField
            label="New Password"
            type="password"
            fullWidth
            margin="normal"
            required
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            disabled={loading}
            helperText="Password must be at least 8 characters long"
          />
          <TextField
            label="Confirm New Password"
            type="password"
            fullWidth
            margin="normal"
            required
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            disabled={loading}
            error={confirmPassword !== '' && newPassword !== confirmPassword}
            helperText={confirmPassword !== '' && newPassword !== confirmPassword ? "Passwords don't match" : ""}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClosePasswordDialog} disabled={loading}>
            Cancel
          </Button>
          <Button 
            onClick={handlePasswordChange} 
            color="primary" 
            variant="contained" 
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : 'Change Password'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Success notification for password change */}
      <Snackbar
        open={pwdChangeSuccess}
        autoHideDuration={6000}
        onClose={() => setPwdChangeSuccess(false)}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert onClose={() => setPwdChangeSuccess(false)} severity="success">
          Password changed successfully
        </Alert>
      </Snackbar>

      {/* Success notification for ticket creation */}
      <Snackbar
        open={createSuccess}
        autoHideDuration={6000}
        onClose={() => setCreateSuccess(false)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={() => setCreateSuccess(false)} severity="success">
          Ticket created successfully
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default UserDashboard; 