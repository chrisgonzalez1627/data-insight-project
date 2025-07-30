import axios from 'axios';

// Get the API base URL from environment variables
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Debug logging
console.log('API Service initialized with base URL:', API_BASE_URL);
console.log('Environment variables:', {
  REACT_APP_API_URL: process.env.REACT_APP_API_URL,
  NODE_ENV: process.env.NODE_ENV
});

// Create axios instance with default configuration
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`Making request to: ${config.baseURL}${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// API endpoints
export const endpoints = {
  // Health check
  health: () => api.get('/health'),
  
  // Data endpoints
  getDataSources: () => api.get('/data/sources'),
  getData: (source, limit = 100) => api.get(`/data/${source}?limit=${limit}`),
  
  // Analytics endpoints
  getInsights: () => api.get('/insights'),
  getAnalytics: () => api.get('/analytics'),
  getTrends: (source, days = 30) => api.get(`/analytics/${source}/trends?days=${days}`),
  
  // Model endpoints
  getModels: () => api.get('/models'),
  makePrediction: (modelName, features) => api.post('/predict', {
    model_name: modelName,
    features: features
  }),
  
  // ETL and Model Management endpoints
  runETLPipeline: () => api.post('/etl/run'),
  trainModels: () => api.post('/models/train'),
  exportReport: () => api.get('/export/report'),
};

export default api; 