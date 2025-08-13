import axios from 'axios';

// Get the base URL from environment variables or fallback to dynamic detection
const getBaseUrl = () => {
  // First, try to get from environment variable
  if (process.env.REACT_APP_API_BASE_URL) {
    return process.env.REACT_APP_API_BASE_URL;
  }

  // Fallback for production builds
  if (process.env.NODE_ENV === 'production') {
    return '/api';
  }

  // Fallback for development (legacy behavior)
  const protocol = window.location.protocol;
  const hostname = window.location.hostname;
  const port = '8000'; // Backend port

  return `${protocol}//${hostname}:${port}`;
};

// Session management
let sessionId = localStorage.getItem('tabbleSessionId');
if (!sessionId) {
  sessionId = 'session_' + Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
  localStorage.setItem('tabbleSessionId', sessionId);
}

// Create an axios instance with default config
const api = axios.create({
  baseURL: getBaseUrl(),
  headers: {
    'Content-Type': 'application/json',
    'x-session-id': sessionId,
  },
});

// Add request interceptor to include database credentials and session ID
api.interceptors.request.use(
  (config) => {
    // Always include session ID
    config.headers['x-session-id'] = sessionId;

    // Include hotel credentials if available
    const selectedHotel = localStorage.getItem('selectedHotel') || localStorage.getItem('selectedDatabase');
    const hotelPassword = localStorage.getItem('hotelPassword') || localStorage.getItem('databasePassword');

    if (selectedHotel && hotelPassword) {
      config.headers['x-hotel-name'] = selectedHotel;
      config.headers['x-hotel-password'] = hotelPassword;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle session ID updates
api.interceptors.response.use(
  (response) => {
    // Update session ID if provided in response
    const newSessionId = response.headers['x-session-id'];
    if (newSessionId && newSessionId !== sessionId) {
      sessionId = newSessionId;
      localStorage.setItem('tabbleSessionId', sessionId);
    }
    return response;
  },
  (error) => {
    // Handle hotel-related errors
    if (error.response?.data?.error_code) {
      const errorCode = error.response.data.error_code;

      if (errorCode === 'HOTEL_NOT_SELECTED' ||
          errorCode === 'HOTEL_AUTH_FAILED' ||
          errorCode === 'HOTEL_VERIFICATION_ERROR' ||
          errorCode === 'DATABASE_NOT_SELECTED' ||
          errorCode === 'DATABASE_AUTH_FAILED' ||
          errorCode === 'DATABASE_CONFIG_MISSING') {
        // Clear hotel/database selection and redirect to setup
        localStorage.removeItem('selectedHotel');
        localStorage.removeItem('hotelPassword');
        localStorage.removeItem('selectedDatabase');
        localStorage.removeItem('databasePassword');
        localStorage.removeItem('tabbleDatabaseSelected');

        // Show error message
        console.error('Hotel authentication error:', error.response.data.detail);

        // Redirect to home for hotel setup
        if (window.location.pathname !== '/') {
          window.location.href = '/';
        }
      }
    }

    return Promise.reject(error);
  }
);

// Customer API services
export const customerService = {
  // Get all menu items
  getMenu: async (category = null) => {
    try {
      const params = category ? { category } : {};
      const response = await api.get('/customer/api/menu', { params });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get offer dishes
  getOffers: async () => {
    try {
      const response = await api.get('/customer/api/offers');
      return response.data;
    } catch (error) {
      
      throw error;
    }
  },

  // Get special dishes
  getSpecials: async () => {
    try {
      const response = await api.get('/customer/api/specials');
      return response.data;
    } catch (error) {
      
      throw error;
    }
  },

  // Get all categories
  getCategories: async () => {
    try {
      const response = await api.get('/customer/api/categories');
      return response.data;
    } catch (error) {
      
      throw error;
    }
  },

  // Create a new order
  createOrder: async (orderData, personId = null) => {
    try {
      // Add person_id as a query parameter if provided
      const params = personId ? { person_id: personId } : {};
      const response = await api.post('/customer/api/orders', orderData, { params });
      return response.data;
    } catch (error) {
      
      throw error;
    }
  },

  // Request payment for an order
  requestPayment: async (orderId) => {
    try {
      const response = await api.put(`/customer/api/orders/${orderId}/payment`);
      return response.data;
    } catch (error) {
      console.error(`Error requesting payment for order ${orderId}:`, error);

      // Provide more specific error messages
      if (error.response) {
        const status = error.response.status;
        const detail = error.response.data?.detail || 'Unknown error';

        if (status === 404) {
          throw new Error('Order not found');
        } else if (status === 400) {
          throw new Error(detail);
        } else if (status === 500) {
          throw new Error('Server error processing payment. Please try again.');
        } else {
          throw new Error(`Payment failed: ${detail}`);
        }
      } else {
        throw new Error('Network error. Please check your connection and try again.');
      }
    }
  },

  // Cancel an order
  cancelOrder: async (orderId) => {
    try {
      const response = await api.put(`/customer/api/orders/${orderId}/cancel`);
      return response.data;
    } catch (error) {
      
      throw error;
    }
  },

  // Get orders by person ID
  getPersonOrders: async (personId) => {
    try {
      const response = await api.get(`/customer/api/person/${personId}/orders`);
      return response.data;
    } catch (error) {
      
      throw error;
    }
  },

  // Get person details
  getPerson: async (personId) => {
    try {
      const response = await api.get(`/customer/api/person/${personId}`);
      return response.data;
    } catch (error) {
      
      throw error;
    }
  },

  // Set a table as occupied by table number
  setTableOccupiedByNumber: async (tableNumber) => {
    try {
      const response = await api.put(`/tables/number/${tableNumber}/occupy`);
      return response.data;
    } catch (error) {
      
      // Don't throw error, just log it
      return null;
    }
  },

  // Submit feedback
  submitFeedback: async (feedbackData) => {
    try {
      const response = await api.post('/feedback/', feedbackData);
      return response.data;
    } catch (error) {
      
      throw error;
    }
  },

  // Get feedback by order ID
  getFeedbackByOrder: async (orderId) => {
    try {
      const response = await api.get(`/feedback/order/${orderId}`);
      return response.data;
    } catch (error) {
      
      throw error;
    }
  },

  // Get loyalty discount for visit count
  getLoyaltyDiscount: async (visitCount) => {
    try {
      const response = await api.get(`/loyalty/discount/${visitCount}`);
      return response.data;
    } catch (error) {
      
      return { discount_percentage: 0, message: 'No loyalty discount available' };
    }
  },

  // Get selection offer discount for order amount
  getSelectionOfferDiscount: async (orderAmount) => {
    try {
      const response = await api.get(`/selection-offers/discount/${orderAmount}`);
      return response.data;
    } catch (error) {

      return { discount_amount: 0, message: 'No selection offer discount available' };
    }
  },

  // Get current database name
  getCurrentDatabase: async () => {
    try {
      const response = await api.get('/settings/current-database');
      return response.data;
    } catch (error) {

      throw error;
    }
  },

  // Send OTP for phone authentication
  sendOtp: async (phoneData) => {
    try {
      const response = await api.post('/customer/api/phone-auth', phoneData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Verify OTP for phone authentication
  verifyOtp: async (otpData) => {
    try {
      const response = await api.post('/customer/api/verify-otp', otpData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Register new phone user
  registerPhoneUser: async (userData) => {
    try {
      const response = await api.post('/customer/api/register-phone-user', userData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },
};

// Chef API services
export const chefService = {
  // Get pending orders (orders that need to be accepted)
  getPendingOrders: async () => {
    try {
      const response = await api.get('/chef/orders/pending');
      return response.data;
    } catch (error) {
      
      throw error;
    }
  },

  // Get accepted orders (orders that have been accepted but not completed)
  getAcceptedOrders: async () => {
    try {
      const response = await api.get('/chef/orders/accepted');
      return response.data;
    } catch (error) {
      
      throw error;
    }
  },

  // Accept an order
  acceptOrder: async (orderId) => {
    try {
      const response = await api.put(`/chef/orders/${orderId}/accept`);
      return response.data;
    } catch (error) {
      
      throw error;
    }
  },

  // Mark an order as completed
  completeOrder: async (orderId) => {
    try {
      const response = await api.put(`/chef/orders/${orderId}/complete`);
      return response.data;
    } catch (error) {
      
      throw error;
    }
  },

  // Get completed orders count
  getCompletedOrdersCount: async () => {
    try {
      const response = await api.get('/chef/api/completed-orders-count');
      return response.data;
    } catch (error) {
      
      throw error;
    }
  },
};

// Admin API services
export const adminService = {
  // Get hotel settings
  getSettings: async () => {
    try {
      const response = await api.get('/settings');
      return response.data;
    } catch (error) {
      
      throw error;
    }
  },

  // Update hotel settings
  updateSettings: async (formData) => {
    try {
      const response = await api.put('/settings', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      
      throw error;
    }
  },

  // Get available hotels (updated from getDatabases)
  getHotels: async () => {
    try {
      const response = await api.get('/settings/hotels');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Legacy method for backward compatibility
  getDatabases: async () => {
    return adminService.getHotels();
  },

  // Get current hotel
  getCurrentHotel: async () => {
    try {
      const response = await api.get('/settings/current-hotel');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Legacy method for backward compatibility
  getCurrentDatabase: async () => {
    try {
      const response = await api.get('/settings/current-database');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Switch hotel (updated from switchDatabase)
  switchHotel: async (hotelName, password) => {
    try {
      const response = await api.post('/settings/switch-hotel', {
        database_name: hotelName,  // Using database_name field for compatibility
        password: password
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Legacy method for backward compatibility
  switchDatabase: async (databaseName, password) => {
    return adminService.switchHotel(databaseName, password);
  },

  // Generate bill PDF for a single order
  generateBill: async (orderId) => {
    try {
      const response = await api.get(`/admin/orders/${orderId}/bill`, {
        responseType: 'blob',
      });
      return response.data;
    } catch (error) {
      
      throw error;
    }
  },

  // Generate bill PDF for multiple orders
  generateMultiBill: async (orderIds) => {
    try {
      const response = await api.post(`/admin/orders/multi-bill`, orderIds, {
        responseType: 'blob',
      });
      return response.data;
    } catch (error) {
      
      throw error;
    }
  },

  // Merge two orders
  mergeOrders: async (sourceOrderId, targetOrderId) => {
    try {
      const response = await api.post(`/admin/orders/merge`, null, {
        params: {
          source_order_id: sourceOrderId,
          target_order_id: targetOrderId
        }
      });
      return response.data;
    } catch (error) {
      
      throw error;
    }
  },
  // Get all dishes
  getDishes: async (isOffer = null, isSpecial = null) => {
    try {
      const params = {};
      if (isOffer !== null) params.is_offer = isOffer;
      if (isSpecial !== null) params.is_special = isSpecial;

      const response = await api.get('/admin/api/dishes', { params });
      return response.data;
    } catch (error) {
      
      throw error;
    }
  },

  // Get offer dishes
  getOfferDishes: async () => {
    try {
      const response = await api.get('/admin/api/offers');
      return response.data;
    } catch (error) {
      
      throw error;
    }
  },

  // Get special dishes
  getSpecialDishes: async () => {
    try {
      const response = await api.get('/admin/api/specials');
      return response.data;
    } catch (error) {
      
      throw error;
    }
  },

  // Get all categories
  getCategories: async () => {
    try {
      const response = await api.get('/admin/api/categories');
      return response.data;
    } catch (error) {
      
      throw error;
    }
  },

  // Create a new category
  createCategory: async (categoryName) => {
    try {
      const formData = new FormData();
      formData.append('category_name', categoryName);
      const response = await api.post('/admin/api/categories', formData);
      return response.data;
    } catch (error) {
      
      throw error;
    }
  },

  // Create a new dish
  createDish: async (dishData) => {
    try {
      const formData = new FormData();
      Object.keys(dishData).forEach(key => {
        formData.append(key, dishData[key]);
      });

      const response = await api.post('/admin/api/dishes', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      
      throw error;
    }
  },

  // Delete a dish
  deleteDish: async (dishId) => {
    try {
      const response = await api.delete(`/admin/api/dishes/${dishId}`);
      return response.data;
    } catch (error) {
      
      throw error;
    }
  },

  // Update a dish
  updateDish: async (dishId, dishData) => {
    try {
      const formData = new FormData();
      Object.keys(dishData).forEach(key => {
        formData.append(key, dishData[key]);
      });

      const response = await api.put(`/admin/api/dishes/${dishId}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      
      throw error;
    }
  },

  // Get all orders
  getOrders: async (status = null) => {
    try {
      const params = status ? { status } : {};
      const response = await api.get('/admin/orders', { params });
      return response.data;
    } catch (error) {
      
      throw error;
    }
  },

  // Get order statistics
  getOrderStats: async () => {
    try {
      const response = await api.get('/admin/stats/orders');
      return response.data;
    } catch (error) {
      
      throw error;
    }
  },

  // Mark an order as paid
  markOrderAsPaid: async (orderId) => {
    try {
      const response = await api.put(`/admin/orders/${orderId}/paid`);
      return response.data;
    } catch (error) {

      throw error;
    }
  },

  // Get completed orders for billing
  getCompletedOrdersForBilling: async () => {
    try {
      const response = await api.get('/admin/orders/completed-for-billing');
      return response.data;
    } catch (error) {

      throw error;
    }
  },

  // Get all loyalty program tiers
  getLoyaltyTiers: async () => {
    try {
      const response = await api.get('/loyalty/');
      return response.data;
    } catch (error) {
      
      throw error;
    }
  },

  // Create a new loyalty tier
  createLoyaltyTier: async (tierData) => {
    try {
      const response = await api.post('/loyalty/', tierData);
      return response.data;
    } catch (error) {
      
      throw error;
    }
  },

  // Update a loyalty tier
  updateLoyaltyTier: async (tierId, tierData) => {
    try {
      const response = await api.put(`/loyalty/${tierId}`, tierData);
      return response.data;
    } catch (error) {
      
      throw error;
    }
  },

  // Delete a loyalty tier
  deleteLoyaltyTier: async (tierId) => {
    try {
      const response = await api.delete(`/loyalty/${tierId}`);
      return response.data;
    } catch (error) {
      
      throw error;
    }
  },

  // Get all selection offers
  getSelectionOffers: async () => {
    try {
      const response = await api.get('/selection-offers/');
      return response.data;
    } catch (error) {
      
      throw error;
    }
  },

  // Create a new selection offer
  createSelectionOffer: async (offerData) => {
    try {
      const response = await api.post('/selection-offers/', offerData);
      return response.data;
    } catch (error) {
      
      throw error;
    }
  },

  // Update a selection offer
  updateSelectionOffer: async (offerId, offerData) => {
    try {
      const response = await api.put(`/selection-offers/${offerId}`, offerData);
      return response.data;
    } catch (error) {
      
      throw error;
    }
  },

  // Delete a selection offer
  deleteSelectionOffer: async (offerId) => {
    try {
      const response = await api.delete(`/selection-offers/${offerId}`);
      return response.data;
    } catch (error) {
      
      throw error;
    }
  },

  // Get all tables
  getTables: async () => {
    try {
      const response = await api.get('/tables/');
      return response.data;
    } catch (error) {
      
      throw error;
    }
  },

  // Get table status summary
  getTableStatus: async () => {
    try {
      const response = await api.get('/tables/status/summary');
      return response.data;
    } catch (error) {
      
      throw error;
    }
  },

  // Create a new table
  createTable: async (tableData) => {
    try {
      const response = await api.post('/tables/', tableData);
      return response.data;
    } catch (error) {
      
      throw error;
    }
  },

  // Create multiple tables at once
  createTablesBatch: async (numTables) => {
    try {
      const response = await api.post(`/tables/batch?num_tables=${numTables}`);
      return response.data;
    } catch (error) {
      
      throw error;
    }
  },

  // Update a table
  updateTable: async (tableId, tableData) => {
    try {
      const response = await api.put(`/tables/${tableId}`, tableData);
      return response.data;
    } catch (error) {
      
      throw error;
    }
  },

  // Delete a table
  deleteTable: async (tableId) => {
    try {
      const response = await api.delete(`/tables/${tableId}`);
      return response.data;
    } catch (error) {
      
      throw error;
    }
  },

  // Set a table as occupied
  setTableOccupied: async (tableId, orderId = null) => {
    try {
      const url = orderId ? `/tables/${tableId}/occupy?order_id=${orderId}` : `/tables/${tableId}/occupy`;
      const response = await api.put(url);
      return response.data;
    } catch (error) {
      
      throw error;
    }
  },

  // Set a table as occupied by table number
  setTableOccupiedByNumber: async (tableNumber) => {
    try {
      const response = await api.put(`/tables/number/${tableNumber}/occupy`);
      return response.data;
    } catch (error) {
      
      throw error;
    }
  },

  // Set a table as free
  setTableFree: async (tableId) => {
    try {
      const response = await api.put(`/tables/${tableId}/free`);
      return response.data;
    } catch (error) {
      
      throw error;
    }
  },
};

// Analytics API services
export const analyticsService = {
  // Get dashboard statistics
  getDashboardStats: async (startDate = null, endDate = null) => {
    try {
      let url = '/analytics/dashboard';
      const params = new URLSearchParams();

      if (startDate) {
        params.append('start_date', startDate);
      }

      if (endDate) {
        params.append('end_date', endDate);
      }

      const queryString = params.toString();
      if (queryString) {
        url += `?${queryString}`;
      }

      const response = await api.get(url);
      return response.data;
    } catch (error) {
      
      throw error;
    }
  },

  // Get top customers
  getTopCustomers: async (limit = 10, startDate = null, endDate = null) => {
    try {
      const params = new URLSearchParams();
      params.append('limit', limit);

      if (startDate) {
        params.append('start_date', startDate);
      }

      if (endDate) {
        params.append('end_date', endDate);
      }

      const response = await api.get(`/analytics/top-customers?${params.toString()}`);
      return response.data;
    } catch (error) {
      
      throw error;
    }
  },

  // Get top dishes
  getTopDishes: async (limit = 10, startDate = null, endDate = null) => {
    try {
      const params = new URLSearchParams();
      params.append('limit', limit);

      if (startDate) {
        params.append('start_date', startDate);
      }

      if (endDate) {
        params.append('end_date', endDate);
      }

      const response = await api.get(`/analytics/top-dishes?${params.toString()}`);
      return response.data;
    } catch (error) {
      
      throw error;
    }
  },

  // Get sales by category
  getSalesByCategory: async (startDate = null, endDate = null) => {
    try {
      let url = '/analytics/sales-by-category';
      const params = new URLSearchParams();

      if (startDate) {
        params.append('start_date', startDate);
      }

      if (endDate) {
        params.append('end_date', endDate);
      }

      const queryString = params.toString();
      if (queryString) {
        url += `?${queryString}`;
      }

      const response = await api.get(url);
      return response.data;
    } catch (error) {
      
      throw error;
    }
  },

  // Get sales over time
  getSalesOverTime: async (days = 30, startDate = null, endDate = null) => {
    try {
      const params = new URLSearchParams();
      params.append('days', days);

      if (startDate) {
        params.append('start_date', startDate);
      }

      if (endDate) {
        params.append('end_date', endDate);
      }

      const response = await api.get(`/analytics/sales-over-time?${params.toString()}`);
      return response.data;
    } catch (error) {
      
      throw error;
    }
  },

  // Get chef performance metrics
  getChefPerformance: async (days = 30, startDate = null, endDate = null) => {
    try {
      const params = new URLSearchParams();
      params.append('days', days);

      if (startDate) {
        params.append('start_date', startDate);
      }

      if (endDate) {
        params.append('end_date', endDate);
      }

      const response = await api.get(`/analytics/chef-performance?${params.toString()}`);
      return response.data;
    } catch (error) {
      
      throw error;
    }
  },

  // Get table utilization statistics
  getTableUtilization: async (startDate = null, endDate = null) => {
    try {
      let url = '/analytics/table-utilization';
      const params = new URLSearchParams();

      if (startDate) {
        params.append('start_date', startDate);
      }

      if (endDate) {
        params.append('end_date', endDate);
      }

      const queryString = params.toString();
      if (queryString) {
        url += `?${queryString}`;
      }

      const response = await api.get(url);
      return response.data;
    } catch (error) {
      
      throw error;
    }
  },

  // Get customer visit frequency analysis
  getCustomerFrequency: async (startDate = null, endDate = null) => {
    try {
      let url = '/analytics/customer-frequency';
      const params = new URLSearchParams();

      if (startDate) {
        params.append('start_date', startDate);
      }

      if (endDate) {
        params.append('end_date', endDate);
      }

      const queryString = params.toString();
      if (queryString) {
        url += `?${queryString}`;
      }

      const response = await api.get(url);
      return response.data;
    } catch (error) {
      
      throw error;
    }
  },

  // Get feedback analysis
  getFeedbackAnalysis: async (startDate = null, endDate = null) => {
    try {
      let url = '/analytics/feedback-analysis';
      const params = new URLSearchParams();

      if (startDate) {
        params.append('start_date', startDate);
      }

      if (endDate) {
        params.append('end_date', endDate);
      }

      const queryString = params.toString();
      if (queryString) {
        url += `?${queryString}`;
      }

      const response = await api.get(url);
      return response.data;
    } catch (error) {
      
      throw error;
    }
  },
};

export default api;
