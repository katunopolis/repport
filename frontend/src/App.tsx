import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';

// Import pages
import UserDashboard from './pages/UserDashboard';
import AdminDashboard from './pages/AdminDashboard';
import LoginPage from './pages/LoginPage';
import TicketPage from './pages/TicketPage';
import NotFoundPage from './pages/NotFoundPage';

// Create a theme instance
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 500,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 500,
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Routes>
          <Route path="/" element={<LoginPage />} />
          <Route path="/dashboard" element={<UserDashboard />} />
          <Route path="/admin" element={<AdminDashboard />} />
          <Route path="/ticket/:id" element={<TicketPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App; 