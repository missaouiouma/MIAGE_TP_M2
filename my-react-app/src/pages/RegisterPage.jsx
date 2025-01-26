import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { registerUser } from '../api/api';

const RegisterPage = () => {
    const [formData, setFormData] = useState({
        username: '',
        password: '',
        age: '',
        loisirs: '',
        pays_de_naissance: '',
        pays_de_residence: '',
        ville_de_residence: '',
    });
    const [error, setError] = useState('');
    const navigate = useNavigate(); // Hook pour la redirection

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
        setError('');
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await registerUser({
                ...formData,
                loisirs: formData.loisirs.split(','),
            });
            alert('Inscription réussie');
            navigate('/chatbot'); // Redirige vers la page chatbot
        } catch (err) {
            console.error('Erreur lors de l’inscription :', err.response?.data || err.message);
            setError('Erreur lors de l’inscription');
        }
    };

    return (
        <div style={{ backgroundColor: '#e0f7fa', padding: '20px', borderRadius: '8px' }}>
            <h2 style={{ color: '#0077b6' }}>Inscription</h2>
            <form onSubmit={handleSubmit}>
                <input type="text" name="username" placeholder="Nom d'utilisateur" onChange={handleChange} />
                <input type="password" name="password" placeholder="Mot de passe" onChange={handleChange} />
                <input type="number" name="age" placeholder="Âge" onChange={handleChange} />
                <input type="text" name="loisirs" placeholder="Loisirs (séparés par des virgules)" onChange={handleChange} />
                <input type="text" name="pays_de_naissance" placeholder="Pays de naissance" onChange={handleChange} />
                <input type="text" name="pays_de_residence" placeholder="Pays de résidence" onChange={handleChange} />
                <input type="text" name="ville_de_residence" placeholder="Ville de résidence" onChange={handleChange} />
                {error && <p style={{ color: 'red' }}>{error}</p>}
                <button type="submit" style={{ backgroundColor: '#0077b6', color: 'white' }}>S'inscrire</button>
            </form>
        </div>
    );
};

export default RegisterPage;
