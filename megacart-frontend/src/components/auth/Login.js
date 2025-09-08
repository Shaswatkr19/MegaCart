import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import './Auth.css';

const Login = ({ onClose, onSwitchToRegister }) => {
  const [formData, setFormData] = useState({
    username: '', // ✅ Using username field
    password: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { login } = useAuth();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // ✅ Debug: Log form submission
    console.log('Form submitted with:', { 
      username: formData.username, 
      password: '***' 
    });

    // ✅ Basic validation
    if (!formData.username.trim() || !formData.password.trim()) {
      setError('Please fill in all fields');
      setLoading(false);
      return;
    }

    const result = await login(formData.username.trim(), formData.password);
    
    if (result.success) {
      console.log('Login successful');
      onClose();
    } else {
      console.error('Login failed:', result.error);
      setError(result.error || 'Login failed');
    }
    setLoading(false);
  };

  return (
    <div className="auth-modal">
      <div className="auth-container">
        <div className="auth-header">
          <h2>Login</h2>
          <button className="close-btn" onClick={onClose}>&times;</button>
        </div>
        
        <form onSubmit={handleSubmit}>
          {/* ✅ Safe error display */}
          {error && (
            <div className="error-message">
              {error}
            </div>
          )}
          
          <div className="form-group">
            <input
              type="email" // Keep email type for validation
              name="username" // ✅ Name matches the state field
              placeholder="Email/Username"
              value={formData.username}
              onChange={handleChange}
              required
              autoComplete="username"
            />
          </div>
          
          <div className="form-group">
            <input
              type="password"
              name="password"
              placeholder="Password"
              value={formData.password}
              onChange={handleChange}
              required
              autoComplete="current-password"
            />
          </div>
          
          <button type="submit" disabled={loading} className="auth-btn">
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>
        
        <p className="auth-switch">
          Don't have an account? 
          <button onClick={onSwitchToRegister} className="link-btn">
            Register
          </button>
        </p>
      </div>
    </div>
  );
};

export default Login;