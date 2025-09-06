import React from 'react';
import { useAuth } from '../../context/AuthContext';

const ProtectedRoute = ({ children, fallback }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  if (!isAuthenticated) {
    return fallback || (
      <div className="auth-required">
        <h3>Login Required</h3>
        <p>Please login to access this page.</p>
      </div>
    );
  }

  return children;
};

export default ProtectedRoute;