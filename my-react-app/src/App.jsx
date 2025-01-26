import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import ChatbotPage from './pages/ChatbotPage';

const App = () => {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<LoginPage />} />
                <Route path="/chatbot" element={<ChatbotPage />} />
            </Routes>
        </Router>
    );
};

export default App;
