import React, { useState, useEffect, useCallback } from 'react';
import {
  Box, TextField, Button, Typography, Container,
  List, ListItem, ListItemText, IconButton, Paper,
  Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle,
  CircularProgress, Alert
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import AddIcon from '@mui/icons-material/Add';
import { masterApiService } from '../../services/masterApi';

const MasterAdminPage = () => {
  // Authentication State
  const [password, setPassword] = useState('');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authError, setAuthError] = useState('');

  // UI State
  const [hotels, setHotels] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [editHotel, setEditHotel] = useState(null);
  const [openEditDialog, setOpenEditDialog] = useState(false);

  // Form State
  const [newHotelName, setNewHotelName] = useState('');
  const [newHotelPassword, setNewHotelPassword] = useState('');
  const [updatePassword, setUpdatePassword] = useState('');

  const fetchHotels = useCallback(async () => {
    if (!password) return;
    setLoading(true);
    setError('');
    try {
      const data = await masterApiService.getHotels(password);
      setHotels(data);
    } catch (err) {
      setError(err.detail || 'Failed to fetch hotels. Check credentials or server status.');
      // If fetching fails, we are not authenticated
      setIsAuthenticated(false);
    } finally {
      setLoading(false);
    }
  }, [password]);

  const handleLogin = async (e) => {
    e.preventDefault();
    setAuthError('');
    if (!password) {
      setAuthError('Master password cannot be empty.');
      return;
    }
    setLoading(true);
    try {
      // We verify the password by attempting to fetch the hotels.
      await masterApiService.getHotels(password);
      setIsAuthenticated(true);
      setAuthError('');
    } catch (err) {
      setAuthError(err.detail || 'Authentication failed.');
      setIsAuthenticated(false);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      fetchHotels();
    }
  }, [isAuthenticated, fetchHotels]);

  const handleCreateHotel = async (e) => {
    e.preventDefault();
    setError('');
    if (!newHotelName || !newHotelPassword) {
      setError('Hotel Name and Password are required.');
      return;
    }
    try {
      await masterApiService.createHotel({ hotel_name: newHotelName, password: newHotelPassword }, password);
      setNewHotelName('');
      setNewHotelPassword('');
      fetchHotels(); // Refresh the list
    } catch (err) {
      setError(err.detail || 'Failed to create hotel.');
    }
  };

  const handleOpenEditDialog = (hotel) => {
    setEditHotel(hotel);
    setUpdatePassword('');
    setOpenEditDialog(true);
  };

  const handleCloseEditDialog = () => {
    setOpenEditDialog(false);
    setEditHotel(null);
  };

  const handleUpdateHotel = async () => {
    setError('');
    if (!updatePassword) {
      setError('New password cannot be empty.');
      return;
    }
    try {
      await masterApiService.updateHotel(editHotel.id, { password: updatePassword }, password);
      handleCloseEditDialog();
      fetchHotels(); // Refresh the list
    } catch (err) {
      setError(err.detail || 'Failed to update hotel.');
    }
  };

  if (!isAuthenticated) {
    return (
      <Container component="main" maxWidth="xs">
        <Box sx={{ marginTop: 8, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <Typography component="h1" variant="h5">Master Access</Typography>
          <Box component="form" onSubmit={handleLogin} noValidate sx={{ mt: 1 }}>
            <TextField margin="normal" required fullWidth name="password" label="Master Password" type="password" id="password" value={password} onChange={(e) => setPassword(e.target.value)} error={!!authError} helperText={authError} autoFocus />
            <Button type="submit" fullWidth variant="contained" sx={{ mt: 3, mb: 2 }} disabled={loading}>
              {loading ? <CircularProgress size={24} /> : 'Authenticate'}
            </Button>
          </Box>
        </Box>
      </Container>
    );
  }

  return (
    <Container>
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>Master Admin Panel</Typography>

        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

        <Paper sx={{ p: 2, mb: 4 }}>
          <Typography variant="h6">Create New Hotel</Typography>
          <Box component="form" onSubmit={handleCreateHotel} sx={{ display: 'flex', gap: 2, mt: 2, flexWrap: 'wrap' }}>
            <TextField label="Hotel Name" value={newHotelName} onChange={(e) => setNewHotelName(e.target.value)} required />
            <TextField label="Password" type="password" value={newHotelPassword} onChange={(e) => setNewHotelPassword(e.target.value)} required />
            <Button type="submit" variant="contained" startIcon={<AddIcon />}>Create</Button>
          </Box>
        </Paper>

        <Typography variant="h6">Manage Hotels</Typography>
        {loading ? <CircularProgress /> : (
          <List component={Paper}>
            {hotels.map((hotel) => (
              <ListItem key={hotel.id} secondaryAction={
                <IconButton edge="end" aria-label="edit" onClick={() => handleOpenEditDialog(hotel)}>
                  <EditIcon />
                </IconButton>
              }>
                <ListItemText primary={hotel.hotel_name} secondary={`ID: ${hotel.id}`} />
              </ListItem>
            ))}
          </List>
        )}
      </Box>

      <Dialog open={openEditDialog} onClose={handleCloseEditDialog}>
        <DialogTitle>Update Hotel</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Updating password for: <strong>{editHotel?.hotel_name}</strong>
          </DialogContentText>
          <TextField autoFocus margin="dense" id="update-password" label="New Password" type="password" fullWidth variant="standard" value={updatePassword} onChange={(e) => setUpdatePassword(e.target.value)} />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseEditDialog}>Cancel</Button>
          <Button onClick={handleUpdateHotel}>Update Password</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default MasterAdminPage;
