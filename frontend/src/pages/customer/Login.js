import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { customerService } from '../../services/api';
import {
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Box,
  InputAdornment,
  Grow,
  Fade,
  Card,
  CardMedia,
  Grid,
  useTheme,
  styled,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress
} from '@mui/material';
import TableRestaurantIcon from '@mui/icons-material/TableRestaurant';
import KeyIcon from '@mui/icons-material/Key';
import LocalDiningIcon from '@mui/icons-material/LocalDining';
import FoodBankIcon from '@mui/icons-material/FoodBank';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import PersonIcon from '@mui/icons-material/Person';

const StyledTextField = styled(TextField)(({ theme }) => ({
  '& .MuiOutlinedInput-root': {
    borderRadius: 4,
    transition: 'all 0.3s ease-in-out',
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    height: '3.5rem', // Increased height by 25%
    '& .MuiOutlinedInput-notchedOutline': {
      borderColor: 'rgba(255, 165, 0, 0.3)',
    },
    '&:hover .MuiOutlinedInput-notchedOutline': {
      borderColor: 'rgba(255, 165, 0, 0.5)',
    },
    '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
      borderWidth: 2,
      borderColor: theme.palette.primary.main,
    },
    '& .MuiOutlinedInput-input': {
      color: '#FFFFFF',
      fontSize: '1.125rem', // Increased font size by 25%
    }
  },
  '& .MuiInputLabel-root': {
    fontWeight: 500,
    color: 'rgba(255, 255, 255, 0.7)',
    fontSize: '1.125rem', // Increased font size by 25%
    '&.Mui-focused': {
      color: theme.palette.primary.main
    }
  },
  '& .MuiInputAdornment-root': {
    '& .MuiSvgIcon-root': {
      color: theme.palette.primary.main,
      fontSize: '1.5rem' // Increased icon size by 25%
    }
  },
  '& .MuiFormHelperText-root': {
    color: 'rgba(255, 255, 255, 0.6)',
    fontSize: '0.875rem', // Increased font size by 25%
    '&.Mui-error': {
      color: '#ff6b6b'
    }
  }
}));

const AnimatedButton = styled(Button)(({ theme }) => ({
  borderRadius: 4,
  fontWeight: 600,
  padding: '15px 30px', // Increased padding by 25%
  fontSize: '1.25rem', // Increased font size by 25%
  boxShadow: '0 8px 20px rgba(255, 165, 0, 0.25)',
  transition: 'all 0.3s ease',
  backgroundColor: theme.palette.primary.main,
  '&:hover': {
    transform: 'translateY(-3px)',
    boxShadow: '0 12px 25px rgba(255, 165, 0, 0.35)',
    backgroundColor: theme.palette.primary.dark,
  }
}));

const LoginBox = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  borderRadius: 6,
  textAlign: 'center',
  boxShadow: '0 12px 30px rgba(0,0,0,0.2)',
  background: '#121212',
  color: '#FFFFFF',
  overflow: 'hidden',
  position: 'relative',
  border: '1px solid rgba(255, 165, 0, 0.2)',
  '&:before': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    height: 4,
    background: theme.palette.primary.main,
  }
}));

const CustomerLogin = () => {
  const navigate = useNavigate();
  const theme = useTheme();

  // Simplified state - only phone number needed
  const [tableNumber, setTableNumber] = useState('');
  const [uniqueId, setUniqueId] = useState('');
  const [phoneNumber, setPhoneNumber] = useState('+91');
  const [phoneError, setPhoneError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [loginError, setLoginError] = useState('');

  // OTP verification states
  const [showOtpDialog, setShowOtpDialog] = useState(false);
  const [otpCode, setOtpCode] = useState('');
  const [otpError, setOtpError] = useState('');
  const [verifyingOtp, setVerifyingOtp] = useState(false);
  const [otpToken, setOtpToken] = useState(null);

  // Username dialog states
  const [showUsernameDialog, setShowUsernameDialog] = useState(false);
  const [username, setUsername] = useState('');
  const [usernameError, setUsernameError] = useState('');
  const [savingUsername, setSavingUsername] = useState(false);

  // Food images for the gallery
  const foodImages = [
    'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=500&q=80',
    'https://images.unsplash.com/photo-1513104890138-7c749659a591?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=500&q=80',
    'https://images.unsplash.com/photo-1476224203421-9ac39bcb3327?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=500&q=80',
    'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=500&q=80'
  ];

  // Load table number from localStorage and verify database is selected
  useEffect(() => {
    // Check if database is already selected from home page
    const selectedDatabase = localStorage.getItem('customerSelectedDatabase');
    const databasePassword = localStorage.getItem('customerDatabasePassword');
    const savedTableNumber = localStorage.getItem('tableNumber');

    if (!selectedDatabase || !databasePassword || !savedTableNumber) {
      // Redirect back to home page if database/table not selected
      navigate('/');
      return;
    }

    // Set the credentials for API calls
    localStorage.setItem('selectedDatabase', selectedDatabase);
    localStorage.setItem('databasePassword', databasePassword);

    // Set table number
    setTableNumber(savedTableNumber);

    // Auto-generate a unique ID
    const generatedUniqueId = Math.random().toString(36).substring(2, 10).toUpperCase();
    setUniqueId(generatedUniqueId);
  }, [navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validate phone number
    let isValid = true;

    if (!phoneNumber) {
      setPhoneError('Please enter your phone number');
      isValid = false;
    } else if (!/^\+91[0-9]{10}$/.test(phoneNumber)) {
      setPhoneError('Please enter a valid phone number starting with +91 followed by 10 digits');
      isValid = false;
    } else {
      setPhoneError('');
    }

    if (isValid) {
      setIsLoading(true);
      setLoginError('');

      try {
        console.log('Requesting verification code for:', phoneNumber);

        const response = await customerService.sendOtp({
          phone_number: phoneNumber,
          table_number: parseInt(tableNumber, 10),
        });

        if (response.success && response.token) {
          setOtpToken(response.token);
          console.log('Verification code sent successfully');
          setShowOtpDialog(true);
        } else {
          throw new Error(response.message || 'Failed to send verification code.');
        }
      } catch (error) {
        console.error('OTP send error:', error);
        const errorMessage = error.response?.data?.detail || error.message || 'An unknown error occurred.';
        setLoginError(`Failed to send verification code: ${errorMessage}`);
      } finally {
        setIsLoading(false);
      }
    }
  };

  const handleVerifyOtp = async () => {
    if (!otpCode || otpCode.length !== 5) {
      setOtpError('Please enter a valid 5-digit OTP');
      return;
    }

    setVerifyingOtp(true);
    setOtpError('');

    try {
      console.log('Verifying OTP:', otpCode);

      const response = await customerService.verifyOtp({
        phone_number: phoneNumber,
        verification_code: otpCode,
        token: otpToken,
        table_number: parseInt(tableNumber, 10),
      });

      if (response.success) {
        if (response.user_exists) {
          // Existing user - redirect to menu
          navigate(`/customer/menu?table_number=${tableNumber}&unique_id=${uniqueId}&user_id=${response.user_id}`);
        } else {
          // New user - show username dialog
          setShowOtpDialog(false);
          setShowUsernameDialog(true);
        }
      } else {
        // This case should ideally not be hit if backend uses HTTP exceptions
        throw new Error(response.message || 'Verification failed.');
      }
    } catch (error) {
      console.error('OTP verification error:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'An unknown error occurred.';
      setOtpError(`Verification failed: ${errorMessage}`);
    } finally {
      setVerifyingOtp(false);
    }
  };

  const handleRegisterUser = async () => {
    if (!username) {
      setUsernameError('Please enter a username');
      return;
    }

    setSavingUsername(true);
    setUsernameError('');

    try {
      // Register new user
      const response = await customerService.registerPhoneUser({
        phone_number: phoneNumber,
        username: username,
        table_number: parseInt(tableNumber, 10)
      });

      // Redirect to menu
      navigate(`/customer/menu?table_number=${tableNumber}&unique_id=${uniqueId}&user_id=${response.user_id}`);
    } catch (error) {
      console.error('User registration error:', error);
      if (error.response && error.response.status === 400) {
        setUsernameError(error.response.data.detail || 'Username already exists. Please choose another one.');
      } else {
        setUsernameError('Failed to register user. Please try again.');
      }
    } finally {
      setSavingUsername(false);
    }
  };

  return (
    <Container maxWidth="xl" sx={{ px: { xs: 1, sm: 2 } }}>
      <Grid container spacing={2} alignItems="center" sx={{ minHeight: 'calc(100vh - 160px)' }}>
        {/* Left side: Form */}
        <Grid item xs={12} md={6}>
          <Grow in={true} timeout={800}>
            <LoginBox>
              <Fade in={true} timeout={1200}>
                <Box>
                  <Box mb={3} display="flex" alignItems="center" justifyContent="center">
                    <FoodBankIcon sx={{ color: 'primary.main', fontSize: 50, mr: 1.5 }} />
                    <Typography variant="h4" fontWeight="bold" sx={{ color: 'white', fontSize: '2rem' }}>
                      TABBLE
                    </Typography>
                  </Box>

                  <Typography variant="h5" gutterBottom fontWeight="bold" sx={{ color: 'white', fontSize: '1.5rem' }}>
                    Hotel Dining Experience
                  </Typography>
                  <Typography variant="body1" sx={{ color: 'rgba(255,255,255,0.7)', maxWidth: 450, mx: 'auto', mb: 3, fontSize: '1.125rem' }}>
                    Enter your details below to access our menu and enjoy a sophisticated dining experience.
                  </Typography>

                  <Box mb={4}>
                    <form onSubmit={handleSubmit}>
                      {/* Show table info */}
                      <Paper
                        elevation={0}
                        sx={{
                          p: 2,
                          mb: 3,
                          backgroundColor: 'rgba(255, 255, 255, 0.05)',
                          borderRadius: '8px',
                          border: '1px solid rgba(255, 165, 0, 0.2)'
                        }}
                      >
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <TableRestaurantIcon sx={{ color: theme.palette.primary.main, mr: 1 }} />
                            <Typography variant="body1" sx={{ color: 'rgba(255,255,255,0.7)' }}>
                              Table Number
                            </Typography>
                          </Box>
                          <Typography variant="h6" sx={{ color: 'white', fontWeight: 'bold' }}>
                            {tableNumber}
                          </Typography>
                        </Box>

                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <KeyIcon sx={{ color: theme.palette.primary.main, mr: 1 }} />
                            <Typography variant="body1" sx={{ color: 'rgba(255,255,255,0.7)' }}>
                              Unique ID
                            </Typography>
                          </Box>
                          <Typography variant="h6" sx={{ color: 'white', fontWeight: 'bold' }}>
                            {uniqueId}
                          </Typography>
                        </Box>
                      </Paper>

                      {/* Phone Number Input */}
                      <StyledTextField
                        label="Phone Number"
                        variant="outlined"
                        fullWidth
                        value={phoneNumber}
                        onChange={(e) => setPhoneNumber(e.target.value)}
                        placeholder="+91XXXXXXXXXX"
                        error={!!phoneError}
                        helperText={phoneError || "Enter your phone number starting with +91"}
                        sx={{ mb: 3 }}
                        InputProps={{
                          startAdornment: (
                            <InputAdornment position="start">
                              <PersonIcon sx={{ color: theme.palette.primary.main }} />
                            </InputAdornment>
                          ),
                        }}
                        autoFocus
                      />

                      {loginError && (
                        <Typography variant="body2" sx={{ mt: 2, textAlign: 'center', color: '#ff6b6b' }}>
                          {loginError}
                        </Typography>
                      )}

                      <Box sx={{ mt: 5, position: 'relative' }}>
                        <AnimatedButton
                          type="submit"
                          variant="contained"
                          fullWidth
                          size="large"
                          endIcon={<ArrowForwardIcon />}
                          disabled={isLoading}
                        >
                          {isLoading ? 'Sending OTP...' : 'Continue with Phone'}
                        </AnimatedButton>
                      </Box>
                    </form>
                  </Box>
                </Box>
              </Fade>
            </LoginBox>
          </Grow>
        </Grid>

        {/* Right side: Food gallery */}
        <Grid item xs={12} md={6}>
          <Box sx={{ height: '100%', position: 'relative' }}>
            <Grid container spacing={1}>
              {foodImages.map((image, index) => (
                <Grid item xs={6} key={index}>
                  <Grow in={true} timeout={(index + 1) * 300 + 800}>
                    <Card
                      sx={{
                        borderRadius: 1,
                        overflow: 'hidden',
                        boxShadow: '0 15px 30px rgba(0, 0, 0, 0.3)',
                        height: index % 2 === 0 ? 250 : 200,
                        transition: 'all 0.3s ease-in-out',
                        border: '1px solid rgba(255, 165, 0, 0.2)',
                        position: 'relative',
                        '&:hover': {
                          transform: 'translateY(-5px)',
                          boxShadow: '0 15px 30px rgba(0, 0, 0, 0.4)'
                        },
                        '&::after': {
                          content: '""',
                          position: 'absolute',
                          top: 0,
                          left: 0,
                          width: '100%',
                          height: '4px',
                          backgroundColor: theme.palette.primary.main
                        }
                      }}
                    >
                      <CardMedia
                        component="img"
                        height="100%"
                        image={image}
                        alt={`Food item ${index + 1}`}
                        sx={{ objectFit: 'cover' }}
                      />
                    </Card>
                  </Grow>
                </Grid>
              ))}
            </Grid>

            <Fade in={true} timeout={2000}>
              <Box
                sx={{
                  position: 'absolute',
                  bottom: 10,
                  left: 0,
                  right: 0,
                  mx: 'auto',
                  width: '90%',
                  textAlign: 'center',
                  backgroundColor: 'rgba(0,0,0,0.85)',
                  backdropFilter: 'blur(10px)',
                  p: 2,
                  borderRadius: 1,
                  border: '1px solid rgba(255, 165, 0, 0.3)',
                  boxShadow: '0 8px 32px rgba(0,0,0,0.3)'
                }}
              >
                <Typography variant="h6" gutterBottom fontWeight="bold" sx={{ color: 'white', fontSize: '1.25rem' }}>
                  <LocalDiningIcon sx={{ mr: 1, verticalAlign: 'middle', color: theme.palette.primary.main, fontSize: '1.5rem' }} />
                  Exquisite Dining
                </Typography>
                <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)', fontSize: '1rem' }}>
                  Discover our award-winning cuisine crafted with premium ingredients
                </Typography>
              </Box>
            </Fade>
          </Box>
        </Grid>
      </Grid>

      {/* OTP Verification Dialog */}
      <Dialog
        open={showOtpDialog}
        maxWidth="xs"
        fullWidth
        PaperProps={{
          sx: {
            backgroundColor: '#121212',
            color: 'white',
            borderRadius: 2,
            border: '1px solid rgba(255, 165, 0, 0.3)',
            boxShadow: '0 8px 32px rgba(0,0,0,0.3)',
            position: 'relative',
            '&::before': {
              content: '""',
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              height: 4,
              backgroundColor: theme.palette.primary.main,
            }
          }
        }}
      >
        <DialogTitle sx={{ textAlign: 'center', pt: 3 }}>
          <Typography variant="h5" fontWeight="bold">
            Verify Phone Number
          </Typography>
        </DialogTitle>
        <DialogContent>
          <Typography variant="body1" sx={{ mb: 3, textAlign: 'center', color: 'rgba(255,255,255,0.7)' }}>
            Enter the 5-digit code sent to {phoneNumber}
          </Typography>

          <StyledTextField
            label="Verification Code"
            variant="outlined"
            fullWidth
            value={otpCode}
            onChange={(e) => setOtpCode(e.target.value)}
            error={!!otpError}
            helperText={otpError}
            sx={{ mb: 2 }}
            inputProps={{ maxLength: 5 }}
          />
        </DialogContent>
        <DialogActions sx={{ p: 3, pt: 0, justifyContent: 'center' }}>
          <Button
            variant="outlined"
            onClick={() => setShowOtpDialog(false)}
            sx={{
              borderColor: 'rgba(255,165,0,0.5)',
              color: 'white',
              '&:hover': {
                borderColor: 'rgba(255,165,0,0.8)',
                backgroundColor: 'rgba(255,165,0,0.1)'
              }
            }}
            disabled={verifyingOtp}
          >
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={handleVerifyOtp}
            disabled={verifyingOtp}
            sx={{
              ml: 2,
              backgroundColor: theme.palette.primary.main,
              '&:hover': {
                backgroundColor: theme.palette.primary.dark
              }
            }}
          >
            {verifyingOtp ? (
              <CircularProgress size={24} color="inherit" />
            ) : (
              'Verify'
            )}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Username Dialog */}
      <Dialog
        open={showUsernameDialog}
        maxWidth="xs"
        fullWidth
        PaperProps={{
          sx: {
            backgroundColor: '#121212',
            color: 'white',
            borderRadius: 2,
            border: '1px solid rgba(255, 165, 0, 0.3)',
            boxShadow: '0 8px 32px rgba(0,0,0,0.3)',
            position: 'relative',
            '&::before': {
              content: '""',
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              height: 4,
              backgroundColor: theme.palette.primary.main,
            }
          }
        }}
      >
        <DialogTitle sx={{ textAlign: 'center', pt: 3 }}>
          <Typography variant="h5" fontWeight="bold">
            Create Your Account
          </Typography>
        </DialogTitle>
        <DialogContent>
          <Typography variant="body1" sx={{ mb: 3, textAlign: 'center', color: 'rgba(255,255,255,0.7)' }}>
            Please choose a username for your account
          </Typography>

          <StyledTextField
            label="Username"
            variant="outlined"
            fullWidth
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            error={!!usernameError}
            helperText={usernameError}
            sx={{ mb: 2 }}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <PersonIcon sx={{ color: theme.palette.primary.main }} />
                </InputAdornment>
              ),
            }}
          />
        </DialogContent>
        <DialogActions sx={{ p: 3, pt: 0, justifyContent: 'center' }}>
          <Button
            variant="contained"
            onClick={handleRegisterUser}
            disabled={savingUsername}
            fullWidth
            sx={{
              backgroundColor: theme.palette.primary.main,
              '&:hover': {
                backgroundColor: theme.palette.primary.dark
              }
            }}
          >
            {savingUsername ? (
              <CircularProgress size={24} color="inherit" />
            ) : (
              'Continue'
            )}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default CustomerLogin;
