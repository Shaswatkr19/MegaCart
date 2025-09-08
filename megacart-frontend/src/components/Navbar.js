// Navbar.js
import React, { useState } from 'react';
import './Navbar.css';
import UserProfile from './auth/UserProfile';

const Navbar = ({ cartItemCount, onCartClick, onLogoClick, isAuthenticated, user, logout, onLoginClick, onNavigation }) => {
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
          {/* Search Icon */}
          <button className="nav-icon-btn">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="11" cy="11" r="8"></circle>
              <path d="m21 21-4.35-4.35"></path>
            </svg>
          </button>

          {/* User Menu */}
          {isAuthenticated ? (
            <div className="user-menu">
              <button onClick={() => setShowProfile(true)}>
                {user?.name || "Profile"}
              </button>
              <button onClick={logout}>Logout</button>
            </div>
          ) : (
            <button onClick={onLoginClick}>Login</button>
          )}

          {/* Cart */}
          <button className="cart-btn" onClick={onCartClick}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 7M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17"></path>
              <circle cx="9" cy="20" r="1"></circle>
              <circle cx="20" cy="20" r="1"></circle>
            </svg>
            {cartItemCount > 0 && (
              <span className="cart-badge">{cartItemCount}</span>
            )}
          </button>
        </div>

        {/* Mobile Menu Button */}
        <button className="mobile-menu-btn">
          <span></span>
          <span></span>
          <span></span>
        </button>
      </div>

      {/* Profile Modal */}
      {showProfile && (
        <UserProfile onClose={() => setShowProfile(false)} />
      )}
    </nav>
  );
};

export default Navbar;