/**
 * Login Component
 */

import React, { useState } from 'react';
import type { LoginCredentials } from '../../Types';

interface LoginProps {
  onLogin: (credentials: LoginCredentials) => Promise<void>;
  onSwitchToRegister: () => void;
  error: string | null;
  isLoading: boolean;
}

export const Login: React.FC<LoginProps> = ({
  onLogin,
  onSwitchToRegister,
  error,
  isLoading,
}) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      await onLogin({ email, password });
    } catch (err) {
      // Error handled by parent
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-box">
        <h2 className="auth-title">🔬 Research Hub Login</h2>
        
        {error && (
          <div className="error-message">
            ⚠️ {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="auth-form">
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="auth-input"
            required
            disabled={isLoading}
          />
          
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="auth-input"
            required
            disabled={isLoading}
          />
          
          <button
            type="submit"
            className="btn btn-primary"
            disabled={isLoading}
          >
            {isLoading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        <p className="auth-switch" onClick={onSwitchToRegister}>
          Create an account →
        </p>
      </div>

      <style>{`
        .auth-container {
          display: flex;
          align-items: center;
          justify-content: center;
          min-height: 100vh;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          padding: 20px;
        }

        .auth-box {
          background: white;
          padding: 40px;
          border-radius: 12px;
          box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
          width: 100%;
          max-width: 400px;
          text-align: center;
        }

        .auth-title {
          margin-bottom: 24px;
          color: #2c3e50;
          font-size: 24px;
        }

        .error-message {
          background: #fdecea;
          border: 1px solid #f5c6cb;
          color: #721c24;
          padding: 12px;
          border-radius: 6px;
          margin-bottom: 16px;
          font-size: 14px;
        }

        .auth-form {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .auth-input {
          width: 100%;
          padding: 12px;
          border: 1px solid #ddd;
          border-radius: 6px;
          font-size: 14px;
        }

        .auth-input:focus {
          outline: none;
          border-color: #667eea;
        }

        .btn {
          padding: 12px 20px;
          border: none;
          border-radius: 6px;
          font-weight: 600;
          cursor: pointer;
          transition: 0.2s;
        }

        .btn-primary {
          background: #667eea;
          color: white;
        }

        .btn-primary:hover:not(:disabled) {
          background: #5568d3;
        }

        .btn:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .auth-switch {
          margin-top: 16px;
          color: #667eea;
          cursor: pointer;
          font-size: 14px;
        }

        .auth-switch:hover {
          text-decoration: underline;
        }
      `}</style>
    </div>
  );
};