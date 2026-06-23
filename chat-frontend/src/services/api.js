// src/services/api.js
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8080/api/';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export const login = async (username, password) => {
  const response = await api.post('/auth/login/', { username, password });
  return response.data;
};

export const register = async (userData) => {
  const response = await api.post('/auth/register/', userData);
  return response.data;
};

// Chats
export const getChatList = async () => {
  const response = await api.get('/chats/');
  return response.data;
};

export const getChatMessages = async (chatId) => {
  const response = await api.get(`/chats/${chatId}/messages/`);
  return response.data;
};

export const sendMessage = async (recipientId, content) => {
  const response = await api.post(`/chats/${recipientId}/send_message/`, {
    recipient_id: recipientId,
    content: content,
  });
  return response.data;
};

// User search
export const searchUsers = async (query) => {
  const response = await api.get(`/users/search/?q=${query}`);
  return response.data;
};

export default api;