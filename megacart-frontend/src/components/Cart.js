import React from 'react';
import './Cart.css';

const Cart = ({ cart, updateQuantity, removeFromCart, totalPrice, onContinueShopping }) => {
  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(price);
  };

  if (cart.length === 0) {
    return (
      <div className="cart-empty">
        <div className="cart-empty-content">
          <div className="empty-cart-icon">🛒</div>
          <h2>Your cart is empty</h2>
          <p>Add some products to get started!</p>
          <button className="continue-shopping-btn" onClick={onContinueShopping}>
            Continue Shopping
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="cart-container">
      <div className="cart-header">
        <button className="back-btn" onClick={onContinueShopping}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <polyline points="15,18 9,12 15,6"></polyline>
          </svg>
          Continue Shopping
        </button>
        <h1>Shopping Cart ({cart.length} items)</h1>
      </div>

      <div className="cart-content">
        <div className="cart-items">
          {cart.map((item, index) => (
            <div key={`cart-item-${item.id}-${index}`} className="cart-item">
              <div className="item-image">
                <img src={item.image} alt={item.name} />
              </div>
              
              <div className="item-details">
                <h3>{item.name}</h3>
                <p className="item-category">{item.category}</p>
                <p className="item-description">{item.description}</p>
                
                <div className="item-rating">
                  <div className="stars">
                    {[...Array(5)].map((_, i) => (
                      <span key={`star-${item.id}-${i}`} className={`star ${i < Math.floor(item.rating) ? 'filled' : ''}`}>
                        ★
                      </span>
                    ))}
                  </div>
                  <span className="rating-text">{item.rating}</span>
                </div>
              </div>

              <div className="item-controls">
                <div className="quantity-controls">
                  <button
                    className="quantity-btn"
                    onClick={() => updateQuantity(item.id, item.quantity - 1)}
                  >
                    -
                  </button>
                  <span className="quantity">{item.quantity}</span>
                  <button
                    className="quantity-btn"
                    onClick={() => updateQuantity(item.id, item.quantity + 1)}
                  >
                    +
                  </button>
                </div>
                
                <div className="item-price">
                  {formatPrice(item.price * item.quantity)}
                </div>
                
                <button
                  className="remove-btn"
                  onClick={() => removeFromCart(item.id)}
                  title="Remove from cart"
                >
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <polyline points="3,6 5,6 21,6"></polyline>
                    <path d="m19,6v14a2,2 0 0,1 -2,2H7a2,2 0 0,1 -2,-2V6m3,0V4a2,2 0 0,1 2,-2h4a2,2 0 0,1 2,2v2"></path>
                    <line x1="10" y1="11" x2="10" y2="17"></line>
                    <line x1="14" y1="11" x2="14" y2="17"></line>
                  </svg>
                </button>
              </div>
            </div>
          ))}
        </div>

        <div className="cart-summary">
          <div className="summary-card">
            <h2>Order Summary</h2>
            
            <div className="summary-details">
              <div className="summary-row">
                <span>Subtotal:</span>
                <span>{formatPrice(totalPrice)}</span>
              </div>
              <div className="summary-row">
                <span>Shipping:</span>
                <span className="free">FREE</span>
              </div>
              <div className="summary-row">
                <span>Tax:</span>
                <span>{formatPrice(totalPrice * 0.18)}</span>
              </div>
              <hr />
              <div className="summary-row total">
                <span>Total:</span>
                <span>{formatPrice(totalPrice + (totalPrice * 0.18))}</span>
              </div>
            </div>

            <div className="promo-code">
              <input type="text" placeholder="Enter promo code" />
              <button>Apply</button>
            </div>

            <button className="checkout-btn">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                <path d="m7,11V7a5,5 0 0,1 10,0v4"></path>
              </svg>
              Proceed to Checkout
            </button>

            <div className="payment-methods">
              <p>We accept:</p>
              <div className="payment-icons">
                <span>💳</span>
                <span>🏦</span>
                <span>📱</span>
                <span>💰</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Cart;