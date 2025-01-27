import React from 'react';
import { Routes, Route } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import ChatbotPage from './pages/ChatbotPage';

const App = () => {
  return (
    <Routes>
      <Route path="/" element={<LoginPage />} />
      <Route path="/chatbot" element={<ChatbotPage />} />
    </Routes>
  );
};

export default App;