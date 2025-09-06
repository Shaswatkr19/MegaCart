import React, { useState } from 'react';
import './ProductCard.css';

const ProductCard = ({ product, onProductClick, onAddToCart }) => {
  const [imageLoading, setImageLoading] = useState(true);
  const [imageError, setImageError] = useState(false);

  const handleImageLoad = () => {
    setImageLoading(false);
  };

  const handleImageError = () => {
    setImageLoading(false);
    setImageError(true);
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(price);
  };

  const renderStars = (rating) => {
    const stars = [];
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 !== 0;

    for (let i = 0; i < fullStars; i++) {
      stars.push(
        <span key={i} className="star filled">★</span>
      );
    }

    if (hasHalfStar) {
      stars.push(
        <span key="half" className="star half">★</span>
      );
    }

    const emptyStars = 5 - Math.ceil(rating);
    for (let i = 0; i < emptyStars; i++) {
      stars.push(
        <span key={`empty-${i}`} className="star empty">☆</span>
      );
    }

    return stars;
  };

  return (
    <div className="product-card">
      {/* Product Image */}
      <div className="product-image-container" onClick={onProductClick}>
        {imageLoading && (
          <div className="image-loading">
            <div className="image-spinner"></div>
          </div>
        )}
        
        {imageError ? (
          <div className="image-placeholder">
            <span>📷</span>
            <p>Image not available</p>
          </div>
        ) : (
          <img
            src={product.image}
            alt={product.name}
            className="product-image"
            onLoad={handleImageLoad}
            onError={handleImageError}
            style={{ display: imageLoading ? 'none' : 'block' }}
          />
        )}

        {/* Stock Badge */}
        {!product.inStock && (
          <div className="stock-badge out-of-stock">
            Out of Stock
          </div>
        )}

        {/* Quick View Button */}
        <div className="quick-view-btn">
          <button>Quick View</button>
        </div>
      </div>

      {/* Product Info */}
      <div className="product-info">
        <div className="product-category">{product.category}</div>
        <h3 className="product-name" onClick={onProductClick}>
          {product.name}
        </h3>
        <p className="product-description">{product.description}</p>
        
        {/* Rating */}
        <div className="product-rating">
          <div className="stars">
            {renderStars(product.rating)}
          </div>
          <span className="rating-text">
            {product.rating} ({product.reviews} reviews)
          </span>
        </div>

        {/* Price and Add to Cart */}
        <div className="product-footer">
          <div className="product-price">
            {formatPrice(product.price)}
          </div>
          <button
            className={`add-to-cart-btn ${!product.inStock ? 'disabled' : ''}`}
            onClick={onAddToCart}
            disabled={!product.inStock}
          >
            {product.inStock ? (
              <>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 7M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17"></path>
                  <circle cx="9" cy="20" r="1"></circle>
                  <circle cx="20" cy="20" r="1"></circle>
                </svg>
                Add to Cart
              </>
            ) : (
              'Out of Stock'
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProductCard;