import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { getUserMessages, askQuestion } from '../api/api';

const ChatbotPage = () => {
    const location = useLocation();
    const userId = location.state?.userId;

    const [sessions, setSessions] = useState([]);
    const [selectedSession, setSelectedSession] = useState(null);
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');

    // Fetch sessions on mount
    useEffect(() => {
        const fetchSessions = async () => {
            try {
                const response = await getUserMessages(userId);
                setSessions(response.data); // Assume sessions are returned here
            } catch (error) {
                console.error('Erreur lors de la récupération des sessions :', error);
            }
        };
        fetchSessions();
    }, [userId]);

    // Load messages for the selected session
    useEffect(() => {
        if (selectedSession) {
            setMessages(selectedSession.messages);
        }
    }, [selectedSession]);

    const sendMessage = async () => {
        if (input.trim()) {
            const userMessage = { role: 'user', content: input };
            setMessages([...messages, userMessage]);

            try {
                const response = await askQuestion({ user_id: userId, question: input });
                const botResponse = { role: 'assistant', content: response.data.response };
                setMessages((prevMessages) => [...prevMessages, botResponse]);
            } catch (error) {
                console.error('Erreur lors de l’appel à l’API :', error);
                const errorResponse = { role: 'assistant', content: 'Erreur : impossible de récupérer une réponse.' };
                setMessages((prevMessages) => [...prevMessages, errorResponse]);
            }

            setInput('');
        }
    };

    if (!userId) {
        return <p style={{ color: 'red' }}>Erreur : Aucun utilisateur connecté.</p>;
    }

    return (
        <div style={{ display: 'flex', height: '100vh', fontFamily: 'Arial, sans-serif' }}>
            {/* Sidebar for sessions */}
            <div style={{ width: '25%', borderRight: '1px solid #ccc', padding: '10px', backgroundColor: '#f7f7f7' }}>
                <h3>Sessions</h3>
                <ul style={{ listStyleType: 'none', padding: 0 }}>
                    {sessions.map((session) => (
                        <li
                            key={session.id}
                            onClick={() => setSelectedSession(session)}
                            style={{
                                padding: '10px',
                                cursor: 'pointer',
                                backgroundColor: selectedSession?.id === session.id ? '#0077b6' : 'transparent',
                                color: selectedSession?.id === session.id ? '#fff' : '#000',
                                borderRadius: '5px',
                                marginBottom: '5px',
                            }}
                        >
                            {session.id}
                        </li>
                    ))}
                </ul>
            </div>

            {/* Chat messages */}
            <div style={{ flex: '1', padding: '20px' }}>
                <h2 style={{ textAlign: 'center', color: '#0077b6' }}>AItravel</h2>
                <div
                    style={{
                        border: '1px solid #ccc',
                        height: '400px',
                        overflowY: 'scroll',
                        padding: '10px',
                        borderRadius: '8px',
                        backgroundColor: '#f9f9f9',
                    }}
                >
                    {messages.map((msg, index) => (
                        <div
                            key={index}
                            style={{
                                textAlign: msg.role === 'user' ? 'right' : 'left',
                                margin: '10px 0',
                            }}
                        >
                            <strong>{msg.role === 'user' ? 'Vous' : 'AItravel'} :</strong>{' '}
                            <span
                                style={{
                                    display: 'inline-block',
                                    backgroundColor: msg.role === 'user' ? '#0077b6' : '#e0f7fa',
                                    color: msg.role === 'user' ? '#fff' : '#000',
                                    padding: '10px',
                                    borderRadius: '12px',
                                    maxWidth: '70%',
                                    wordWrap: 'break-word',
                                }}
                            >
                                {msg.content}
                            </span>
                        </div>
                    ))}
                </div>
                <div style={{ marginTop: '10px', display: 'flex', alignItems: 'center' }}>
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Tapez un message..."
                        style={{
                            flex: '1',
                            padding: '10px',
                            borderRadius: '8px',
                            border: '1px solid #ccc',
                            marginRight: '10px',
                        }}
                    />
                    <button
                        onClick={sendMessage}
                        style={{
                            backgroundColor: '#0077b6',
                            color: '#fff',
                            padding: '10px 20px',
                            borderRadius: '8px',
                            border: 'none',
                            cursor: 'pointer',
                        }}
                    >
                        Envoyer
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ChatbotPage;
