# MegaCart E-commerce Website

A modern, full-stack e-commerce platform built with FastAPI backend, responsive HTML/CSS/Tailwind frontend, and MongoDB database.

## 🚀 Live Demo

Visit the live website: [MegaCart](https://68c1e053a811e70693c97ba2--kaleidoscopic-kitsune-d0d5df.netlify.app/)

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [License](#license)

## ✨ Features

- **Product Catalog**: Browse and search through a wide range of products
- **User Authentication**: Secure user registration and login system
- **Shopping Cart**: Add, remove, and manage products in cart
- **Order Management**: Complete order processing and tracking
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Admin Panel**: Product and order management for administrators
- **Payment Integration**: Secure payment processing
- **User Profile**: Manage personal information and order history

## 🛠 Tech Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs with Python
- **Python**: 3.8+
- **MongoDB**: NoSQL database for flexible data storage
- **Motor**: Async MongoDB driver
- **Pydantic**: Data validation and serialization
- **JWT**: JSON Web Tokens for authentication

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Modern styling with custom properties
- **Tailwind CSS**: Utility-first CSS framework
- **JavaScript**: ES6+ for dynamic interactions
- **Responsive Design**: Mobile-first approach

### Database
- **MongoDB**: Document-based NoSQL database
- **MongoDB Atlas**: Cloud database service (if applicable)

### Deployment
- **Netlify**: Frontend deployment and hosting
- **Backend**: (Add your backend deployment platform)

## 🚀 Installation

### Prerequisites
- Python 3.8+
- Node.js (for Tailwind CSS if using build process)
- MongoDB instance (local or cloud)
- Git


### Frontend Setup

1. **Navigate to frontend directory**
```bash
cd frontend
```

2. **Install dependencies (if using build tools)**
```bash
npm install
```

3. **Build Tailwind CSS (if needed)**
```bash
npm run build-css
```

4. **Serve the frontend**
- For development: Use live server or similar
- For production: Deploy to Netlify or similar platform

## 📖 Usage

### Running the Application

1. **Start MongoDB** (if running locally)
```bash
mongod
```

2. **Start the FastAPI backend**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

3. **Access the application**
- Frontend: `http://localhost:3000` (or your development server)
- Backend API: `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`

### Key Functionalities

- **Browse Products**: View all available products with filtering options
- **User Registration/Login**: Create account and authenticate
- **Add to Cart**: Select products and manage shopping cart
- **Checkout Process**: Complete purchase with payment integration
- **Order Tracking**: Monitor order status and history
- **Admin Functions**: Manage products, orders, and users (admin only)

## 📚 API Documentation

The FastAPI backend automatically generates interactive API documentation.

**Note**: Since the backend is deployed on Render, API documentation is available at the deployed backend URL.


## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Contact

- **Project Maintainer**: Shaswat Kumar
- **Email**: shaswatsinha05@gmail.com
- **GitHub**: Shaswatkr19 (https://github.com/Shaswatkr19)

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- Tailwind CSS for the utility-first CSS framework
- MongoDB for flexible data storage
- Netlify for seamless deployment

---

⭐ If you found this project helpful, please give it a star on GitHub!

## 📈 Future Enhancements

- [ ] Product reviews and ratings
- [ ] Wishlist functionality
- [ ] Advanced search filters
- [ ] Email notifications
- [ ] Multi-language support
- [ ] Progressive Web App (PWA) features
- [ ] Real-time chat support
- [ ] Analytics dashboard