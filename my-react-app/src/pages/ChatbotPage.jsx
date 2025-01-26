import React, { useState } from 'react';
import { useLocation } from 'react-router-dom';
import { askQuestion } from '../api/api';

const ChatbotPage = () => {
    const location = useLocation();
    const userId = location.state?.userId; // Récupérer l'user_id depuis l'état transmis via navigate()

    // Déclarez vos hooks ici, hors de toute condition
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');

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

    // Gérez le cas où userId est manquant via un rendu conditionnel
    if (!userId) {
        return <p style={{ color: 'red' }}>Erreur : Aucun utilisateur connecté.</p>;
    }

    return (
        <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
            <h2 style={{ textAlign: 'center', color: '#0077b6' }}>Chatbot</h2>
            <div
                style={{
                    border: '1px solid #ccc',
                    height: '300px',
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
                        <strong>{msg.role === 'user' ? 'Vous' : 'Chatbot'} :</strong>{' '}
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
    );
};

export default ChatbotPage;
