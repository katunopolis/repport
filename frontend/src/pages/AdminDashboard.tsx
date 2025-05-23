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
  Tabs,
  Tab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Switch,
  FormControlLabel,
  CircularProgress,
  Alert,
  Snackbar
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import RefreshIcon from '@mui/icons-material/Refresh';
import LogoutIcon from '@mui/icons-material/Logout';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import PersonAddIcon from '@mui/icons-material/PersonAdd';
import LockIcon from '@mui/icons-material/Lock';
import { ticketsApi, userApi, User, Ticket, authApi, formatTicketId } from '../api/api';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel = (props: TabPanelProps) => {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`admin-tabpanel-${index}`}
      aria-labelledby={`admin-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
};

const AdminDashboard: React.FC = () => {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [userLoading, setUserLoading] = useState(false);
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [tabValue, setTabValue] = useState(0);
  const [openUserDialog, setOpenUserDialog] = useState(false);
  const [openEditDialog, setOpenEditDialog] = useState(false);
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [newUserEmail, setNewUserEmail] = useState('');
  const [newUserPassword, setNewUserPassword] = useState('');
  const [isAdmin, setIsAdmin] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [pwdDialogOpen, setPwdDialogOpen] = useState(false);
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [pwdChangeError, setPwdChangeError] = useState<string | null>(null);
  const navigate = useNavigate();

  // Fetch tickets and users
  const fetchTickets = async () => {
    setLoading(true);
    try {
      const data = await ticketsApi.getTickets();
      setTickets(data);
    } catch (err) {
      console.error('Error fetching tickets:', err);
      // Fallback to mock data for development/testing
      setTickets([
        { id: 1, title: "Can't login to my account", status: "open", created_at: "2025-05-15T10:00:00Z", created_by: "user@example.com", description: "", is_public: false },
        { id: 2, title: "Need to reset my password", status: "closed", created_at: "2025-05-10T14:30:00Z", created_by: "jane.smith@example.com", description: "", is_public: false },
        { id: 3, title: "Feature request: dark mode", status: "in_progress", created_at: "2025-05-18T09:15:00Z", created_by: "mike.johnson@example.com", description: "", is_public: true },
        { id: 4, title: "Error when uploading files", status: "open", created_at: "2025-05-19T11:20:00Z", created_by: "sarah.wilson@example.com", description: "", is_public: false },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const fetchUsers = async () => {
    setUserLoading(true);
    try {
      const data = await userApi.getUsers();
      setUsers(data);
    } catch (err) {
      console.error('Error fetching users:', err);
      // Fallback to mock data for development/testing
      setUsers([
        { id: '1', email: 'admin@example.com', is_active: true, is_superuser: true, is_verified: true, created_at: '2025-05-10T10:00:00Z' },
        { id: '2', email: 'user@example.com', is_active: true, is_superuser: false, is_verified: true, created_at: '2025-05-10T11:00:00Z' },
        { id: '3', email: 'jane.smith@example.com', is_active: true, is_superuser: false, is_verified: true, created_at: '2025-05-12T09:30:00Z' },
        { id: '4', email: 'support@example.com', is_active: true, is_superuser: true, is_verified: true, created_at: '2025-05-14T08:45:00Z' },
      ]);
    } finally {
      setUserLoading(false);
    }
  };

  useEffect(() => {
    fetchTickets();
    fetchUsers();
  }, []);

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
      setSnackbar({
        open: true,
        message: 'Password changed successfully',
        severity: 'success'
      });
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

  const handleStatusChange = (event: SelectChangeEvent) => {
    setStatusFilter(event.target.value);
  };

  const handleTabChange = (_: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  // User management handlers
  const handleCreateUser = async () => {
    if (!newUserEmail || !newUserPassword) return;
    
    setLoading(true);
    try {
      await userApi.createUser(newUserEmail, newUserPassword, isAdmin);
      setSnackbar({ 
        open: true, 
        message: `User ${newUserEmail} created successfully`, 
        severity: 'success' 
      });
      fetchUsers();
      setOpenUserDialog(false);
      setNewUserEmail('');
      setNewUserPassword('');
      setIsAdmin(false);
    } catch (err) {
      console.error('Error creating user:', err);
      setSnackbar({ 
        open: true, 
        message: 'Failed to create user', 
        severity: 'error' 
      });
    } finally {
      setLoading(false);
    }
  };

  const handleEditUser = (user: User) => {
    setSelectedUser(user);
    setIsAdmin(user.is_superuser);
    setOpenEditDialog(true);
  };

  const handleUpdateUser = async () => {
    if (!selectedUser) return;
    
    setLoading(true);
    try {
      await userApi.updateUser(selectedUser.id, {
        is_superuser: isAdmin,
        is_active: selectedUser.is_active
      });
      setSnackbar({ 
        open: true, 
        message: `User ${selectedUser.email} updated successfully`, 
        severity: 'success' 
      });
      fetchUsers();
      setOpenEditDialog(false);
      setSelectedUser(null);
    } catch (err) {
      console.error('Error updating user:', err);
      setSnackbar({ 
        open: true, 
        message: 'Failed to update user', 
        severity: 'error' 
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteClick = (user: User) => {
    setSelectedUser(user);
    setOpenDeleteDialog(true);
  };

  const handleDeleteUser = async () => {
    if (!selectedUser) return;
    
    setLoading(true);
    try {
      await userApi.deleteUser(selectedUser.id);
      setSnackbar({ 
        open: true, 
        message: `User ${selectedUser.email} deleted successfully`, 
        severity: 'success' 
      });
      fetchUsers();
      setOpenDeleteDialog(false);
      setSelectedUser(null);
    } catch (err) {
      console.error('Error deleting user:', err);
      setSnackbar({ 
        open: true, 
        message: 'Failed to delete user', 
        severity: 'error' 
      });
    } finally {
      setLoading(false);
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

  // Filter tickets based on status
  const filteredTickets = statusFilter === 'all' 
    ? tickets 
    : tickets.filter(ticket => ticket.status === statusFilter);

  // Add togglePublic handler
  const handleTogglePublic = async (ticketId: number, currentPublicStatus: boolean) => {
    setLoading(true);
    try {
      const result = await ticketsApi.toggleTicketPublic(ticketId, !currentPublicStatus);
      
      // Update tickets in state
      setTickets(tickets.map(ticket => 
        ticket.id === ticketId ? { ...ticket, is_public: !currentPublicStatus } : ticket
      ));
      
      setSnackbar({
        open: true,
        message: `Ticket ${formatTicketId(ticketId)} is now ${!currentPublicStatus ? 'public' : 'private'}`,
        severity: 'success'
      });
    } catch (err) {
      console.error('Error toggling ticket public status:', err);
      setSnackbar({
        open: true,
        message: 'Failed to update ticket visibility',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Admin Dashboard
        </Typography>
        <Box>
          <IconButton onClick={tabValue === 0 ? fetchTickets : fetchUsers} disabled={loading} sx={{ mr: 1 }}>
            <RefreshIcon />
          </IconButton>
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

      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={tabValue} onChange={handleTabChange} aria-label="admin tabs">
          <Tab label="Ticket Management" id="admin-tab-0" aria-controls="admin-tabpanel-0" />
          <Tab label="User Management" id="admin-tab-1" aria-controls="admin-tabpanel-1" />
        </Tabs>
      </Box>

      {/* Ticket Management Tab */}
      <TabPanel value={tabValue} index={0}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
          <FormControl sx={{ minWidth: 150 }}>
            <InputLabel id="status-filter-label">Status</InputLabel>
            <Select
              labelId="status-filter-label"
              value={statusFilter}
              label="Status"
              onChange={handleStatusChange}
            >
              <MenuItem value="all">All</MenuItem>
              <MenuItem value="open">Open</MenuItem>
              <MenuItem value="in_progress">In Progress</MenuItem>
              <MenuItem value="closed">Closed</MenuItem>
            </Select>
          </FormControl>
          <Button 
            startIcon={<RefreshIcon />} 
            onClick={fetchTickets}
            disabled={loading}
          >
            Refresh
          </Button>
        </Box>
        
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Ticket ID</TableCell>
                <TableCell>Title</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Created By</TableCell>
                <TableCell>Date</TableCell>
                <TableCell>Visibility</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    <CircularProgress size={24} />
                  </TableCell>
                </TableRow>
              ) : tickets.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    No tickets found
                  </TableCell>
                </TableRow>
              ) : (
                tickets
                  .filter(ticket => statusFilter === 'all' || ticket.status === statusFilter)
                  .map(ticket => (
                    <TableRow 
                      key={ticket.id} 
                      hover 
                      onClick={() => handleTicketClick(ticket.id)}
                      sx={{ cursor: 'pointer' }}
                    >
                      <TableCell>{formatTicketId(ticket.id)}</TableCell>
                      <TableCell>{ticket.title}</TableCell>
                      <TableCell>
                        <Chip 
                          label={ticket.status.replace('_', ' ')} 
                          color={getStatusColor(ticket.status)} 
                          size="small" 
                        />
                      </TableCell>
                      <TableCell>{ticket.created_by}</TableCell>
                      <TableCell>{formatDate(ticket.created_at)}</TableCell>
                      <TableCell onClick={(e) => e.stopPropagation()}>
                        <FormControlLabel
                          control={
                            <Switch
                              checked={ticket.is_public}
                              onChange={() => handleTogglePublic(ticket.id, ticket.is_public)}
                              color="primary"
                            />
                          }
                          label={ticket.is_public ? "Public" : "Private"}
                        />
                      </TableCell>
                    </TableRow>
                  ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </TabPanel>

      {/* User Management Tab */}
      <TabPanel value={tabValue} index={1}>
        <Box sx={{ mb: 3, display: 'flex', justifyContent: 'flex-end' }}>
          <Button 
            variant="contained" 
            startIcon={<PersonAddIcon />}
            onClick={() => setOpenUserDialog(true)}
          >
            Add User
          </Button>
        </Box>

        <TableContainer component={Paper} elevation={2}>
          <Table sx={{ minWidth: 650 }}>
            <TableHead>
              <TableRow>
                <TableCell>Email</TableCell>
                <TableCell>Role</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Created</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {userLoading ? (
                <TableRow>
                  <TableCell colSpan={5} align="center">
                    <CircularProgress size={30} sx={{ my: 2 }} />
                  </TableCell>
                </TableRow>
              ) : users.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} align="center">
                    No users found
                  </TableCell>
                </TableRow>
              ) : (
                users.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell>{user.email}</TableCell>
                    <TableCell>
                      <Chip 
                        label={user.is_superuser ? "Admin" : "User"}
                        color={user.is_superuser ? "error" : "primary"}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={user.is_active ? "Active" : "Inactive"}
                        color={user.is_active ? "success" : "default"}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{formatDate(user.created_at)}</TableCell>
                    <TableCell align="right">
                      <IconButton 
                        color="primary" 
                        onClick={() => handleEditUser(user)}
                        sx={{ mr: 1 }}
                      >
                        <EditIcon />
                      </IconButton>
                      <IconButton 
                        color="error" 
                        onClick={() => handleDeleteClick(user)}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </TabPanel>

      {/* Add User Dialog */}
      <Dialog open={openUserDialog} onClose={() => setOpenUserDialog(false)}>
        <DialogTitle>Add New User</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Email Address"
            type="email"
            fullWidth
            variant="outlined"
            value={newUserEmail}
            onChange={(e) => setNewUserEmail(e.target.value)}
          />
          <TextField
            margin="dense"
            label="Password"
            type="password"
            fullWidth
            variant="outlined"
            value={newUserPassword}
            onChange={(e) => setNewUserPassword(e.target.value)}
          />
          <FormControlLabel
            control={
              <Switch 
                checked={isAdmin} 
                onChange={(e) => setIsAdmin(e.target.checked)} 
              />
            }
            label="Admin User"
            sx={{ mt: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenUserDialog(false)}>Cancel</Button>
          <Button onClick={handleCreateUser} variant="contained" disabled={!newUserEmail || !newUserPassword}>
            Create
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit User Dialog */}
      <Dialog open={openEditDialog} onClose={() => setOpenEditDialog(false)}>
        <DialogTitle>Edit User</DialogTitle>
        <DialogContent>
          {selectedUser && (
            <>
              <Typography variant="h6" sx={{ mb: 2 }}>
                {selectedUser.email}
              </Typography>
              <FormControlLabel
                control={
                  <Switch 
                    checked={isAdmin} 
                    onChange={(e) => setIsAdmin(e.target.checked)} 
                  />
                }
                label="Admin User"
                sx={{ mb: 1, display: 'block' }}
              />
              <FormControlLabel
                control={
                  <Switch 
                    checked={selectedUser.is_active} 
                    onChange={(e) => setSelectedUser({
                      ...selectedUser,
                      is_active: e.target.checked
                    })} 
                  />
                }
                label="Active"
              />
            </>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenEditDialog(false)}>Cancel</Button>
          <Button onClick={handleUpdateUser} variant="contained">
            Update
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete User Confirmation Dialog */}
      <Dialog open={openDeleteDialog} onClose={() => setOpenDeleteDialog(false)}>
        <DialogTitle>Delete User</DialogTitle>
        <DialogContent>
          {selectedUser && (
            <Typography>
              Are you sure you want to delete the user <strong>{selectedUser.email}</strong>? This action cannot be undone.
            </Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDeleteDialog(false)}>Cancel</Button>
          <Button onClick={handleDeleteUser} variant="contained" color="error">
            Delete
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

      {/* Snackbar for notifications */}
      <Snackbar 
        open={snackbar.open} 
        autoHideDuration={6000} 
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert 
          onClose={() => setSnackbar({ ...snackbar, open: false })} 
          severity={snackbar.severity as any} 
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default AdminDashboard; 