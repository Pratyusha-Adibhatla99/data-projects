import React, { useState } from 'react';
import type { User } from '../../Types'; // Make sure this path points to your Types file!

interface RegisterProps {
    setUser: React.Dispatch<React.SetStateAction<User | null>>;
    onSwitchToLogin: () => void;
}

export default function Register({ setUser, onSwitchToLogin }: RegisterProps) {
    const [formData, setFormData] = useState({
        full_name: '',
        email: '',
        institution: '',
        password: '',
        confirm_password: ''
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleRegister = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        if (formData.password !== formData.confirm_password) {
            return setError('Passwords do not match.');
        }

        setLoading(true);
        try {
            const response = await fetch('http://localhost:5001/api/register', {
                method: 'POST',
                credentials: 'include', // Ensures the new session cookie is saved!
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    full_name: formData.full_name,
                    email: formData.email,
                    institution: formData.institution,
                    password: formData.password
                })
            });

            const data = await response.json();

            if (data.success) {
                // Because your Flask code does `login_user`, we instantly drop them into the app!
                setUser(data.user);
            } else {
                setError(data.error);
            }
        } catch (err) {
            setError('Failed to connect to the server.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ maxWidth: '400px', margin: '40px auto', padding: '30px', background: 'white', borderRadius: '12px', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}>
            <h2 style={{ margin: '0 0 20px 0', color: '#1e293b', textAlign: 'center' }}>Create an Account</h2>
            
            {/* 🚨 UCSD Hint */}
            <div style={{ background: '#eff6ff', borderLeft: '4px solid #3b82f6', padding: '12px', marginBottom: '20px', borderRadius: '4px', fontSize: '13px', color: '#1e3a8a' }}>
                <strong>Note:</strong> Anyone can create an account, but downloading datasets requires an authorized <strong>@ucsd.edu</strong> email address.
            </div>

            <form onSubmit={handleRegister} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                
                {error && <div style={{ color: '#b91c1c', background: '#fef2f2', padding: '10px', borderRadius: '6px', fontSize: '14px' }}>{error}</div>}

                <input required type="text" name="full_name" placeholder="Full Name" value={formData.full_name} onChange={handleChange} style={inputStyle} />
                <input required type="email" name="email" placeholder="Email Address" value={formData.email} onChange={handleChange} style={inputStyle} />
                <input type="text" name="institution" placeholder="Institution (e.g., UC San Diego)" value={formData.institution} onChange={handleChange} style={inputStyle} />
                <input required type="password" name="password" placeholder="Password" value={formData.password} onChange={handleChange} style={inputStyle} />
                <input required type="password" name="confirm_password" placeholder="Confirm Password" value={formData.confirm_password} onChange={handleChange} style={inputStyle} />

                <button disabled={loading} type="submit" style={{ background: '#3b82f6', color: 'white', padding: '12px', border: 'none', borderRadius: '6px', fontSize: '16px', cursor: loading ? 'wait' : 'pointer', marginTop: '10px' }}>
                    {loading ? 'Creating Account...' : 'Sign Up'}
                </button>
            </form>

            <p style={{ textAlign: 'center', marginTop: '20px', fontSize: '14px', color: '#64748b' }}>
                Already have an account? <span onClick={onSwitchToLogin} style={{ color: '#3b82f6', cursor: 'pointer', fontWeight: 'bold' }}>Log in here</span>
            </p>
        </div>
    );
}

const inputStyle = {
    padding: '12px', borderRadius: '6px', border: '1px solid #cbd5e1', fontSize: '15px', width: '100%', boxSizing: 'border-box' as const
};