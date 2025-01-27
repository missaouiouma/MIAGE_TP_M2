import axios from 'axios';

// Configuration de l'instance Axios
const api = axios.create({
    baseURL: 'http://localhost:8000', 
});

// Fonctions pour interagir avec l'API
export const registerUser = (data) => api.post('/chat/register', data);
export const loginUser = (data) => api.post('/chat/login', data);
export const askQuestion = (data) => api.post('/chat/ask', data);
export const getUserMessages = (userId, sessionId) => api.get(`/chat/users/${userId}/messages`, { params: { session_id: sessionId } });
export const getUserSessions = (userId) => api.get(`/chat/users/${userId}/sessions`);