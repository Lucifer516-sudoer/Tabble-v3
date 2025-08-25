import React, { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Provider } from 'react-redux';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import MasterAdminPage from './pages/admin/MasterAdminPage';

// Store and Query Client
import { store } from './store';
import { queryClient } from './services/queryClient';

// Error Boundary
import ErrorBoundary from './components/ErrorBoundary';
import LoadingSpinner, { PageLoadingSpinner } from './components/LoadingSpinner';

// Authentication Wrapper
import AuthWrapper from './components/AuthWrapper';

// Layouts (not lazy loaded as they're used frequently)
import Layout from './components/Layout';
import AdminLayout from './components/AdminLayout';
import ChefLayout from './components/ChefLayout';

// Lazy load pages for code splitting
const Home = lazy(() => import('./pages/Home'));
const ChefDashboard = lazy(() => import('./pages/chef/Dashboard'));
const ChefOrders = lazy(() => import('./pages/chef/Orders'));
const CustomerLogin = lazy(() => import('./pages/customer/Login'));
const CustomerMenu = lazy(() => import('./pages/customer/Menu'));
const AdminDashboard = lazy(() => import('./pages/admin/Dashboard'));
const DashboardDemo = lazy(() => import('./pages/admin/DashboardDemo'));
const AdminDishes = lazy(() => import('./pages/admin/Dishes'));
const AdminOffers = lazy(() => import('./pages/admin/Offers'));
const AdminSpecials = lazy(() => import('./pages/admin/Specials'));
const CompletedOrders = lazy(() => import('./pages/admin/CompletedOrders'));
const LoyaltyProgram = lazy(() => import('./pages/admin/LoyaltyProgram'));
const SelectionOffers = lazy(() => import('./pages/admin/SelectionOffers'));
const TableManagement = lazy(() => import('./pages/admin/TableManagement'));
const AdminSettings = lazy(() => import('./pages/admin/Settings'));

// Analysis Pages (lazy loaded)
const AnalysisDashboard = lazy(() => import('./pages/analysis/Dashboard'));
const CustomerAnalysis = lazy(() => import('./pages/analysis/CustomerAnalysis'));
const DishAnalysis = lazy(() => import('./pages/analysis/DishAnalysis'));
const ChefAnalysis = lazy(() => import('./pages/analysis/ChefAnalysis'));

// Create a theme with luxury hotel aesthetic
const theme = createTheme({
  palette: {
    primary: {
      main: '#FFA500', // Vibrant Orange as primary color
      light: '#FFB733', // Light Orange for subtle highlights
      dark: '#E69500', // Dark Orange for hover states
      contrastText: '#FFFFFF',
    },
    secondary: {
      main: '#000000', // Black as secondary color
      light: '#333333', // Dark Gray for secondary text
      dark: '#000000',
      contrastText: '#FFFFFF',
    },
    error: {
      main: '#FF385C',
    },
    warning: {
      main: '#FFA500', // Using orange for warnings too
      light: '#FFB733',
    },
    success: {
      main: '#4DAA57',
      light: '#6ECF77',
    },
    info: {
      main: '#2196F3',
    },
    background: {
      default: '#000000', // Black background
      paper: '#121212', // Dark paper background
    },
    text: {
      primary: '#FFFFFF', // White text for dark backgrounds
      secondary: '#F5F5F5', // Light gray for secondary text
    },
  },
  typography: {
    fontFamily: '"Montserrat", "Roboto", "Helvetica", "Arial", sans-serif', // Elegant sans-serif font
    h1: {
      fontWeight: 700,
      letterSpacing: '-0.01em',
      fontSize: '32px',
    },
    h2: {
      fontWeight: 700,
      letterSpacing: '-0.01em',
      fontSize: '28px',
    },
    h3: {
      fontWeight: 600,
      fontSize: '24px',
    },
    h4: {
      fontWeight: 600,
      fontSize: '22px',
    },
    h5: {
      fontWeight: 600,
      fontSize: '20px',
    },
    h6: {
      fontWeight: 600,
      fontSize: '18px',
    },
    button: {
      fontWeight: 600,
      textTransform: 'none',
      fontSize: '16px',
    },
    subtitle1: {
      fontWeight: 500,
      fontSize: '16px',
    },
    body1: {
      fontSize: '16px',
      lineHeight: 1.5,
    },
    body2: {
      fontSize: '14px',
      lineHeight: 1.5,
    },
  },
  shape: {
    borderRadius: 6, // Slightly reduced border radius for more elegant look
  },
  shadows: [
    'none',
    '0px 2px 4px rgba(0,0,0,0.15)',
    '0px 4px 8px rgba(0,0,0,0.16)',
    '0px 6px 12px rgba(0,0,0,0.18)',
    '0px 8px 16px rgba(0,0,0,0.18)',
    '0px 10px 20px rgba(0,0,0,0.19)',
    // ...existing shadows
  ],
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          backgroundColor: '#000000',
          color: '#FFFFFF',
        },
        html: {
          backgroundColor: '#000000',
        },
        '#root': {
          backgroundColor: '#000000',
          minHeight: '100vh',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundColor: '#121212', // Dark background for cards
          color: '#FFFFFF', // White text
          boxShadow: '0 8px 20px rgba(0, 0, 0, 0.16)',
          transition: 'transform 0.2s ease, box-shadow 0.2s ease',
          '&:hover': {
            boxShadow: '0 12px 24px rgba(0, 0, 0, 0.18)',
          },
          borderTop: '1px solid rgba(255, 165, 0, 0.3)', // Subtle orange accent
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: '4px', // Rounded corners as specified
          fontWeight: 600,
          padding: '8px 16px',
          boxShadow: '0 4px 10px rgba(0, 0, 0, 0.17)',
          '&:hover': {
            boxShadow: '0 6px 12px rgba(0, 0, 0, 0.2)',
          },
        },
        contained: {
          '&.MuiButton-containedPrimary': {
            background: '#FFA500', // Solid orange for primary buttons
            '&:hover': {
              background: '#E69500', // Darker orange on hover
            },
          },
          '&.MuiButton-containedSecondary': {
            background: '#000000', // Black for secondary buttons
            '&:hover': {
              background: '#333333', // Slightly lighter on hover
            },
          },
        },
        outlined: {
          borderWidth: '2px',
          '&.MuiButton-outlinedPrimary': {
            borderColor: '#FFA500',
            color: '#FFA500',
            '&:hover': {
              borderColor: '#E69500',
              backgroundColor: 'rgba(255, 165, 0, 0.08)',
            },
          },
        },
        text: {
          '&.MuiButton-textPrimary': {
            color: '#FFA500',
            '&:hover': {
              backgroundColor: 'rgba(255, 165, 0, 0.08)',
            },
          },
        },
      },
    },

    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: '#000000', // Black app bar
          boxShadow: '0 2px 10px rgba(0, 0, 0, 0.15)',
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          fontWeight: 500,
          borderRadius: '4px',
        },
        filled: {
          '&.MuiChip-colorPrimary': {
            backgroundColor: '#FFA500',
          },
        },
        outlined: {
          '&.MuiChip-colorPrimary': {
            borderColor: '#FFA500',
            color: '#FFA500',
          },
        },
      },
    },
    MuiTableHead: {
      styleOverrides: {
        root: {
          backgroundColor: 'rgba(255, 165, 0, 0.1)', // Subtle orange background
        },
      },
    },
    MuiTableContainer: {
      styleOverrides: {
        root: {
          border: '1px solid rgba(255, 165, 0, 0.2)', // Orange border around entire table
          borderRadius: '8px',
          overflow: 'hidden',
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
        },
      },
    },
    MuiTableRow: {
      styleOverrides: {
        root: {
          borderBottom: '1px solid rgba(255, 165, 0, 0.15)', // Orange border between rows
          '&:hover': {
            backgroundColor: 'rgba(255, 165, 0, 0.05)', // Subtle orange hover
          },
          '&:last-child': {
            borderBottom: 'none', // Remove border from last row
          },
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        root: {
          borderBottom: '1px solid rgba(255, 165, 0, 0.15)', // Consistent cell borders
          '&:not(:last-child)': {
            borderRight: '1px solid rgba(255, 165, 0, 0.1)', // Vertical borders between cells
          },
        },
        head: {
          borderBottom: '2px solid rgba(255, 165, 0, 0.3)', // Stronger border for header
          fontWeight: 'bold',
        },
      },
    },
    MuiDivider: {
      styleOverrides: {
        root: {
          backgroundColor: 'rgba(255, 165, 0, 0.2)', // Subtle orange dividers
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            '& fieldset': {
              borderColor: 'rgba(255, 255, 255, 0.23)',
            },
            '&:hover fieldset': {
              borderColor: 'rgba(255, 165, 0, 0.5)',
            },
            '&.Mui-focused fieldset': {
              borderColor: '#FFA500',
            },
          },
          '& .MuiInputLabel-root': {
            color: '#F5F5F5',
            '&.Mui-focused': {
              color: '#FFA500',
            },
          },
          '& .MuiInputBase-input': {
            color: '#FFFFFF',
          },
        },
      },
    },
    MuiListItem: {
      styleOverrides: {
        root: {
          borderBottom: '1px solid rgba(255, 165, 0, 0.1)', // Subtle border between list items
          '&:last-child': {
            borderBottom: 'none', // Remove border from last item
          },
          '&.Mui-selected': {
            backgroundColor: 'rgba(255, 165, 0, 0.16)',
            borderLeft: '3px solid #FFA500', // Orange accent for selected items
            '&:hover': {
              backgroundColor: 'rgba(255, 165, 0, 0.2)',
            },
          },
          '&:hover': {
            backgroundColor: 'rgba(255, 165, 0, 0.05)',
          },
        },
      },
    },
    MuiMenuItem: {
      styleOverrides: {
        root: {
          borderBottom: '1px solid rgba(255, 165, 0, 0.1)', // Border between menu items
          '&:last-child': {
            borderBottom: 'none', // Remove border from last item
          },
          '&:hover': {
            backgroundColor: 'rgba(255, 165, 0, 0.08)',
          },
          '&.Mui-selected': {
            backgroundColor: 'rgba(255, 165, 0, 0.12)',
            '&:hover': {
              backgroundColor: 'rgba(255, 165, 0, 0.16)',
            },
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundColor: '#121212', // Dark background for papers
          color: '#FFFFFF', // White text
          borderRadius: '8px',
          border: '1px solid rgba(255, 165, 0, 0.15)', // Subtle border around paper components
          '&.MuiMenu-paper': {
            border: '1px solid rgba(255, 165, 0, 0.2)', // Stronger border for dropdown menus
            boxShadow: '0 8px 24px rgba(0, 0, 0, 0.2)',
            backgroundColor: '#121212',
          },
        },
      },
    },
  },
});

function App() {
  return (
    <Provider store={store}>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <ErrorBoundary>
            <AuthWrapper>
              <Router>
                <Suspense fallback={<PageLoadingSpinner message="Loading application..." />}>
                  <Routes>
                    {/* Master Admin Route (no layout) */}
                    <Route
                      path="/master-admin"
                      element={
                        <ErrorBoundary>
                          <MasterAdminPage />
                        </ErrorBoundary>
                      }
                    />

                    {/* Main Layout Routes */}
                    <Route element={<Layout />}>
                      <Route
                      path="/"
                      element={
                        <ErrorBoundary>
                          <Home />
                        </ErrorBoundary>
                      }
                    />
                  </Route>

                  {/* Chef Layout Routes */}
                  <Route element={<ChefLayout />}>
                    <Route
                      path="/chef"
                      element={
                        <ErrorBoundary>
                          <ChefDashboard />
                        </ErrorBoundary>
                      }
                    />
                    <Route
                      path="/chef/orders"
                      element={
                        <ErrorBoundary>
                          <ChefOrders />
                        </ErrorBoundary>
                      }
                    />
                  </Route>

                  {/* Main Layout Routes (continued) */}
                  <Route element={<Layout />}>
                    {/* Customer Routes */}
                    <Route
                      path="/customer"
                      element={
                        <ErrorBoundary>
                          <CustomerLogin />
                        </ErrorBoundary>
                      }
                    />
                    <Route
                      path="/customer/menu"
                      element={
                        <ErrorBoundary>
                          <CustomerMenu />
                        </ErrorBoundary>
                      }
                    />
                  </Route>

                  {/* Admin Layout Routes */}
                  <Route element={<AdminLayout />}>
                    <Route
                      path="/admin"
                      element={
                        <ErrorBoundary>
                          <AdminDashboard />
                        </ErrorBoundary>
                      }
                    />
                    <Route
                      path="/admin/demo"
                      element={
                        <ErrorBoundary>
                          <DashboardDemo />
                        </ErrorBoundary>
                      }
                    />
                    <Route
                      path="/admin/dishes"
                      element={
                        <ErrorBoundary>
                          <AdminDishes />
                        </ErrorBoundary>
                      }
                    />
                    <Route
                      path="/admin/offers"
                      element={
                        <ErrorBoundary>
                          <AdminOffers />
                        </ErrorBoundary>
                      }
                    />
                    <Route
                      path="/admin/specials"
                      element={
                        <ErrorBoundary>
                          <AdminSpecials />
                        </ErrorBoundary>
                      }
                    />
                    <Route
                      path="/admin/completed-orders"
                      element={
                        <ErrorBoundary>
                          <CompletedOrders />
                        </ErrorBoundary>
                      }
                    />
                    <Route
                      path="/admin/loyalty"
                      element={
                        <ErrorBoundary>
                          <LoyaltyProgram />
                        </ErrorBoundary>
                      }
                    />
                    <Route
                      path="/admin/selection-offers"
                      element={
                        <ErrorBoundary>
                          <SelectionOffers />
                        </ErrorBoundary>
                      }
                    />
                    <Route
                      path="/admin/tables"
                      element={
                        <ErrorBoundary>
                          <TableManagement />
                        </ErrorBoundary>
                      }
                    />
                    <Route
                      path="/admin/settings"
                      element={
                        <ErrorBoundary>
                          <AdminSettings />
                        </ErrorBoundary>
                      }
                    />

                    {/* Analysis Routes */}
                    <Route
                      path="/analysis"
                      element={
                        <ErrorBoundary>
                          <AnalysisDashboard />
                        </ErrorBoundary>
                      }
                    />
                    <Route
                      path="/analysis/customer"
                      element={
                        <ErrorBoundary>
                          <CustomerAnalysis />
                        </ErrorBoundary>
                      }
                    />
                    <Route
                      path="/analysis/dish"
                      element={
                        <ErrorBoundary>
                          <DishAnalysis />
                        </ErrorBoundary>
                      }
                    />
                    <Route
                      path="/analysis/chef"
                      element={
                        <ErrorBoundary>
                          <ChefAnalysis />
                        </ErrorBoundary>
                      }
                    />
                  </Route>
                </Routes>
              </Suspense>
            </Router>
            </AuthWrapper>
          </ErrorBoundary>
        </ThemeProvider>
        {/* React Query Devtools - only in development */}
        {process.env.NODE_ENV === 'development' && (
          <ReactQueryDevtools initialIsOpen={false} />
        )}
      </QueryClientProvider>
    </Provider>
  );
}

export default App;
