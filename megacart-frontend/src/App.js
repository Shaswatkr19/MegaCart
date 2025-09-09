import React, { useState, useEffect, useCallback, useRef } from 'react';
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
  const [currentView, setCurrentView] = useState('home'); // 'home', 'product', 'cart', 'products', 'categories', 'deals', 'contact'
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [loading, setLoading] = useState(false);
  const [apiConnected, setApiConnected] = useState(false);
  

  // Auth states
  const [showLogin, setShowLogin] = useState(false);
  const [showRegister, setShowRegister] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null); // Removed setUser since it's not being used
  
  // Categories state (dynamic from backend)
  const [categories, setCategories] = useState(['All']);

  // Ref for scrolling to products section
  const productsRef = useRef(null);

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

  console.log('Product images:', filteredProducts.map(p => ({ name: p.name, image: p.image })));

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
  
  // // Authentication handlers
  // const handleLogin = (userData) => {
  //   setIsAuthenticated(true);
  //   setUser(userData);
  //   setShowLogin(false);
  // };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setUser(null);
  };

  // Navigation handlers
  const handleNavigation = (view) => {
    setCurrentView(view);
    // Reset search and category when navigating
    if (view === 'home' || view === 'products') {
      setSearchTerm('');
      setSelectedCategory('All');
    }
  };

  // Handle Shop Now button click
  const handleShopNowClick = () => {
    // Smooth scroll to products section
    if (productsRef.current) {
      productsRef.current.scrollIntoView({ 
        behavior: 'smooth',
        block: 'start'
      });
    }
  };

  // Handle search button click from navbar
  const handleSearchClick = () => {
    // Navigate to products page and scroll to search
    setCurrentView('products');
    // Small delay to ensure the view has changed before scrolling
    setTimeout(() => {
      if (productsRef.current) {
        productsRef.current.scrollIntoView({ 
          behavior: 'smooth',
          block: 'start'
        });
      }
    }, 100);
  };
  

  // // Navigation handlers
  // const handleNavigation = (view) => {
  //   setCurrentView(view);
  //   // Reset search and category when navigating
  //   if (view === 'home' || view === 'products') {
  //     setSearchTerm('');
  //     setSelectedCategory('All');
  //   }
  // };

  

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
        // Fallback sample data if API fails
        const fallbackProducts = [
          {
            id: 1,
            name: "Wireless Headphones",
            description: "High-quality wireless headphones with noise cancellation",
            price: 99.99,
            category: "Electronics",
            image: "🎧"
          },
          {
            id: 2,
            name: "Running Shoes",
            description: "Comfortable running shoes for all terrains",
            price: 79.99,
            category: "Sports",
            image: "👟"
          },
          {
            id: 3,
            name: "Coffee Maker",
            description: "Automatic coffee maker with programmable timer",
            price: 129.99,
            category: "Home",
            image: "☕"
          },
          {
            id: 4,
            name: "Smartwatch",
            description: "Fitness tracking smartwatch with heart rate monitor",
            price: 199.99,
            category: "Electronics",
            image: "⌚"
          },
          {
            id: 5,
            name: "Yoga Mat",
            description: "Non-slip yoga mat for all your exercise needs",
            price: 29.99,
            category: "Sports",
            image: "🧘"
          },
          {
            id: 6,
            name: "Desk Lamp",
            description: "LED desk lamp with adjustable brightness",
            price: 39.99,
            category: "Home",
            image: "💡"
          }
        ];
        setProducts(fallbackProducts);
      }
      
    } catch (error) {
      console.error("Error fetching products:", error);
      // Fallback sample data on error
      const fallbackProducts = [
        {
          id: 1,
          name: "Wireless Headphones",
          description: "High-quality wireless headphones with noise cancellation",
          price: 99.99,
          category: "Electronics",
          image: "🎧"
        },
        {
          id: 2,
          name: "Running Shoes",
          description: "Comfortable running shoes for all terrains",
          price: 79.99,
          category: "Sports",
          image: "👟"
        },
        {
          id: 3,
          name: "Coffee Maker",
          description: "Automatic coffee maker with programmable timer",
          price: 129.99,
          category: "Home",
          image: "☕"
        },
        {
          id: 4,
          name: "Smartwatch",
          description: "Fitness tracking smartwatch with heart rate monitor",
          price: 199.99,
          category: "Electronics",
          image: "⌚"
        },
        {
          id: 5,
          name: "Yoga Mat",
          description: "Non-slip yoga mat for all your exercise needs",
          price: 29.99,
          category: "Sports",
          image: "🧘"
        },
        {
          id: 6,
          name: "Desk Lamp",
          description: "LED desk lamp with adjustable brightness",
          price: 39.99,
          category: "Home",
          image: "💡"
        }
      ];
      setProducts(fallbackProducts);
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
        // Fallback data will be handled by the fetch functions
        await Promise.all([fetchProducts(), fetchCategories()]);
      }
    } catch (error) {
      console.error('Error initializing data:', error);
      // Ensure we always have some data
      await Promise.all([fetchProducts(), fetchCategories()]);
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
      case 'products':
        return (
          <div>
            {/* Search and Filter Section */}
            <section className="search-filter" ref={productsRef}>
              <div className="container">
                <h2>All Products</h2>
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

            {/* Products Grid */}
            <ProductGrid
              products={filteredProducts}
              onProductClick={(product) => {
                setSelectedProduct(product);
                setCurrentView('product');
              }}
              onAddToCart={addToCart}
              loading={loading}
            />
          </div>
        );
      case 'deals':
        return (
          <div style={{ minHeight: '100vh', background: '#f8f9fa' }}>
            {/* Hero Section */}
            <section style={{
              background: 'linear-gradient(135deg, #ff6b6b 0%, #ee5a24 50%, #ff4757 100%)',
              padding: '60px 20px 40px',
              textAlign: 'center',
              color: 'white'
            }}>
              <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
                <h1 style={{ 
                  fontSize: '3rem', 
                  marginBottom: '20px', 
                  fontWeight: '700',
                  textShadow: '2px 2px 4px rgba(0,0,0,0.3)'
                }}>
                  🔥 MEGA DEALS 🔥
                </h1>
                <p style={{ 
                  fontSize: '1.2rem', 
                  marginBottom: '30px',
                  opacity: '0.9'
                }}>
                  Unbelievable discounts on your favorite products!
                </p>
                <div style={{
                  background: 'rgba(255,255,255,0.2)',
                  backdropFilter: 'blur(10px)',
                  borderRadius: '25px',
                  padding: '15px 30px',
                  display: 'inline-block',
                  fontSize: '1rem',
                  fontWeight: '600'
                }}>
                  ⏰ Limited Time Offers - Hurry Up!
                </div>
              </div>
            </section>

            {/* Main Content */}
            <div style={{ padding: '40px 20px' }}>
              <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
                
                {/* Flash Deals Section */}
                <section style={{ marginBottom: '60px' }}>
                  <div style={{ 
                    textAlign: 'center', 
                    marginBottom: '40px'
                  }}>
                    <h2 style={{ 
                      fontSize: '2.5rem', 
                      color: '#333',
                      fontWeight: '700',
                      marginBottom: '10px'
                    }}>
                      ⚡ Flash Deals
                    </h2>
                    <div style={{
                      background: '#fff5f5',
                      color: '#e53e3e',
                      padding: '10px 20px',
                      borderRadius: '20px',
                      display: 'inline-block',
                      fontSize: '1rem',
                      fontWeight: '600',
                      border: '2px solid #fed7d7'
                    }}>
                      Ends in 23:45:12
                    </div>
                  </div>

                  <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
                    gap: '25px',
                    marginBottom: '40px'
                  }}>
                    {/* Flash Deal Product 1 */}
                    <div style={{
                      background: 'white',
                      borderRadius: '20px',
                      padding: '25px',
                      boxShadow: '0 10px 30px rgba(0,0,0,0.1)',
                      position: 'relative',
                      transition: 'transform 0.3s ease, box-shadow 0.3s ease',
                      cursor: 'pointer',
                      border: '2px solid #ff6b6b'
                    }}>
                      <div style={{
                        position: 'absolute',
                        top: '-10px',
                        right: '-10px',
                        background: '#ff6b6b',
                        color: 'white',
                        padding: '10px 15px',
                        borderRadius: '20px',
                        fontSize: '0.9rem',
                        fontWeight: '700'
                      }}>
                        -60%
                      </div>
                      
                      <div style={{ textAlign: 'center', marginBottom: '20px' }}>
                        <div style={{ fontSize: '4rem', marginBottom: '15px' }}>📱</div>
                        <h3 style={{ 
                          fontSize: '1.4rem', 
                          marginBottom: '10px', 
                          color: '#333',
                          fontWeight: '600'
                        }}>
                          iPhone 15 Pro
                        </h3>
                        <p style={{ 
                          color: '#666', 
                          fontSize: '0.9rem',
                          lineHeight: '1.4'
                        }}>
                          Latest iPhone with advanced features
                        </p>
                      </div>
                      
                      <div style={{ textAlign: 'center', marginBottom: '20px' }}>
                        <div style={{ 
                          fontSize: '2rem', 
                          fontWeight: '700', 
                          color: '#e53e3e',
                          marginBottom: '5px'
                        }}>
                          ₹99,999.00
                        </div>
                        <div style={{ 
                          fontSize: '1.1rem', 
                          color: '#999',
                          textDecoration: 'line-through'
                        }}>
                          ₹1,49,999.00
                        </div>
                      </div>
                      
                      <div style={{ marginBottom: '20px' }}>
                        <div style={{
                          background: '#f0f0f0',
                          borderRadius: '10px',
                          height: '8px',
                          overflow: 'hidden'
                        }}>
                          <div style={{
                            background: 'linear-gradient(45deg, #ff6b6b, #ee5a24)',
                            height: '100%',
                            width: '75%',
                            borderRadius: '10px'
                          }}></div>
                        </div>
                        <p style={{ 
                          fontSize: '0.8rem', 
                          color: '#666',
                          marginTop: '8px',
                          textAlign: 'center'
                        }}>
                          85 sold / 120 total
                        </p>
                      </div>
                      
                      <button
                        onClick={() => addToCart({id: 'flash1', name: 'iPhone 15 Pro', price: 99999})}
                        style={{
                          width: '100%',
                          background: 'linear-gradient(45deg, #667eea, #764ba2)',
                          color: 'white',
                          border: 'none',
                          padding: '15px',
                          borderRadius: '12px',
                          fontSize: '1rem',
                          fontWeight: '600',
                          cursor: 'pointer',
                          transition: 'all 0.3s ease'
                        }}
                      >
                        Add to Cart 🛒
                      </button>
                    </div>

                    {/* Flash Deal Product 2 */}
                    <div style={{
                      background: 'white',
                      borderRadius: '20px',
                      padding: '25px',
                      boxShadow: '0 10px 30px rgba(0,0,0,0.1)',
                      position: 'relative',
                      transition: 'transform 0.3s ease, box-shadow 0.3s ease',
                      cursor: 'pointer',
                      border: '2px solid #ff6b6b'
                    }}>
                      <div style={{
                        position: 'absolute',
                        top: '-10px',
                        right: '-10px',
                        background: '#ff6b6b',
                        color: 'white',
                        padding: '10px 15px',
                        borderRadius: '20px',
                        fontSize: '0.9rem',
                        fontWeight: '700'
                      }}>
                        -45%
                      </div>
                      
                      <div style={{ textAlign: 'center', marginBottom: '20px' }}>
                        <div style={{ fontSize: '4rem', marginBottom: '15px' }}>👕</div>
                        <h3 style={{ 
                          fontSize: '1.4rem', 
                          marginBottom: '10px', 
                          color: '#333',
                          fontWeight: '600'
                        }}>
                          Levi's Jeans
                        </h3>
                        <p style={{ 
                          color: '#666', 
                          fontSize: '0.9rem',
                          lineHeight: '1.4'
                        }}>
                          Classic denim jeans
                        </p>
                      </div>
                      
                      <div style={{ textAlign: 'center', marginBottom: '20px' }}>
                        <div style={{ 
                          fontSize: '2rem', 
                          fontWeight: '700', 
                          color: '#e53e3e',
                          marginBottom: '5px'
                        }}>
                          ₹3,999.00
                        </div>
                        <div style={{ 
                          fontSize: '1.1rem', 
                          color: '#999',
                          textDecoration: 'line-through'
                        }}>
                          ₹7,299.00
                        </div>
                      </div>
                      
                      <div style={{ marginBottom: '20px' }}>
                        <div style={{
                          background: '#f0f0f0',
                          borderRadius: '10px',
                          height: '8px',
                          overflow: 'hidden'
                        }}>
                          <div style={{
                            background: 'linear-gradient(45deg, #ff6b6b, #ee5a24)',
                            height: '100%',
                            width: '60%',
                            borderRadius: '10px'
                          }}></div>
                        </div>
                        <p style={{ 
                          fontSize: '0.8rem', 
                          color: '#666',
                          marginTop: '8px',
                          textAlign: 'center'
                        }}>
                          66 sold / 110 total
                        </p>
                      </div>
                      
                      <button
                        onClick={() => addToCart({id: 'flash2', name: "Levi's Jeans", price: 3999})}
                        style={{
                          width: '100%',
                          background: 'linear-gradient(45deg, #667eea, #764ba2)',
                          color: 'white',
                          border: 'none',
                          padding: '15px',
                          borderRadius: '12px',
                          fontSize: '1rem',
                          fontWeight: '600',
                          cursor: 'pointer',
                          transition: 'all 0.3s ease'
                        }}
                      >
                        Add to Cart 🛒
                      </button>
                    </div>

                    {/* Flash Deal Product 3 */}
                    <div style={{
                      background: 'white',
                      borderRadius: '20px',
                      padding: '25px',
                      boxShadow: '0 10px 30px rgba(0,0,0,0.1)',
                      position: 'relative',
                      transition: 'transform 0.3s ease, box-shadow 0.3s ease',
                      cursor: 'pointer',
                      border: '2px solid #ff6b6b'
                    }}>
                      <div style={{
                        position: 'absolute',
                        top: '-10px',
                        right: '-10px',
                        background: '#ff6b6b',
                        color: 'white',
                        padding: '10px 15px',
                        borderRadius: '20px',
                        fontSize: '0.9rem',
                        fontWeight: '700'
                      }}>
                        -70%
                      </div>
                      
                      <div style={{ textAlign: 'center', marginBottom: '20px' }}>
                        <div style={{ fontSize: '4rem', marginBottom: '15px' }}>🎧</div>
                        <h3 style={{ 
                          fontSize: '1.4rem', 
                          marginBottom: '10px', 
                          color: '#333',
                          fontWeight: '600'
                        }}>
                          Apple AirPods Pro 2
                        </h3>
                        <p style={{ 
                          color: '#666', 
                          fontSize: '0.9rem',
                          lineHeight: '1.4'
                        }}>
                          Wireless earbuds with noise cancellation
                        </p>
                      </div>
                      
                      <div style={{ textAlign: 'center', marginBottom: '20px' }}>
                        <div style={{ 
                          fontSize: '2rem', 
                          fontWeight: '700', 
                          color: '#e53e3e',
                          marginBottom: '5px'
                        }}>
                          ₹24,999.00
                        </div>
                        <div style={{ 
                          fontSize: '1.1rem', 
                          color: '#999',
                          textDecoration: 'line-through'
                        }}>
                          ₹34,900.00
                        </div>
                      </div>
                      
                      <div style={{ marginBottom: '20px' }}>
                        <div style={{
                          background: '#f0f0f0',
                          borderRadius: '10px',
                          height: '8px',
                          overflow: 'hidden'
                        }}>
                          <div style={{
                            background: 'linear-gradient(45deg, #ff6b6b, #ee5a24)',
                            height: '100%',
                            width: '40%',
                            borderRadius: '10px'
                          }}></div>
                        </div>
                        <p style={{ 
                          fontSize: '0.8rem', 
                          color: '#666',
                          marginTop: '8px',
                          textAlign: 'center'
                        }}>
                          40 sold / 100 total
                        </p>
                      </div>
                      
                      <button
                        onClick={() => addToCart({id: 'flash3', name: 'Apple AirPods Pro 2', price: 24999})}
                        style={{
                          width: '100%',
                          background: 'linear-gradient(45deg, #667eea, #764ba2)',
                          color: 'white',
                          border: 'none',
                          padding: '15px',
                          borderRadius: '12px',
                          fontSize: '1rem',
                          fontWeight: '600',
                          cursor: 'pointer',
                          transition: 'all 0.3s ease'
                        }}
                      >
                        Add to Cart 🛒
                      </button>
                    </div>
                  </div>
                </section>

                {/* Today's Best Deals */}
                <section style={{ marginBottom: '60px' }}>
                  <h2 style={{ 
                    textAlign: 'center', 
                    fontSize: '2.5rem', 
                    marginBottom: '40px',
                    color: '#333',
                    fontWeight: '700'
                  }}>
                    🌟 Today's Best Deals
                  </h2>
                  
                  <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                    gap: '20px'
                  }}>
                    {filteredProducts.map((product, index) => {
                      const discountPercent = 20 + (index % 5) * 10; // Random discount 20-60%
                      const originalPrice = product.price * (1 + discountPercent / 100);
                      
                      return (
                        <div key={product.id} style={{
                          background: 'white',
                          borderRadius: '15px',
                          padding: '20px',
                          boxShadow: '0 5px 20px rgba(0,0,0,0.1)',
                          border: '1px solid #f0f0f0',
                          transition: 'all 0.3s ease',
                          cursor: 'pointer'
                        }}>
                          <div style={{ position: 'relative' }}>
                            {/* Discount Badge */}
                            <div style={{
                              position: 'absolute',
                              top: '-10px',
                              right: '-10px',
                              background: '#e53e3e',
                              color: 'white',
                              padding: '5px 10px',
                              borderRadius: '15px',
                              fontSize: '0.8rem',
                              fontWeight: '700',
                              zIndex: 1
                            }}>
                              -{discountPercent}%
                            </div>
                            
                            <div style={{ textAlign: 'center', marginBottom: '15px' }}>
                              <div style={{ fontSize: '3rem', marginBottom: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center', height: '10vh' }}>
                                {product.image && product.image.startsWith('http') ? (
                                  <img
                                    src={product.image}
                                    alt={product.name}
                                    style={{ maxWidth: '100%', height: '60px', objectFit: 'cover' }}
                                  />
                                ) : (
                                  <span style={{ fontSize: '3rem' }}>{product.image || '📦'}</span>
                                )}
                              </div>
                              <h4 style={{ 
                                fontSize: '1.1rem', 
                                marginBottom: '8px', 
                                color: '#333',
                                fontWeight: '600'
                              }}>
                                {product.name}
                              </h4>
                            </div>
                            
                            <div style={{ textAlign: 'center', marginBottom: '15px' }}>
                              <span style={{ 
                                fontSize: '1.3rem', 
                                fontWeight: '700', 
                                color: '#e53e3e'
                              }}>
                                ₹{product.price.toFixed(2)}
                              </span>
                              <span style={{ 
                                fontSize: '0.9rem', 
                                color: '#999',
                                textDecoration: 'line-through',
                                marginLeft: '10px'
                              }}>
                                ₹{originalPrice.toFixed(2)}
                              </span>
                            </div>
                            
                            <button
                              onClick={() => addToCart(product)}
                              style={{
                                width: '100%',
                                background: 'linear-gradient(45deg, #48bb78, #38a169)',
                                color: 'white',
                                border: 'none',
                                padding: '12px',
                                borderRadius: '10px',
                                fontSize: '0.9rem',
                                fontWeight: '600',
                                cursor: 'pointer',
                                transition: 'all 0.3s ease'
                              }}
                            >
                              Quick Add 🚀
                            </button>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </section>

                {/* Deal Categories */}
                <section style={{ marginBottom: '60px' }}>
                  <h2 style={{ 
                    textAlign: 'center', 
                    fontSize: '2.5rem', 
                    marginBottom: '40px',
                    color: '#333',
                    fontWeight: '700'
                  }}>
                    💎 Deal Categories
                  </h2>
                  
                  <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                    gap: '25px'
                  }}>
                    {['Electronics', 'Sports', 'Home', 'Accessories'].map((category, index) => {
                      const categoryIcons = { 
                        Electronics: '📱', 
                        Sports: '⚽', 
                        Home: '🏠', 
                        Accessories: '👜' 
                      };
                      const gradients = [
                        'linear-gradient(135deg, #ff9a9e, #fecfef)',
                        'linear-gradient(135deg, #a8edea, #fed6e3)',
                        'linear-gradient(135deg, #ffecd2, #fcb69f)',
                        'linear-gradient(135deg, #c2e9fb, #a1c4fd)'
                      ];
                      const avgDiscount = 30 + (index * 15);
                      
                      return (
                        <div key={category} style={{
                          background: gradients[index],
                          borderRadius: '20px',
                          padding: '30px',
                          textAlign: 'center',
                          cursor: 'pointer',
                          transition: 'transform 0.3s ease',
                          boxShadow: '0 10px 25px rgba(0,0,0,0.1)'
                        }}
                        onClick={() => {
                          setSelectedCategory(category);
                          setCurrentView('products');
                        }}>
                          <div style={{ fontSize: '3.5rem', marginBottom: '15px' }}>
                            {categoryIcons[category]}
                          </div>
                          <h3 style={{ 
                            fontSize: '1.3rem', 
                            marginBottom: '10px', 
                            color: '#333',
                            fontWeight: '700'
                          }}>
                            {category}
                          </h3>
                          <div style={{
                            background: 'rgba(255,255,255,0.8)',
                            borderRadius: '15px',
                            padding: '8px 15px',
                            display: 'inline-block',
                            fontSize: '1rem',
                            fontWeight: '600',
                            color: '#e53e3e'
                          }}>
                            Up to {avgDiscount}% OFF
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </section>

                {/* Special Offers Banner */}
                <section>
                  <div style={{
                    background: 'linear-gradient(45deg, #667eea, #764ba2)',
                    borderRadius: '20px',
                    padding: '40px',
                    textAlign: 'center',
                    color: 'white'
                  }}>
                    <h2 style={{ 
                      fontSize: '2.5rem', 
                      marginBottom: '20px',
                      fontWeight: '700'
                    }}>
                      🎉 Special Offer Alert!
                    </h2>
                    <p style={{ 
                      fontSize: '1.2rem', 
                      marginBottom: '25px',
                      opacity: '0.9'
                    }}>
                      Get additional 10% off on orders above ₹999 | Use code: MEGA10
                    </p>
                    <div style={{
                      background: 'rgba(255,255,255,0.2)',
                      borderRadius: '15px',
                      padding: '15px 30px',
                      display: 'inline-block',
                      fontSize: '1.1rem',
                      fontWeight: '600'
                    }}>
                      Free shipping on all orders • 30-day return policy
                    </div>
                  </div>
                </section>
              </div>
            </div>
          </div>
        );
      case 'about':
        return (
          <div style={{ padding: '40px 20px', minHeight: '80vh', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
            <div className="container" style={{ maxWidth: '1200px', margin: '0 auto' }}>
              <h2 style={{ textAlign: 'center', marginBottom: '50px', fontSize: '3rem', color: 'white', textShadow: '2px 2px 4px rgba(0,0,0,0.3)' }}>About Us</h2>
              
              {/* Company Info */}
              <div style={{
                background: 'rgba(255,255,255,0.95)',
                borderRadius: '20px',
                padding: '40px',
                marginBottom: '40px',
                boxShadow: '0 20px 40px rgba(0,0,0,0.2)',
                textAlign: 'center'
              }}>
                <div style={{ fontSize: '4rem', marginBottom: '20px' }}>👨‍💼</div>
                <h3 style={{ fontSize: '2.5rem', marginBottom: '15px', color: '#333' }}>Meet Our Founder</h3>
                <h4 style={{ fontSize: '2rem', marginBottom: '20px', color: '#667eea', fontWeight: '600' }}>Shaswat Kumar</h4>
                <p style={{ fontSize: '1.2rem', color: '#666', lineHeight: '1.6', maxWidth: '800px', margin: '0 auto' }}>
                  Founder & Admin of MegaCart, passionate about bringing you the best shopping experience with quality products at affordable prices. 
                  With a vision to revolutionize online shopping in India, MegaCart aims to be your trusted partner for all your shopping needs.
                </p>
              </div>

              {/* Company Story */}
              <div style={{
                background: 'rgba(255,255,255,0.95)',
                borderRadius: '20px',
                padding: '40px',
                marginBottom: '40px',
                boxShadow: '0 20px 40px rgba(0,0,0,0.2)'
              }}>
                <h3 style={{ fontSize: '2rem', marginBottom: '30px', color: '#333', textAlign: 'center' }}>Our Story</h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '30px', marginBottom: '30px' }}>
                  <div style={{ textAlign: 'center', padding: '20px' }}>
                    <div style={{ fontSize: '3rem', marginBottom: '15px' }}>🚀</div>
                    <h4 style={{ fontSize: '1.5rem', marginBottom: '10px', color: '#667eea' }}>Our Mission</h4>
                    <p style={{ color: '#666', lineHeight: '1.6' }}>To provide high-quality products at competitive prices with exceptional customer service.</p>
                  </div>
                  <div style={{ textAlign: 'center', padding: '20px' }}>
                    <div style={{ fontSize: '3rem', marginBottom: '15px' }}>🎯</div>
                    <h4 style={{ fontSize: '1.5rem', marginBottom: '10px', color: '#667eea' }}>Our Vision</h4>
                    <p style={{ color: '#666', lineHeight: '1.6' }}>To become India's most trusted e-commerce platform for all your shopping needs.</p>
                  </div>
                  <div style={{ textAlign: 'center', padding: '20px' }}>
                    <div style={{ fontSize: '3rem', marginBottom: '15px' }}>💎</div>
                    <h4 style={{ fontSize: '1.5rem', marginBottom: '10px', color: '#667eea' }}>Our Values</h4>
                    <p style={{ color: '#666', lineHeight: '1.6' }}>Quality, Transparency, Customer Satisfaction, and Innovation in everything we do.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        );
      case 'contact':
        return (
          <div style={{ padding: '40px 20px', minHeight: '80vh', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
            <div className="container" style={{ maxWidth: '1200px', margin: '0 auto' }}>
              <h2 style={{ textAlign: 'center', marginBottom: '50px', fontSize: '3rem', color: 'white', textShadow: '2px 2px 4px rgba(0,0,0,0.3)' }}>Contact Us</h2>
              
              <div style={{ 
                display: 'grid', 
                gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', 
                gap: '40px',
                alignItems: 'start'
              }}>
                {/* Contact Info */}
                <div style={{
                  background: 'rgba(255,255,255,0.95)',
                  borderRadius: '20px',
                  padding: '40px',
                  boxShadow: '0 20px 40px rgba(0,0,0,0.2)'
                }}>
                  <h3 style={{ fontSize: '2rem', marginBottom: '30px', color: '#333', textAlign: 'center' }}>Get in Touch</h3>
                  
                  <div style={{ space: '30px 0' }}>
                    <div style={{ marginBottom: '30px' }}>
                      <h4 style={{ fontSize: '1.3rem', color: '#667eea', marginBottom: '15px', display: 'flex', alignItems: 'center' }}>
                        <span style={{ fontSize: '1.5rem', marginRight: '10px' }}>📧</span>
                        Email Address
                      </h4>
                      <div style={{ padding: '15px', background: '#f8f9fa', borderRadius: '10px', marginLeft: '35px' }}>
                        <div style={{ marginBottom: '5px' }}>shaswatsinha05@gmail.com</div>
                        <div>support@megacart.com</div>
                      </div>
                    </div>
                    
                    <div style={{ marginBottom: '30px' }}>
                      <h4 style={{ fontSize: '1.3rem', color: '#667eea', marginBottom: '15px', display: 'flex', alignItems: 'center' }}>
                        <span style={{ fontSize: '1.5rem', marginRight: '10px' }}>📞</span>
                        Phone Number
                      </h4>
                      <div style={{ padding: '15px', background: '#f8f9fa', borderRadius: '10px', marginLeft: '35px' }}>
                        <div style={{ marginBottom: '5px', fontWeight: '600' }}>+91 7004504120</div>
                        <div style={{ fontSize: '0.9rem', color: '#666' }}>Available Mon-Fri, 9 AM - 6 PM IST</div>
                      </div>
                    </div>
                    
                    <div style={{ marginBottom: '30px' }}>
                      <h4 style={{ fontSize: '1.3rem', color: '#667eea', marginBottom: '15px', display: 'flex', alignItems: 'center' }}>
                        <span style={{ fontSize: '1.5rem', marginRight: '10px' }}>📍</span>
                        Office Address
                      </h4>
                      <div style={{ padding: '15px', background: '#f8f9fa', borderRadius: '10px', marginLeft: '35px' }}>
                        <div style={{ fontWeight: '600', marginBottom: '5px' }}>MegaCart Headquarters</div>
                        <div>Ranchi, Jharkhand - 834001, India</div>
                      </div>
                    </div>
                    
                    <div>
                      <h4 style={{ fontSize: '1.3rem', color: '#667eea', marginBottom: '15px', display: 'flex', alignItems: 'center' }}>
                        <span style={{ fontSize: '1.5rem', marginRight: '10px' }}>🕒</span>
                        Business Hours
                      </h4>
                      <div style={{ padding: '15px', background: '#f8f9fa', borderRadius: '10px', marginLeft: '35px' }}>
                        <div style={{ marginBottom: '5px' }}>Monday - Friday: 9:00 AM - 6:00 PM</div>
                        <div>Saturday: 10:00 AM - 4:00 PM</div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Contact Form */}
                <div style={{
                  background: 'rgba(255,255,255,0.95)',
                  borderRadius: '20px',
                  padding: '40px',
                  boxShadow: '0 20px 40px rgba(0,0,0,0.2)'
                }}>
                  <h3 style={{ fontSize: '2rem', marginBottom: '30px', color: '#333', textAlign: 'center' }}>Send us a Message</h3>
                  <form style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                    <input 
                      type="text" 
                      placeholder="Your Name"
                      style={{
                        padding: '15px',
                        border: '2px solid #e9ecef',
                        borderRadius: '10px',
                        fontSize: '1rem',
                        transition: 'border-color 0.3s ease'
                      }}
                    />
                    <input 
                      type="email" 
                      placeholder="Your Email"
                      style={{
                        padding: '15px',
                        border: '2px solid #e9ecef',
                        borderRadius: '10px',
                        fontSize: '1rem',
                        transition: 'border-color 0.3s ease'
                      }}
                    />
                    <input 
                      type="text" 
                      placeholder="Subject"
                      style={{
                        padding: '15px',
                        border: '2px solid #e9ecef',
                        borderRadius: '10px',
                        fontSize: '1rem',
                        transition: 'border-color 0.3s ease'
                      }}
                    />
                    <textarea 
                      placeholder="Your Message" 
                      rows="5"
                      style={{
                        padding: '15px',
                        border: '2px solid #e9ecef',
                        borderRadius: '10px',
                        fontSize: '1rem',
                        resize: 'vertical',
                        fontFamily: 'inherit',
                        transition: 'border-color 0.3s ease'
                      }}
                    ></textarea>
                    <button 
                      type="submit"
                      style={{
                        background: 'linear-gradient(45deg, #667eea, #764ba2)',
                        color: 'white',
                        border: 'none',
                        padding: '15px 30px',
                        borderRadius: '10px',
                        fontSize: '1.1rem',
                        fontWeight: '600',
                        cursor: 'pointer',
                        boxShadow: '0 5px 15px rgba(102,126,234,0.4)',
                        transition: 'transform 0.2s ease'
                      }}
                      onMouseOver={(e) => e.target.style.transform = 'translateY(-2px)'}
                      onMouseOut={(e) => e.target.style.transform = 'translateY(0)'}
                    >
                      Send Message
                    </button>
                  </form>
                </div>
              </div>
            </div>
          </div>
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
                  onClick={handleShopNowClick}
                >
                  Shop Now
                </button>
              </div>
            </section>

            {/* Search and Filter Section */}
            <section className="search-filter" ref={productsRef}>
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
          currentView={currentView}
          onNavigation={handleNavigation}
          onSearchClick={handleSearchClick}
          isAuthenticated={isAuthenticated}
          user={user}
          logout={handleLogout}
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