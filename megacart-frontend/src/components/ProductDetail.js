import React, { useState } from 'react';
import './ProductDetail.css';

const ProductDetail = ({ product, onAddToCart, onBack }) => {
  const [quantity, setQuantity] = useState(1);
  const [selectedTab, setSelectedTab] = useState('description');

  if (!product) {
    return <div>Product not found</div>;
  }

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(price);
  };

  const renderStars = (rating) => {
    const stars = [];
    for (let i = 0; i < 5; i++) {
      stars.push(
        <span key={i} className={`star ${i < Math.floor(rating) ? 'filled' : ''}`}>
          ★
        </span>
      );
    }
    return stars;
  };

  const handleQuantityChange = (change) => {
    const newQuantity = quantity + change;
    if (newQuantity >= 1) {
      setQuantity(newQuantity);
    }
  };

  const handleAddToCart = () => {
    onAddToCart(product, quantity);
    // Show success message or animation
    alert(`Added ${quantity} ${product.name}(s) to cart!`);
  };

  return (
    <div className="product-detail-container">
      <div className="product-detail-header">
        <button className="back-btn" onClick={onBack}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <polyline points="15,18 9,12 15,6"></polyline>
          </svg>
          Back to Products
        </button>
      </div>

      <div className="product-detail-content">
        {/* Product Images */}
        <div className="product-images">
          <div className="main-image">
            <img src={product.image} alt={product.name} />
          </div>
          <div className="thumbnail-images">
            <div className="thumbnail active">
              <img src={product.image} alt={product.name} />
            </div>
            <div className="thumbnail">
              <img src={product.image} alt={product.name} />
            </div>
            <div className="thumbnail">
              <img src={product.image} alt={product.name} />
            </div>
          </div>
        </div>

        {/* Product Info */}
        <div className="product-info">
          <div className="product-category">{product.category}</div>
          <h1 className="product-title">{product.name}</h1>
          
          <div className="product-rating">
            <div className="stars">
              {renderStars(product.rating)}
            </div>
            <span className="rating-text">
              {product.rating} ({product.reviews} reviews)
            </span>
          </div>

          <div className="product-price">
            <span className="current-price">{formatPrice(product.price)}</span>
            <span className="original-price">{formatPrice(product.price * 1.2)}</span>
            <span className="discount">17% OFF</span>
          </div>

          <div className="stock-status">
            {product.inStock ? (
              <span className="in-stock">✅ In Stock</span>
            ) : (
              <span className="out-of-stock">❌ Out of Stock</span>
            )}
          </div>

          <div className="product-description">
            <p>{product.description}</p>
          </div>

          {/* Quantity and Add to Cart */}
          <div className="purchase-section">
            <div className="quantity-selector">
              <label>Quantity:</label>
              <div className="quantity-controls">
                <button onClick={() => handleQuantityChange(-1)}>-</button>
                <span className="quantity">{quantity}</span>
                <button onClick={() => handleQuantityChange(1)}>+</button>
              </div>
            </div>

            <div className="action-buttons">
              <button
                className={`add-to-cart-btn ${!product.inStock ? 'disabled' : ''}`}
                onClick={handleAddToCart}
                disabled={!product.inStock}
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 7M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17"></path>
                  <circle cx="9" cy="20" r="1"></circle>
                  <circle cx="20" cy="20" r="1"></circle>
                </svg>
                Add to Cart
              </button>
              
              <button className="buy-now-btn">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                  <path d="m7,11V7a5,5 0 0,1 10,0v4"></path>
                </svg>
                Buy Now
              </button>
            </div>
          </div>

          {/* Product Features */}
          <div className="product-features">
            <div className="feature">
              <span className="feature-icon">🚚</span>
              <div>
                <strong>Free Delivery</strong>
                <p>On orders above ₹499</p>
              </div>
            </div>
            <div className="feature">
              <span className="feature-icon">↩️</span>
              <div>
                <strong>Easy Returns</strong>
                <p>30 days return policy</p>
              </div>
            </div>
            <div className="feature">
              <span className="feature-icon">🔒</span>
              <div>
                <strong>Secure Payment</strong>
                <p>100% secure payments</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Product Tabs */}
      <div className="product-tabs">
        <div className="tab-buttons">
          <button
            className={`tab-btn ${selectedTab === 'description' ? 'active' : ''}`}
            onClick={() => setSelectedTab('description')}
          >
            Description
          </button>
          <button
            className={`tab-btn ${selectedTab === 'specifications' ? 'active' : ''}`}
            onClick={() => setSelectedTab('specifications')}
          >
            Specifications
          </button>
          <button
            className={`tab-btn ${selectedTab === 'reviews' ? 'active' : ''}`}
            onClick={() => setSelectedTab('reviews')}
          >
            Reviews ({product.reviews})
          </button>
        </div>

        <div className="tab-content">
          {selectedTab === 'description' && (
            <div className="tab-panel">
              <h3>Product Description</h3>
              <p>{product.description}</p>
              <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.</p>
              <ul>
                <li>High-quality materials</li>
                <li>Durable construction</li>
                <li>Modern design</li>
                <li>Easy to use</li>
              </ul>
            </div>
          )}

          {selectedTab === 'specifications' && (
            <div className="tab-panel">
              <h3>Technical Specifications</h3>
              <table className="specs-table">
                <tbody>
                  <tr>
                    <td>Brand</td>
                    <td>MegaCart</td>
                  </tr>
                  <tr>
                    <td>Category</td>
                    <td>{product.category}</td>
                  </tr>
                  <tr>
                    <td>Weight</td>
                    <td>1.2 kg</td>
                  </tr>
                  <tr>
                    <td>Dimensions</td>
                    <td>25 x 15 x 10 cm</td>
                  </tr>
                  <tr>
                    <td>Warranty</td>
                    <td>1 Year</td>
                  </tr>
                </tbody>
              </table>
            </div>
          )}

          {selectedTab === 'reviews' && (
            <div className="tab-panel">
              <h3>Customer Reviews</h3>
              <div className="reviews-summary">
                <div className="rating-breakdown">
                  <div className="overall-rating">
                    <span className="rating-number">{product.rating}</span>
                    <div className="stars">
                      {renderStars(product.rating)}
                    </div>
                    <span>({product.reviews} reviews)</span>
                  </div>
                </div>
              </div>
              
              <div className="review-item">
                <div className="reviewer">
                  <strong>John Doe</strong>
                  <div className="stars">
                    {renderStars(5)}
                  </div>
                </div>
                <p>Amazing product! Great quality and fast delivery. Highly recommended!</p>
                <span className="review-date">2 days ago</span>
              </div>
              
              <div className="review-item">
                <div className="reviewer">
                  <strong>Jane Smith</strong>
                  <div className="stars">
                    {renderStars(4)}
                  </div>
                </div>
                <p>Good value for money. Works as expected. Would buy again.</p>
                <span className="review-date">1 week ago</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}; // Added this closing brace and semicolon

export default ProductDetail;