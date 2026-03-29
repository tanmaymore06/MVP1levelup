import axios from 'axios';

const API_BASE = 'https://level-up-zt4w.onrender.com/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      if (window.location.pathname !== '/login' && window.location.pathname !== '/register') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default api;

// Auth
export const loginUser = (username: string, password: string) =>
  api.post('/auth/login/', { username, password });

export const registerUser = (username: string, password: string, email?: string) =>
  api.post('/auth/register/', { username, password, ...(email ? { email } : {}) });

export const logoutUser = () => api.post('/auth/logout/');

// Quests
export const getQuests = () => api.get('/quests/');
export const getQuestNodes = (questId: number) => api.get(`/quests/${questId}/nodes/`);

// Pages
export const getNodePages = (nodeId: number) => api.get(`/nodes/${nodeId}/pages/`);
export const completePage = (pageId: number) => api.post(`/pages/${pageId}/complete/`);

// Session
export const getSession = () => api.get('/session/');
export const completeSession = (focusNodeId: number) =>
  api.post('/session/complete/', { focus_node_id: focusNodeId });

// Dashboard
export const getDashboard = () => api.get('/dashboard/');
