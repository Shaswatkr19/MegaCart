import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import ProtectedRoute from './ProtectedRoute';
import './Auth.css';

const UserProfile = ({ onClose }) => {
  const { user, logout } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    address: ''
  });
  const [orders, setOrders] = useState([]);
  const [activeTab, setActiveTab] = useState('profile'); // 'profile', 'orders', 'settings'

  useEffect(() => {
    if (user) {
      setFormData({
        name: user.name || '',
        email: user.email || '',
        phone: user.phone || '',
        address: user.address || ''
      });
      // Fetch user orders
      fetchOrders();
    }
  }, [user]);

  const fetchOrders = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/orders', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setOrders(data);
      }
    } catch (error) {
      console.error('Error fetching orders:', error);
    }
  };

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleUpdateProfile = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/user/profile', {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        setIsEditing(false);
        alert('Profile updated successfully!');
      } else {
        alert('Failed to update profile');
      }
    } catch (error) {
      console.error('Error updating profile:', error);
      alert('Error updating profile');
    }
  };

  const renderProfileTab = () => (
    <div className="profile-tab">
      <div className="profile-header">
        <h3>Personal Information</h3>
        <button 
          onClick={() => setIsEditing(!isEditing)}
          className="edit-btn"
        >
          {isEditing ? 'Cancel' : 'Edit'}
        </button>
      </div>

      {isEditing ? (
        <form onSubmit={handleUpdateProfile} className="profile-form">
          <div className="form-group">
            <label>Full Name</label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              required
            />
          </div>

          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              required
            />
          </div>

          <div className="form-group">
            <label>Phone</label>
            <input
              type="tel"
              name="phone"
              value={formData.phone}
              onChange={handleInputChange}
            />
          </div>

          <div className="form-group">
            <label>Address</label>
            <textarea
              name="address"
              value={formData.address}
              onChange={handleInputChange}
              rows="3"
            />
          </div>

          <button type="submit" className="save-btn">
            Save Changes
          </button>
        </form>
      ) : (
        <div className="profile-info">
          <div className="info-item">
            <strong>Name:</strong> {user?.name}
          </div>
          <div className="info-item">
            <strong>Email:</strong> {user?.email}
          </div>
          <div className="info-item">
            <strong>Phone:</strong> {user?.phone || 'Not provided'}
          </div>
          <div className="info-item">
            <strong>Address:</strong> {user?.address || 'Not provided'}
          </div>
          <div className="info-item">
            <strong>Member since:</strong> {new Date(user?.created_at).toLocaleDateString()}
          </div>
        </div>
      )}
    </div>
  );

  const renderOrdersTab = () => (
    <div className="orders-tab">
      <h3>Order History</h3>
      {orders.length === 0 ? (
        <p className="no-orders">No orders found</p>
      ) : (
        <div className="orders-list">
          {orders.map(order => (
            <div key={order.id} className="order-card">
              <div className="order-header">
                <h4>Order #{order.id}</h4>
                <span className={`status ${order.status.toLowerCase()}`}>
                  {order.status}
                </span>
              </div>
              <div className="order-details">
                <p><strong>Date:</strong> {new Date(order.created_at).toLocaleDateString()}</p>
                <p><strong>Total:</strong> ₹{order.total}</p>
                <p><strong>Items:</strong> {order.items?.length} item(s)</p>
              </div>
              <div className="order-items">
                {order.items?.map(item => (
                  <div key={item.id} className="order-item">
                    <span>{item.product_name} x {item.quantity}</span>
                    <span>₹{item.price * item.quantity}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  const renderSettingsTab = () => (
    <div className="settings-tab">
      <h3>Account Settings</h3>
      
      <div className="setting-item">
        <h4>Change Password</h4>
        <button className="setting-btn">Update Password</button>
      </div>
      
      <div className="setting-item">
        <h4>Email Notifications</h4>
        <label className="toggle-switch">
          <input type="checkbox" defaultChecked />
          <span>Receive order updates via email</span>
        </label>
      </div>
      
      <div className="setting-item">
        <h4>SMS Notifications</h4>
        <label className="toggle-switch">
          <input type="checkbox" />
          <span>Receive order updates via SMS</span>
        </label>
      </div>
      
      <div className="setting-item danger-zone">
        <h4>Danger Zone</h4>
        <button className="delete-btn">Delete Account</button>
      </div>
    </div>
  );

  return (
    <ProtectedRoute>
      <div className="auth-modal">
        <div className="profile-container">
          <div className="profile-header-main">
            <h2>My Profile</h2>
            <button className="close-btn" onClick={onClose}>&times;</button>
          </div>
          
          <div className="profile-tabs">
            <button 
              className={`tab-btn ${activeTab === 'profile' ? 'active' : ''}`}
              onClick={() => setActiveTab('profile')}
            >
              Profile
            </button>
            <button 
              className={`tab-btn ${activeTab === 'orders' ? 'active' : ''}`}
              onClick={() => setActiveTab('orders')}
            >
              Orders
            </button>
            <button 
              className={`tab-btn ${activeTab === 'settings' ? 'active' : ''}`}
              onClick={() => setActiveTab('settings')}
            >
              Settings
            </button>
          </div>

          <div className="profile-content">
            {activeTab === 'profile' && renderProfileTab()}
            {activeTab === 'orders' && renderOrdersTab()}
            {activeTab === 'settings' && renderSettingsTab()}
          </div>

          <div className="profile-actions">
            <button onClick={logout} className="logout-btn">
              Logout
            </button>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
};

export default UserProfile;