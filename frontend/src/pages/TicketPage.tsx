import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Typography, 
  Box,
  Paper,
  TextField,
  Button,
  Chip,
  CircularProgress,
  Alert,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import { useParams, useNavigate } from 'react-router-dom';
import { ticketsApi, Ticket, formatTicketId } from '../api/api';
import { getUserEmail } from '../config';

// Update the interface to use Record
interface RouteParams {
  id: string;
}

const TicketPage: React.FC = () => {
  // Fix the useParams hook usage
  const params = useParams<Record<string, string>>();
  const id = params.id;
  const [ticket, setTicket] = useState<Ticket | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [response, setResponse] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false); // Check admin status
  const [solveDialogOpen, setSolveDialogOpen] = useState(false);
  const [finalResponse, setFinalResponse] = useState('');
  const [solvingTicket, setSolvingTicket] = useState(false);
  const [updatingPublicStatus, setUpdatingPublicStatus] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchTicket = async () => {
      setLoading(true);
      setError(null);
      try {
        if (id) {
          const data = await ticketsApi.getTicket(parseInt(id));
          setTicket(data);
          
          // Check if user is admin - simple check for admin in email
          // This would be replaced with proper role checking in a production app
          const userEmail = getUserEmail() || '';
          setIsAdmin(userEmail.includes('admin'));
        }
      } catch (err) {
        console.error('Error fetching ticket:', err);
        setError('Failed to load ticket details. Please try again.');
        
        // For development - mock data when API fails
        setTicket({
          id: parseInt(id || '1'),
          title: "Sample ticket",
          description: "This is a sample description for development purposes.",
          status: "open",
          created_at: new Date().toISOString(),
          created_by: "user@example.com",
          is_public: false
        });
      } finally {
        setLoading(false);
      }
    };

    fetchTicket();
  }, [id]);

  const handleRespond = async () => {
    if (!response.trim() || !id) return;
    
    setSubmitting(true);
    setError(null);
    
    try {
      const updatedTicket = await ticketsApi.respondToTicket(parseInt(id), response);
      // Check if response is directly in the response data or if we need to refetch
      if (updatedTicket && typeof updatedTicket === 'object') {
        if (updatedTicket.response) {
          // Direct response in the returned data
          setTicket(updatedTicket);
        } else {
          // Refetch the ticket to get the updated data
          const refreshedTicket = await ticketsApi.getTicket(parseInt(id));
          setTicket(refreshedTicket);
        }
      } else {
        // Response doesn't contain ticket object, refetch
        const refreshedTicket = await ticketsApi.getTicket(parseInt(id));
        setTicket(refreshedTicket);
      }
      setResponse('');
    } catch (err) {
      console.error('Error responding to ticket:', err);
      setError('Failed to submit response. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };
  
  const handleOpenSolveDialog = () => {
    setSolveDialogOpen(true);
    setFinalResponse(ticket?.response || '');
  };
  
  const handleCloseSolveDialog = () => {
    setSolveDialogOpen(false);
  };
  
  const handleSolveTicket = async () => {
    if (!finalResponse.trim() || !id) return;
    
    setSolvingTicket(true);
    setError(null);
    
    try {
      const updatedTicket = await ticketsApi.solveTicket(parseInt(id), finalResponse);
      setTicket(updatedTicket);
      setSolveDialogOpen(false);
    } catch (err) {
      console.error('Error solving ticket:', err);
      setError('Failed to solve ticket. Please try again.');
    } finally {
      setSolvingTicket(false);
    }
  };

  const handleTogglePublic = async () => {
    if (!ticket || !id) return;
    
    setUpdatingPublicStatus(true);
    try {
      await ticketsApi.toggleTicketPublic(parseInt(id), !ticket.is_public);
      // Update the local state
      setTicket({...ticket, is_public: !ticket.is_public});
    } catch (err) {
      console.error('Error toggling public status:', err);
      setError('Failed to update ticket visibility. Please try again.');
    } finally {
      setUpdatingPublicStatus(false);
    }
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
      return date.toLocaleString();
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

  const canRespond = () => {
    return isAdmin && ticket && ticket.status !== 'closed';
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Box sx={{ mb: 3 }}>
        <Button variant="outlined" onClick={() => navigate(-1)}>
          Back
        </Button>
      </Box>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
          <CircularProgress />
        </Box>
      ) : error && !ticket ? (
        <Alert severity="error">{error}</Alert>
      ) : ticket ? (
        <Paper elevation={2} sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Box>
              <Typography variant="h5" sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}>
                <Chip 
                  label={formatTicketId(ticket.id)} 
                  color="primary" 
                  sx={{ mr: 1.5, fontWeight: 'bold' }}
                />
                {ticket.title}
                {ticket.is_public && (
                  <Chip 
                    label="Public" 
                    color="success" 
                    size="small" 
                    sx={{ ml: 1 }}
                  />
                )}
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Chip 
                label={ticket.status.replace('_', ' ')}
                color={getStatusColor(ticket.status)}
                sx={{ mr: 1 }}
              />
              {isAdmin && (
                <Button
                  variant="outlined"
                  size="small"
                  color={ticket.is_public ? "success" : "primary"}
                  onClick={handleTogglePublic}
                  disabled={updatingPublicStatus}
                  sx={{ mr: 1 }}
                >
                  {updatingPublicStatus ? 
                    <CircularProgress size={20} /> : 
                    (ticket.is_public ? "Make Private" : "Make Public")
                  }
                </Button>
              )}
              {isAdmin && ticket.status !== 'closed' && (
                <Button
                  variant="contained"
                  color="primary"
                  size="small"
                  onClick={handleOpenSolveDialog}
                >
                  Solve Ticket
                </Button>
              )}
            </Box>
          </Box>
          
          <Box sx={{ 
            display: 'flex', 
            bgcolor: 'grey.50', 
            p: 1, 
            borderRadius: 1,
            mb: 3
          }}>
            <Typography variant="body2" color="textSecondary">
              <strong>Created by:</strong> {ticket.created_by}
            </Typography>
            <Typography variant="body2" color="textSecondary" sx={{ ml: 3 }}>
              <strong>Date:</strong> {formatDate(ticket.created_at || new Date().toISOString())}
            </Typography>
          </Box>
          
          <Typography variant="body1" sx={{ mb: 3, whiteSpace: 'pre-wrap' }}>
            {ticket.description}
          </Typography>
          
          {ticket.response && (
            <>
              <Divider sx={{ my: 3 }} />
              <Typography variant="h6" sx={{ mb: 2 }}>
                Response {isAdmin && <Chip size="small" label="Admin" color="primary" sx={{ ml: 1 }} />}
              </Typography>
              <Paper 
                elevation={0} 
                sx={{ 
                  p: 2, 
                  bgcolor: 'grey.100',
                  borderLeft: '4px solid',
                  borderColor: 'primary.main'
                }}
              >
                <Typography 
                  variant="body1" 
                  sx={{ 
                    whiteSpace: 'pre-wrap',
                    fontWeight: 'medium'
                  }}
                >
                  {ticket.response}
                </Typography>
              </Paper>
            </>
          )}
          
          {canRespond() && (
            <>
              <Divider sx={{ my: 3 }} />
              <Typography variant="h6" sx={{ mb: 2 }}>
                {ticket.response ? 'Add Additional Response' : 'Add Response'}
              </Typography>
              
              {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
              
              <TextField
                fullWidth
                multiline
                rows={4}
                label="Your response"
                value={response}
                onChange={(e) => setResponse(e.target.value)}
                disabled={submitting}
                sx={{ mb: 2 }}
              />
              
              <Button 
                variant="contained" 
                onClick={handleRespond}
                disabled={!response.trim() || submitting}
              >
                {submitting ? <CircularProgress size={24} /> : 'Submit Response'}
              </Button>
            </>
          )}
        </Paper>
      ) : null}
      
      {/* Solve Ticket Dialog */}
      <Dialog 
        open={solveDialogOpen} 
        onClose={handleCloseSolveDialog}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Solve Ticket</DialogTitle>
        <DialogContent>
          <Typography variant="body2" sx={{ mb: 2 }}>
            Add a final response and close this ticket. Once closed, no further responses can be added.
          </Typography>
          <TextField
            fullWidth
            multiline
            rows={6}
            label="Final Response"
            value={finalResponse}
            onChange={(e) => setFinalResponse(e.target.value)}
            disabled={solvingTicket}
            sx={{ mb: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseSolveDialog} disabled={solvingTicket}>
            Cancel
          </Button>
          <Button 
            onClick={handleSolveTicket} 
            variant="contained" 
            color="success"
            disabled={!finalResponse.trim() || solvingTicket}
          >
            {solvingTicket ? <CircularProgress size={24} /> : 'Solve & Close Ticket'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default TicketPage; 