import React, { useState, useEffect, useCallback } from 'react';
import './App.css';
import { getProducts, getCategories, testConnection } from "./services/api";

import { AuthProvider } from './context/AuthContext';

// Components
import Navbar from './components/Navbar';
import ProductGrid from './components/ProductGrid';
import ProductDetail from './components/ProductDetail';
import Cart from './components/Cart';
import Footer from './components/Footer';

// Auth components
import Login from './components/auth/Login.js';
import Register from './components/auth/Register.js';

function App() {
  // Initialize products as empty array to prevent filter errors
  const [products, setProducts] = useState([]);
  const [cart, setCart] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [currentView, setCurrentView] = useState('home'); // 'home', 'product', 'cart'
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [loading, setLoading] = useState(false);
  const [apiConnected, setApiConnected] = useState(false);

  // Auth states
  const [showLogin, setShowLogin] = useState(false);
  const [showRegister, setShowRegister] = useState(false);

  // Categories state (dynamic from backend)
  const [categories, setCategories] = useState(['All']);

  // Safe filter products - ensure products is always an array
  const filteredProducts = React.useMemo(() => {
    if (!Array.isArray(products)) {
      console.warn('Products is not an array:', products);
      return [];
    }
    
    return products.filter(product => {
      if (!product || typeof product !== 'object') {
        return false;
      }
      
      const productName = product.name || '';
      const productCategory = product.category || '';
      
      const matchesSearch = productName.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesCategory = selectedCategory === 'All' || productCategory === selectedCategory;
      
      return matchesSearch && matchesCategory;
    });
  }, [products, searchTerm, selectedCategory]);

  // Cart functions
  const addToCart = (product, quantity = 1) => {
    setCart(prevCart => {
      const existingItem = prevCart.find(item => item.id === product.id);
      if (existingItem) {
        return prevCart.map(item =>
          item.id === product.id
            ? { ...item, quantity: item.quantity + quantity }
            : item
        );
      }
      return [...prevCart, { ...product, quantity }];
    });
  };

  const removeFromCart = (productId) => {
    setCart(prevCart => prevCart.filter(item => item.id !== productId));
  };

  const updateCartQuantity = (productId, newQuantity) => {
    if (newQuantity <= 0) {
      removeFromCart(productId);
      return;
    }
    setCart(prevCart =>
      prevCart.map(item =>
        item.id === productId ? { ...item, quantity: newQuantity } : item
      )
    );
  };

  const getTotalPrice = () => {
    return cart.reduce((total, item) => total + (item.price * item.quantity), 0);
  };

  const getTotalItems = () => {
    return cart.reduce((total, item) => total + item.quantity, 0);
  };

  // Fetch products from FastAPI with comprehensive error handling
  const fetchProducts = useCallback(async () => {
    try {
      setLoading(true);
      console.log('Fetching products...');
      
      const data = await getProducts();
      console.log('Fetched products:', data);
      console.log('Is array:', Array.isArray(data));
      
      if (Array.isArray(data)) {
        setProducts(data);
        console.log('Products set successfully:', data.length, 'items');
      } else {
        console.error('Products data is not an array:', typeof data, data);
        setProducts([]); // Ensure it's always an array
      }
      
    } catch (error) {
      console.error("Error fetching products:", error);
      setProducts([]); // Ensure it's always an array on error
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch categories from FastAPI with comprehensive error handling
  const fetchCategories = useCallback(async () => {
    try {
      console.log('Fetching categories...');
      
      const data = await getCategories();
      console.log('Fetched categories:', data);
      console.log('Is array:', Array.isArray(data));
      
      if (Array.isArray(data) && data.length > 0) {
        // Handle both string categories and category objects with name property
        const categoryNames = data.map(cat => {
          if (typeof cat === 'string') {
            return cat;
          } else if (cat && typeof cat === 'object' && cat.name) {
            return cat.name;
          }
          return null;
        }).filter(name => name && name.trim().length > 0);
        
        const uniqueCategories = [...new Set(categoryNames)];
        setCategories(['All', ...uniqueCategories]);
        console.log('Categories set successfully:', uniqueCategories);
      } else {
        // Fallback to default categories
        const defaultCategories = ['Electronics', 'Sports', 'Home', 'Accessories'];
        setCategories(['All', ...defaultCategories]);
        console.log('Using default categories');
      }
      
    } catch (error) {
      console.error('Error fetching categories:', error);
      // Fallback to default categories
      const defaultCategories = ['Electronics', 'Sports', 'Home', 'Accessories'];
      setCategories(['All', ...defaultCategories]);
    }
  }, []);

  // Test API connection and fetch data
  const initializeData = useCallback(async () => {
    try {
      console.log('Testing API connection...');
      const connected = await testConnection();
      setApiConnected(connected);
      
      if (connected) {
        console.log('API connected, fetching data...');
        await Promise.all([fetchProducts(), fetchCategories()]);
      } else {
        console.log('API not connected, using fallback data...');
        // Fallback data will be handled by the API service
        await Promise.all([fetchProducts(), fetchCategories()]);
      }
    } catch (error) {
      console.error('Error initializing data:', error);
    }
  }, [fetchProducts, fetchCategories]);

  useEffect(() => {
    initializeData();
  }, [initializeData]);

  const renderCurrentView = () => {
    switch (currentView) {
      case 'cart':
        return (
          <Cart
            cart={cart}
            updateQuantity={updateCartQuantity}
            removeFromCart={removeFromCart}
            totalPrice={getTotalPrice()}
            onContinueShopping={() => setCurrentView('home')}
          />
        );
      case 'product':
        return (
          <ProductDetail
            product={selectedProduct}
            onAddToCart={addToCart}
            onBack={() => setCurrentView('home')}
          />
        );
      default:
        return (
          <div>
            {/* API Status Indicator (for debugging) */}
            {!apiConnected && (
              <div style={{ 
                backgroundColor: '#ff6b35', 
                color: 'white', 
                padding: '8px', 
                textAlign: 'center',
                fontSize: '12px'
              }}>
                API disconnected - Using sample data
              </div>
            )}
            
            {/* Hero Section */}
            <section className="hero">
              <div className="hero-content">
                <h1>Welcome to MegaCart</h1>
                <p>Discover amazing products at unbeatable prices</p>
                <button
                  className="cta-button"
                  onClick={() => setCurrentView('home')}
                >
                  Shop Now
                </button>
              </div>
            </section>

            {/* Search and Filter Section */}
            <section className="search-filter">
              <div className="container">
                <div className="search-bar">
                  <input
                    type="text"
                    placeholder="Search products..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </div>
                <div className="category-filter">
                  {categories.map((category, index) => (
                    <button
                      key={`category-${index}-${category}`}
                      className={`category-btn ${selectedCategory === category ? 'active' : ''}`}
                      onClick={() => setSelectedCategory(category)}
                    >
                      {String(category)}
                    </button>
                  ))}
                </div>
              </div>
            </section>

            {/* Products Section */}
            <ProductGrid
              products={filteredProducts}
              onProductClick={(product) => {
                setSelectedProduct(product);
                setCurrentView('product');
              }}
              onAddToCart={addToCart}
              loading={loading}
            />
            
            {/* Debug info (remove in production) */}
            {process.env.NODE_ENV === 'development' && (
              <div style={{ 
                position: 'fixed', 
                bottom: '10px', 
                right: '10px', 
                backgroundColor: '#f0f0f0', 
                padding: '10px',
                fontSize: '10px',
                border: '1px solid #ccc',
                borderRadius: '4px',
                maxWidth: '200px'
              }}>
                <div>API: {apiConnected ? '✅ Connected' : '❌ Disconnected'}</div>
                <div>Products: {products.length}</div>
                <div>Categories: {categories.length - 1}</div>
                <div>Filtered: {filteredProducts.length}</div>
              </div>
            )}
          </div>
        );
    }
  };

  return (
    <AuthProvider>
      <div className="App">
        <Navbar
          cartItemCount={getTotalItems()}
          onCartClick={() => setCurrentView('cart')}
          onLogoClick={() => setCurrentView('home')}
          onLoginClick={() => setShowLogin(true)}
        />
        <main>
          {renderCurrentView()}
        </main>
        <Footer />

        {/* Auth Modals */}
        {showLogin && (
          <Login
            onClose={() => setShowLogin(false)}
            onSwitchToRegister={() => {
              setShowLogin(false);
              setShowRegister(true);
            }}
          />
        )}

        {showRegister && (
          <Register
            onClose={() => setShowRegister(false)}
            onSwitchToLogin={() => {
              setShowRegister(false);
              setShowLogin(true);
            }}
          />
        )}
      </div>
    </AuthProvider>
  );
}

export default App;