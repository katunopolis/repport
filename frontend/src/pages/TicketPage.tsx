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
  Divider
} from '@mui/material';
import { useParams, useNavigate } from 'react-router-dom';
import { ticketsApi, Ticket } from '../api/api';

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
  const navigate = useNavigate();

  useEffect(() => {
    const fetchTicket = async () => {
      setLoading(true);
      setError(null);
      try {
        if (id) {
          const data = await ticketsApi.getTicket(parseInt(id));
          setTicket(data);
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
          created_by: "user@example.com"
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
      setTicket(updatedTicket);
      setResponse('');
    } catch (err) {
      console.error('Error responding to ticket:', err);
      setError('Failed to submit response. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  // Helper function to format date
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString();
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
            <Typography variant="h5">{ticket.title}</Typography>
            <Chip 
              label={ticket.status.replace('_', ' ')}
              color={getStatusColor(ticket.status) as any}
            />
          </Box>
          
          <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
            Created by {ticket.created_by} on {formatDate(ticket.created_at)}
          </Typography>
          
          <Typography variant="body1" sx={{ mb: 3, whiteSpace: 'pre-wrap' }}>
            {ticket.description}
          </Typography>
          
          {ticket.response && (
            <>
              <Divider sx={{ my: 3 }} />
              <Typography variant="h6" sx={{ mb: 2 }}>Response</Typography>
              <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                {ticket.response}
              </Typography>
            </>
          )}
          
          {!ticket.response && (
            <>
              <Divider sx={{ my: 3 }} />
              <Typography variant="h6" sx={{ mb: 2 }}>Add Response</Typography>
              
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
    </Container>
  );
};

export default TicketPage; 