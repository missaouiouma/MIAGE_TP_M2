import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { loginUser } from '../api/api';

const LoginPage = () => {
    const [formData, setFormData] = useState({ username: '', password: '' });
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
        setError('');
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await loginUser(formData);
            const userId = response.data.user_id; // Récupérer l'user_id
            navigate('/chatbot', { state: { userId } }); // Passer l'user_id à la page Chatbot
        } catch (err) {
            console.error('Erreur lors de la connexion :', err.response?.data || err.message);
            setError(err.response?.data?.detail || 'Nom d’utilisateur ou mot de passe incorrect');
        }
    };

    const handleRegisterClick = () => {
        navigate('/register');
    };

    return (
        <div style={{ backgroundColor: '#e0f7fa', padding: '20px', borderRadius: '8px', maxWidth: '400px', margin: 'auto', marginTop: '50px' }}>
            <h2 style={{ color: '#0077b6', textAlign: 'center' }}>Connexion</h2>
            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                <input
                    type="text"
                    name="username"
                    placeholder="Nom d'utilisateur"
                    value={formData.username}
                    onChange={handleChange}
                    style={{ padding: '10px', borderRadius: '4px', border: '1px solid #ccc' }}
                />
                <input
                    type="password"
                    name="password"
                    placeholder="Mot de passe"
                    value={formData.password}
                    onChange={handleChange}
                    style={{ padding: '10px', borderRadius: '4px', border: '1px solid #ccc' }}
                />
                {error && <p style={{ color: 'red', textAlign: 'center' }}>{error}</p>}
                <button type="submit" style={{ backgroundColor: '#0077b6', color: 'white', padding: '10px', borderRadius: '4px', border: 'none' }}>Se connecter</button>
            </form>
            <p style={{ textAlign: 'center', marginTop: '20px' }}>
                Pas encore de compte ? <span onClick={handleRegisterClick} style={{ color: '#0077b6', cursor: 'pointer' }}>S'inscrire</span>
            </p>
        </div>
    );
};

export default LoginPage;