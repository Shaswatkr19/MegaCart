// Navbar.js
import React, { useState } from 'react';
import './Navbar.css';
import UserProfile from './auth/UserProfile';

const Navbar = ({
  cartItemCount,
  onCartClick,
  onLogoClick,
  isAuthenticated,
  user,
  logout,           // App.js ka handleLogout
  onLoginClick,     // App.js ka setShowLogin
  onNavigation,
  onSearchClick
}) => {
  const [showProfile, setShowProfile] = useState(false);

  return (
    <nav className="navbar">
      <div className="nav-container">
        {/* Logo */}
        <div className="nav-logo" onClick={onLogoClick}>
          <span className="logo-text">MegaCart</span>
          <span className="logo-icon">🛒</span>
        </div>

        {/* Navigation Links */}
        <div className="nav-links">
          <button className="nav-link" onClick={() => onNavigation('home')}>Home</button>
          <button className="nav-link" onClick={() => onNavigation('products')}>Products</button>
          <button className="nav-link" onClick={() => onNavigation('deals')}>Deals</button>
          <button className="nav-link" onClick={() => onNavigation('contact')}>Contact</button>
          <button className="nav-link" onClick={() => onNavigation('about')}>About Us</button>
        </div>

        {/* Right Side */}
        <div className="nav-right">
          {/* Search */}
          <button className="nav-icon-btn" onClick={onSearchClick} title="Search">
            🔍
          </button>

          {/* Auth buttons */}
          {!isAuthenticated ? (
            <button className="login-btn" onClick={onLoginClick}>
              Login
            </button>
          ) : (
            <>
              <span className="welcome-msg">Welcome, {user?.name || user?.email}!</span>
              <button
                className="profile-btn"
                onClick={() => setShowProfile(true)}
                title="View Profile"
              >
                👤 Profile
              </button>
              <button
                className="logout-btn"
                onClick={logout}
                title="Logout"
              >
                Logout
              </button>
            </>
          )}

          {/* Cart */}
          <button className="cart-btn" onClick={onCartClick} title="Shopping Cart">
            🛒
            {cartItemCount > 0 && <span className="cart-badge">{cartItemCount}</span>}
          </button>
        </div>
      </div>

      {/* Profile Modal */}
      {showProfile && (
        <UserProfile onClose={() => setShowProfile(false)} />
      )}
    </nav>
  );
};

export default Navbar;