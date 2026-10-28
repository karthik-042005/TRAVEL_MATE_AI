import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 120000, // 2 minutes for LLM calls
  headers: { 'Content-Type': 'application/json' },
});

// Response interceptor for error normalization
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail ||
      error.message ||
      'An unexpected error occurred';
    return Promise.reject(new Error(message));
  }
);

export const travelApi = {
  /**
   * Check backend health
   */
  health: () => api.get('/health'),

  /**
   * Get tool configuration status (no keys exposed)
   */
  toolStatus: () => api.get('/api/v1/tools/status'),

  /**
   * Generate a new travel plan
   * @param {string} message - Natural language travel request
   * @param {string|null} sessionId - Optional existing session ID
   */
  planTrip: (message, sessionId = null) =>
    api.post('/api/v1/travel/plan', { message, session_id: sessionId }),

  /**
   * Continue a travel planning conversation
   * @param {string} message - Follow-up message
   * @param {string} sessionId - Existing session ID
   */
  chat: (message, sessionId) =>
    api.post('/api/v1/chat', { message, session_id: sessionId }),
};

export default api;
