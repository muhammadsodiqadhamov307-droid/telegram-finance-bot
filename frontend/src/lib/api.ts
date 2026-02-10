import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Get Telegram WebApp initData for authentication
function getInitData(): string {
    return window.Telegram?.WebApp?.initData || '';
};

// Create axios instance
const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add auth header to every request
api.interceptors.request.use((config) => {
    const token = getAuthToken();
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// API methods
export const apiClient = {
    // User endpoints
    getProfile: () => api.get('/api/user/profile'),

    // Transaction endpoints
    getTransactions: (params?: {
        skip?: number;
        limit?: number;
        type?: string;
        category_id?: number;
        start_date?: string;
        end_date?: string;
    }) => api.get('/api/transactions', { params }),

    createTransaction: (data: {
        type: string;
        amount: number;
        category_id?: number;
        description?: string;
        transaction_date?: string;
    }) => api.post('/api/transactions', data),

    deleteTransaction: (id: number) => api.delete(`/api/transactions/${id}`),

    // Analytics endpoints
    getSummary: (days: number = 30) => api.get('/api/analytics/summary', { params: { days } }),

    getCategoryBreakdown: (days: number = 30) => api.get('/api/analytics/by-category', { params: { days } }),

    // Category endpoints
    getCategories: (type?: string) => api.get('/api/categories', { params: { type } }),
};

export default apiClient;
