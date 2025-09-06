# main.py - Complete FastAPI Backend

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel
import json

# Create FastAPI app
app = FastAPI(
    title="MegaCart API",
    description="E-commerce API for MegaCart",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class Product(BaseModel):
    id: int
    name: str
    description: str
    price: float
    category: str
    image: str
    rating: float
    reviews: int
    inStock: bool

# Sample data (replace with your database)
PRODUCTS = [
    {
        "id": 1,
        "name": "iPhone 15 Pro",
        "description": "Latest iPhone with advanced features",
        "price": 99999,
        "category": "Electronics",
        "image": "https://images.unsplash.com/photo-1697284959152-32ef13855932?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8OXx8aXBob25lJTIwMTUlMjBwcm98ZW58MHx8MHx8fDA%3D",
        "rating": 4.8,
        "reviews": 1250,
        "inStock": True
    },
    {
        "id": 2,
        "name": "Samsung Galaxy S24",
        "description": "Premium Android smartphone",
        "price": 79999,
        "category": "Electronics", 
        "image": "https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=400",
        "rating": 4.6,
        "reviews": 890,
        "inStock": True
    },
    {
        "id": 3,
        "name": "Nike Air Max",
        "description": "Comfortable running shoes",
        "price": 8999,
        "category": "Clothing",
        "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400",
        "rating": 4.4,
        "reviews": 567,
        "inStock": True
    },
    {
        "id": 4,
        "name": "MacBook Pro M3",
        "description": "Powerful laptop for professionals",
        "price": 199999,
        "category": "Electronics",
        "image": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400",
        "rating": 4.9,
        "reviews": 423,
        "inStock": True
    },
    {
        "id": 5,
        "name": "Levi's Jeans",
        "description": "Classic denim jeans",
        "price": 3999,
        "category": "Clothing",
        "image": "https://images.unsplash.com/photo-1542272604-787c3835535d?w=400",
        "rating": 4.2,
        "reviews": 234,
        "inStock": True
    },
    {
        "id": 6,
        "name": "Apple Watch Series 9",
        "description": "Smartwatch with fitness tracking and health features",
        "price": 45999,
        "category": "Electronics",
        "image": "https://images.unsplash.com/photo-1644235779485-e4d021d8edab?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTl8fEFwcGxlJTIwV2F0Y2glMjBTZXJpZXMlMjA5fGVufDB8fDB8fHww",
        "rating": 4.6,
        "reviews": 870,
        "inStock": True
    },
    {
        "id": 7,
        "name": "HP Spectre x360",
        "description": "Convertible laptop with touchscreen display",
        "price": 134999,
        "category": "Electronics",
        "image": "https://images.unsplash.com/photo-1619532550465-ad4dc9bd680a?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NHx8SFAlMjBTcGVjdHJlJTIweDM2MHxlbnwwfHwwfHx8MA%3D%3D",
        "rating": 4.5,
        "reviews": 560,
        "inStock": True
    },
    {
        "id": 8,
        "name": "Canon EOS R10",
        "description": "Mirrorless camera for photography enthusiasts",
        "price": 89999,
        "category": "Electronics",
        "image": "https://images.unsplash.com/photo-1745848037998-1e6dc8380f7e?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8Q2Fub24lMjBFT1MlMjBSMTB8ZW58MHx8MHx8fDA%3D",
        "rating": 4.7,
        "reviews": 340,
        "inStock": True
    },
    {
        "id": 9,
        "name": "Apple AirPods Pro 2",
        "description": "Wireless earbuds with noise cancellation",
        "price": 24999,
        "category": "Electronics",
        "image": "https://images.unsplash.com/photo-1610438235354-a6ae5528385c?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8N3x8QXBwbGUlMjBBaXJQb2RzJTIwUHJvJTIwMnxlbnwwfHwwfHx8MA%3D%3D",
        "rating": 4.8,
        "reviews": 1120,
        "inStock": True
    },
    {
        "id": 10,
        "name": "Fitbit Charge 6",
        "description": "Fitness band with heart rate monitoring",
        "price": 15999,
        "category": "Electronics",
        "image": "https://images.unsplash.com/photo-1611270629569-948d94ca915a?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8Rml0Yml0JTIwQ2hhcmdlJTIwNnxlbnwwfHwwfHx8MA%3D%3D",
        "rating": 4.4,
        "reviews": 450,
        "inStock": True
    },
    {
        "id": 11,
        "name": "Woodland Hiking Boots",
        "description": "Durable boots for trekking and hiking",
        "price": 7999,
        "category": "Clothing",
        "image": "https://images.unsplash.com/photo-1542841366-9a30e19bb19a?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTZ8fFdvb2RsYW5kJTIwSGlraW5nJTIwQm9vdHN8ZW58MHx8MHx8fDA%3D",
        "rating": 4.3,
        "reviews": 290,
        "inStock": True
    },
    {
        "id": 12,
        "name": "Ray-Ban Aviator Sunglasses",
        "description": "Classic unisex sunglasses",
        "price": 12999,
        "category": "Clothing",
        "image": "https://images.unsplash.com/photo-1612479121907-15bca39a5388?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTV8fFJheSUyMEJhbiUyMEF2aWF0b3IlMjBTdW5nbGFzc2VzfGVufDB8fDB8fHww",
        "rating": 4.6,
        "reviews": 710,
        "inStock": True
    },
    {
        "id": 13,
        "name": "Gucci Leather Wallet",
        "description": "Luxury leather wallet for men",
        "price": 24999,
        "category": "Clothing",
        "image": "https://images.unsplash.com/photo-1584723344605-03537a1369d5?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NHx8R3VjY2klMjBMZWF0aGVyJTIwV2FsbGV0fGVufDB8fDB8fHww",
        "rating": 4.5,
        "reviews": 180,
        "inStock": True
    },
    {
        "id": 14,
        "name": "Yonex Badminton Racket",
        "description": "Lightweight racket for professional players",
        "price": 6999,
        "category": "Sports",
        "image": "https://images.unsplash.com/photo-1615326882458-e0d45b097f55?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8WW9uZXglMjBCYWRtaW50b24lMjBSYWNrZXR8ZW58MHx8MHx8fDA%3D",
        "rating": 4.7,
        "reviews": 520,
        "inStock": True
    },
    {
        "id": 15,
        "name": "Decathlon Yoga Mat",
        "description": "Non-slip yoga mat with cushioning",
        "price": 2499,
        "category": "Sports",
        "image": "https://plus.unsplash.com/premium_photo-1716025656382-cc9dfe8714a7?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MXx8RGVjYXRobG9uJTIwWW9nYSUyME1hdHxlbnwwfHwwfHx8MA%3D%3D",
        "rating": 4.4,
        "reviews": 330,
        "inStock": True
    }
]

CATEGORIES = ["Electronics", "Clothing", "Books", "Home", "Sports", "Beauty"]

# Routes
@app.get("/")
async def root():
    return {"message": "MegaCart API is running!", "status": "success"}

@app.get("/api/products/", response_model=List[Product])
async def get_products():
    """Get all products"""
    try:
        return PRODUCTS
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch products")

@app.get("/api/products/{product_id}", response_model=Product)
async def get_product(product_id: int):
    """Get single product by ID"""
    try:
        product = next((p for p in PRODUCTS if p["id"] == product_id), None)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch product")

@app.get("/api/categories/", response_model=List[str])
async def get_categories():
    """Get all categories"""
    try:
        return CATEGORIES
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch categories")

# Auth endpoints (basic structure)
class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

@app.post("/api/auth/login")
async def login(request: LoginRequest):
    """Login endpoint (basic implementation)"""
    # This is a basic implementation - replace with proper auth
    if request.email == "test@example.com" and request.password == "password":
        return {
            "access_token": "fake_token_123",
            "token_type": "bearer",
            "user": {
                "id": 1,
                "name": "Test User",
                "email": request.email
            }
        }
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/api/auth/register")
async def register(request: RegisterRequest):
    """Register endpoint (basic implementation)"""
    # This is a basic implementation - replace with proper registration
    return {
        "message": "User registered successfully",
        "user": {
            "id": 2,
            "name": request.name,
            "email": request.email
        }
    }

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "MegaCart API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)