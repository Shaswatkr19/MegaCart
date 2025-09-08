import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Check if user is logged in on app start
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      verifyToken(token);
    } else {
      setLoading(false);
    }
  }, []);

  const verifyToken = async (token) => {
    try {
      const response = await fetch('http://localhost:8000/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      } else {
        localStorage.removeItem('token');
        setUser(null);
      }
    } catch (error) {
      console.error('Token verification failed:', error);
      localStorage.removeItem('token');
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (username, password) => {
    try {
      console.log('Login attempt for:', username);
      
      const loginData = {
        email: username,
        password: password,
      };
      
      const response = await fetch('http://localhost:8000/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(loginData),
      });

      const data = await response.json();
      console.log('Login response:', { status: response.status, data });
      
      if (response.ok) {
        // Store token and set user
        localStorage.setItem('token', data.access_token);
        setUser(data.user);
        return { success: true };
      } else {
        // Handle different error types
        let errorMessage;
        
        if (response.status === 422) {
          errorMessage = data.detail || 'Please check your input';
        } else if (response.status === 401) {
          errorMessage = 'Invalid email or password';
        } else if (response.status === 500) {
          errorMessage = 'Server error. Please try again later.';
        } else {
          errorMessage = data.detail || data.message || `Login failed (${response.status})`;
        }
        
        return { success: false, error: errorMessage };
      }
    } catch (error) {
      console.error('Network error during login:', error);
      return { 
        success: false, 
        error: 'Unable to connect to server. Please check if the server is running.' 
      };
    }
  };

  const register = async (userData) => {
    try {
      console.log('Registration attempt:', { ...userData, password: '***' });
      
      const response = await fetch('http://localhost:8000/auth/register', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json' 
        },
        body: JSON.stringify(userData),
      });

      const data = await response.json();
      console.log('Registration response:', { status: response.status, data });

      if (response.ok) {
        // Store token and set user
        localStorage.setItem('token', data.access_token);
        setUser(data.user);
        return { success: true };
      } else {
        // Handle validation errors
        let errorMessage;
        
        if (response.status === 422) {
          if (Array.isArray(data.detail)) {
            errorMessage = data.detail.map(err => {
              const field = err.loc && err.loc.length > 1 ? err.loc[err.loc.length - 1] : 'Field';
              return `${field}: ${err.msg}`;
            }).join(', ');
          } else {
            errorMessage = data.detail || 'Please check your input';
          }
        } else if (response.status === 400) {
          errorMessage = data.detail || 'Registration failed';
        } else if (response.status === 500) {
          errorMessage = 'Server error. Please try again later.';
        } else {
          errorMessage = data.detail || data.message || 'Registration failed';
        }
        
        return { success: false, error: errorMessage };
      }
    } catch (error) {
      console.error('Network error during registration:', error);
      return { 
        success: false, 
        error: 'Unable to connect to server. Please check if the server is running.' 
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  const value = {
    user,
    login,
    register,
    logout,
    loading,
    isAuthenticated: !!user,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};