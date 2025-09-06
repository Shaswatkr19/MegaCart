// src/services/api.js - Complete API Service

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Mock data - define these constants at the top of the file
const MOCK_PRODUCTS = [
  {
    id: 1,
    name: 'Wireless Headphones',
    price: 99.99,
    category: 'Electronics',
    description: 'High-quality wireless headphones with noise cancellation',
    image: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300&h=300&fit=crop',
    stock: 15
  },
  {
    id: 2,
    name: 'Smartphone',
    price: 699.99,
    category: 'Electronics',
    description: 'Latest model smartphone with advanced features',
    image: 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=300&h=300&fit=crop',
    stock: 8
  },
  {
    id: 3,
    name: 'Running Shoes',
    price: 129.99,
    category: 'Sports',
    description: 'Comfortable running shoes for all terrains',
    image: 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=300&h=300&fit=crop',
    stock: 20
  },
  {
    id: 4,
    name: 'Coffee Maker',
    price: 79.99,
    category: 'Home',
    description: 'Automatic coffee maker with programmable timer',
    image: 'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=300&h=300&fit=crop',
    stock: 12
  },
  {
    id: 5,
    name: 'Laptop Backpack',
    price: 49.99,
    category: 'Accessories',
    description: 'Durable laptop backpack with multiple compartments',
    image: 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=300&h=300&fit=crop',
    stock: 25
  }
];

const MOCK_CATEGORIES = [
  { id: 1, name: 'Electronics', count: 2 },
  { id: 2, name: 'Sports', count: 1 },
  { id: 3, name: 'Home', count: 1 },
  { id: 4, name: 'Accessories', count: 1 }
];

// Simulate API delay
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// API service functions
export const apiService = {
  // Get all products with optional filtering
  async getProducts(filters = {}) {
    await delay(500); // Simulate network delay
    
    let filteredProducts = [...MOCK_PRODUCTS];
    
    // Filter by category
    if (filters.category && filters.category !== 'all') {
      filteredProducts = filteredProducts.filter(
        product => product.category.toLowerCase() === filters.category.toLowerCase()
      );
    }
    
    // Filter by search query
    if (filters.search) {
      const searchTerm = filters.search.toLowerCase();
      filteredProducts = filteredProducts.filter(
        product => 
          product.name.toLowerCase().includes(searchTerm) ||
          product.description.toLowerCase().includes(searchTerm)
      );
    }
    
    // Sort products
    if (filters.sortBy) {
      filteredProducts.sort((a, b) => {
        switch (filters.sortBy) {
          case 'price-low':
            return a.price - b.price;
          case 'price-high':
            return b.price - a.price;
          case 'name':
            return a.name.localeCompare(b.name);
          default:
            return 0;
        }
      });
    }
    
    return {
      products: filteredProducts,
      total: filteredProducts.length
    };
  },

  // Get single product by ID
  async getProduct(id) {
    await delay(300);
    const product = MOCK_PRODUCTS.find(p => p.id === parseInt(id));
    if (!product) {
      throw new Error('Product not found');
    }
    return product;
  },

  // Get all categories
  async getCategories() {
    await delay(200);
    return [...MOCK_CATEGORIES];
  },

  // Add product to cart (simulate)
  async addToCart(productId, quantity = 1) {
    await delay(300);
    const product = MOCK_PRODUCTS.find(p => p.id === productId);
    if (!product) {
      throw new Error('Product not found');
    }
    if (product.stock < quantity) {
      throw new Error('Insufficient stock');
    }
    
    // In a real app, this would update the backend
    return {
      success: true,
      message: `Added ${quantity} ${product.name}(s) to cart`
    };
  },

  // Update product stock (simulate)
  async updateStock(productId, newStock) {
    await delay(300);
    const productIndex = MOCK_PRODUCTS.findIndex(p => p.id === productId);
    if (productIndex === -1) {
      throw new Error('Product not found');
    }
    
    MOCK_PRODUCTS[productIndex].stock = newStock;
    return MOCK_PRODUCTS[productIndex];
  }
};

// Helper function for API calls
const apiCall = async (endpoint, options = {}) => {
  try {
    const url = `${API_URL}${endpoint}`;
    console.log('API Call:', url); // Debug log
    
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log('API Response:', data); // Debug log
    return data;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};

// Products API with fallback
export const getProducts = async () => {
  try {
    const data = await apiCall('/api/products/');
    return Array.isArray(data) ? data : [];
  } catch (error) {
    console.error('Products API failed, using mock data');
    return MOCK_PRODUCTS;
  }
};

export const getProduct = async (id) => {
  try {
    return await apiCall(`/api/products/${id}`);
  } catch (error) {
    console.error('Product API failed, using mock data');
    return MOCK_PRODUCTS.find(p => p.id === parseInt(id)) || null;
  }
};

// Categories API with fallback
export const getCategories = async () => {
  try {
    const data = await apiCall('/api/categories/');
    return Array.isArray(data) ? data : MOCK_CATEGORIES;
  } catch (error) {
    console.warn('Categories API failed, using mock categories');
    return MOCK_CATEGORIES;
  }
};

// Auth APIs
export const loginUser = async (credentials) => {
  return await apiCall('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify(credentials),
  });
};

export const registerUser = async (userData) => {
  return await apiCall('/api/auth/register', {
    method: 'POST',
    body: JSON.stringify(userData),
  });
};

// User Profile API
export const getUserProfile = async (token) => {
  return await apiCall('/api/user/profile', {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
};

export const updateUserProfile = async (userData, token) => {
  return await apiCall('/api/user/profile', {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(userData),
  });
};

// Orders API (if implemented in backend)
export const getUserOrders = async (token) => {
  try {
    return await apiCall('/api/user/orders', {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
  } catch (error) {
    console.warn('Orders API not available');
    return []; // Return empty array if not implemented
  }
};

// Health Check
export const healthCheck = async () => {
  return await apiCall('/');
};

// Test API connectivity
export const testConnection = async () => {
  try {
    await healthCheck();
    console.log('✅ Backend connection successful');
    return true;
  } catch (error) {
    console.error('❌ Backend connection failed:', error);
    return false;
  }
};