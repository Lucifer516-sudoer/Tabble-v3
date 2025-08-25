import api from './api';

export const masterApiService = {
  /**
   * Fetches a list of all hotels from the server.
   * @param {string} masterPassword - The master password for authentication.
   * @returns {Promise<Array>} A promise that resolves to an array of hotel objects.
   */
  getHotels: async (masterPassword) => {
    try {
      const response = await api.get('/master/hotels', {
        headers: {
          'X-Master-Password': masterPassword,
        },
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching hotels:', error.response?.data || error.message);
      throw error.response?.data || new Error('Failed to fetch hotels');
    }
  },

  /**
   * Creates a new hotel.
   * @param {object} hotelData - The data for the new hotel.
   * @param {string} hotelData.hotel_name - The name of the new hotel.
   * @param {string} hotelData.password - The password for the new hotel.
   * @param {string} masterPassword - The master password for authentication.
   * @returns {Promise<object>} A promise that resolves to the newly created hotel object.
   */
  createHotel: async (hotelData, masterPassword) => {
    try {
      const response = await api.post('/master/hotels', hotelData, {
        headers: {
          'X-Master-Password': masterPassword,
        },
      });
      return response.data;
    } catch (error) {
      console.error('Error creating hotel:', error.response?.data || error.message);
      throw error.response?.data || new Error('Failed to create hotel');
    }
  },

  /**
   * Updates an existing hotel's details.
   * @param {number} hotelId - The ID of the hotel to update.
   * @param {object} hotelData - The data to update.
   * @param {string} [hotelData.hotel_name] - The new name of the hotel.
   * @param {string} [hotelData.password] - The new password for the hotel.
   * @param {string} masterPassword - The master password for authentication.
   * @returns {Promise<object>} A promise that resolves to the updated hotel object.
   */
  updateHotel: async (hotelId, hotelData, masterPassword) => {
    try {
      const response = await api.put(`/master/hotels/${hotelId}`, hotelData, {
        headers: {
          'X-Master-Password': masterPassword,
        },
      });
      return response.data;
    } catch (error) {
      console.error(`Error updating hotel ${hotelId}:`, error.response?.data || error.message);
      throw error.response?.data || new Error('Failed to update hotel');
    }
  },
};
