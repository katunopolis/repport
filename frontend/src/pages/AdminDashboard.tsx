import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Typography, 
  Button, 
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import RefreshIcon from '@mui/icons-material/Refresh';
import LogoutIcon from '@mui/icons-material/Logout';
import VisibilityIcon from '@mui/icons-material/Visibility';

// Mock data for tickets
const mockTickets = [
  { 
    id: 1, 
    title: "Can't login to my account", 
    status: "open", 
    created_at: "2025-05-15T10:00:00Z",
    created_by: "john.doe@example.com" 
  },
  { 
    id: 2, 
    title: "Need to reset my password", 
    status: "closed", 
    created_at: "2025-05-10T14:30:00Z",
    created_by: "jane.smith@example.com" 
  },
  { 
    id: 3, 
    title: "Feature request: dark mode", 
    status: "in_progress", 
    created_at: "2025-05-18T09:15:00Z",
    created_by: "mike.johnson@example.com" 
  },
  { 
    id: 4, 
    title: "Error when uploading files", 
    status: "open", 
    created_at: "2025-05-19T11:20:00Z",
    created_by: "sarah.wilson@example.com" 
  },
];

const AdminDashboard: React.FC = () => {
  const [tickets, setTickets] = useState(mockTickets);
  const [loading, setLoading] = useState(false);
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const navigate = useNavigate();

  // Simulate fetching tickets
  const fetchTickets = () => {
    setLoading(true);
    // TODO: Replace with actual API call
    setTimeout(() => {
      setTickets(mockTickets);
      setLoading(false);
    }, 500);
  };

  useEffect(() => {
    fetchTickets();
  }, []);

  const handleLogout = () => {
    // TODO: Implement logout logic
    navigate('/');
  };

  const handleTicketClick = (id: number) => {
    navigate(`/ticket/${id}`);
  };

  const handleStatusChange = (event: SelectChangeEvent) => {
    setStatusFilter(event.target.value);
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

  // Filter tickets based on status
  const filteredTickets = statusFilter === 'all' 
    ? tickets 
    : tickets.filter(ticket => ticket.status === statusFilter);

  return (
    <Container maxWidth="lg" sx={{ mt: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Admin Dashboard
        </Typography>
        <Box>
          <IconButton onClick={fetchTickets} disabled={loading} sx={{ mr: 1 }}>
            <RefreshIcon />
          </IconButton>
          <IconButton onClick={handleLogout} color="primary">
            <LogoutIcon />
          </IconButton>
        </Box>
      </Box>

      <Box sx={{ mb: 3 }}>
        <FormControl sx={{ minWidth: 200 }}>
          <InputLabel id="status-filter-label">Status Filter</InputLabel>
          <Select
            labelId="status-filter-label"
            id="status-filter"
            value={statusFilter}
            label="Status Filter"
            onChange={handleStatusChange}
          >
            <MenuItem value="all">All Tickets</MenuItem>
            <MenuItem value="open">Open</MenuItem>
            <MenuItem value="in_progress">In Progress</MenuItem>
            <MenuItem value="closed">Closed</MenuItem>
          </Select>
        </FormControl>
      </Box>

      <TableContainer component={Paper} elevation={2}>
        <Table sx={{ minWidth: 650 }}>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Title</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Created By</TableCell>
              <TableCell>Date</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredTickets.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} align="center">
                  No tickets found
                </TableCell>
              </TableRow>
            ) : (
              filteredTickets.map((ticket) => (
                <TableRow key={ticket.id}>
                  <TableCell>{ticket.id}</TableCell>
                  <TableCell>{ticket.title}</TableCell>
                  <TableCell>
                    <Chip 
                      label={ticket.status.replace('_', ' ')}
                      color={getStatusColor(ticket.status) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{ticket.created_by}</TableCell>
                  <TableCell>{formatDate(ticket.created_at)}</TableCell>
                  <TableCell align="right">
                    <IconButton 
                      color="primary" 
                      onClick={() => handleTicketClick(ticket.id)}
                    >
                      <VisibilityIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Container>
  );
};

export default AdminDashboard; 