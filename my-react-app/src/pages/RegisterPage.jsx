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
            await registerUser({
                ...formData,
                loisirs: formData.loisirs.split(','),
            });
            alert('Inscription réussie');
            navigate('/'); // Redirige vers la page login
        } catch (err) {
            console.error('Erreur lors de l’inscription :', err.response?.data || err.message);
            setError('Erreur lors de l’inscription');
        }
    };

    return (
        <div style={{ backgroundColor: '#e0f7fa', padding: '20px', borderRadius: '8px', maxWidth: '400px', margin: 'auto', marginTop: '50px' }}>
            <h2 style={{ color: '#0077b6', textAlign: 'center' }}>Inscription</h2>
            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                <input type="text" name="username" placeholder="Nom d'utilisateur" onChange={handleChange} style={{ padding: '10px', borderRadius: '4px', border: '1px solid #ccc' }} />
                <input type="password" name="password" placeholder="Mot de passe" onChange={handleChange} style={{ padding: '10px', borderRadius: '4px', border: '1px solid #ccc' }} />
                <input type="number" name="age" placeholder="Âge" onChange={handleChange} style={{ padding: '10px', borderRadius: '4px', border: '1px solid #ccc' }} />
                <input type="text" name="loisirs" placeholder="Loisirs (séparés par des virgules)" onChange={handleChange} style={{ padding: '10px', borderRadius: '4px', border: '1px solid #ccc' }} />
                <input type="text" name="pays_de_naissance" placeholder="Pays de naissance" onChange={handleChange} style={{ padding: '10px', borderRadius: '4px', border: '1px solid #ccc' }} />
                <input type="text" name="pays_de_residence" placeholder="Pays de résidence" onChange={handleChange} style={{ padding: '10px', borderRadius: '4px', border: '1px solid #ccc' }} />
                <input type="text" name="ville_de_residence" placeholder="Ville de résidence" onChange={handleChange} style={{ padding: '10px', borderRadius: '4px', border: '1px solid #ccc' }} />
                {error && <p style={{ color: 'red', textAlign: 'center' }}>{error}</p>}
                <button type="submit" style={{ backgroundColor: '#0077b6', color: 'white', padding: '10px', borderRadius: '4px', border: 'none' }}>S'inscrire</button>
            </form>
        </div>
    );
};

export default RegisterPage;