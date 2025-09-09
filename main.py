# main.py - FIXED FastAPI Backend with MongoDB Integration

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional
from pydantic import BaseModel, EmailStr
import json
import hashlib
import os
from datetime import datetime, timedelta
import jwt
from bson import ObjectId

# MongoDB imports
from megacart_backend.database.mongodb import connect_to_mongo, close_mongo_connection, get_database
from megacart_backend.models.mongodb_models import ProductModel

# Create FastAPI app
app = FastAPI(
    title="MegaCart API",
    description="E-commerce API for MegaCart",
    version="1.0.0"
)

allowed_origins = os.getenv("CORS_ORIGINS", "*").split(",")


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    # allow_methods=["*"],
    allow_headers=["*"],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
)

# Authentication setup
security = HTTPBearer()
JWT_SECRET = "your-secret-key-here-change-in-production"
JWT_ALGORITHM = "HS256"

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

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    name: str
    email: str  # Using EmailStr for validation
    password: str

class UserResponse(BaseModel):
    id: str
    name: str
    email: str

# Categories
CATEGORIES = ["Electronics", "Clothing", "Books", "Home", "Sports", "Beauty"]

# Authentication helper functions
def hash_password(password: str) -> str:
    """Simple password hashing"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return hash_password(plain_password) == hashed_password

def create_access_token(user_data: dict) -> str:
    """Create JWT access token"""
    payload = {
        "user_id": str(user_data["_id"]),
        "email": user_data["email"],
        "exp": datetime.utcnow() + timedelta(days=30)  # Token expires in 30 days
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(token: str) -> dict:
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token"""
    try:
        # Verify token
        payload = verify_token(credentials.credentials)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        # Get user from MongoDB
        db = get_database()
        user_id = payload.get("user_id")
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return {
            "id": str(user["_id"]),
            "name": user["name"],
            "email": user["email"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Auth error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )

# Database connection events
@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()

@app.on_event("shutdown") 
async def shutdown_db_client():
    await close_mongo_connection()

# Routes
@app.get("/")
async def root():
    return {"message": "MegaCart API is running!", "status": "success"}

# Product routes
@app.get("/api/products/", response_model=List[dict])
async def get_products():
    """Get all products from MongoDB"""
    try:
        db = get_database()
        products = await db.products.find().to_list(1000)
        
        # Convert ObjectId to string for JSON response
        for product in products:
            product["_id"] = str(product["_id"])
        
        return products
    except Exception as e:
        # Fallback to sample data if MongoDB fails
        SAMPLE_PRODUCTS = [
            {
        "id": 1,
        "name": "iPhone 15 Pro MAX",
        "description": "Latest iPhone with advanced features",
        "price": 99999,
        "category": "Electronics",
        "image": "https://images.unsplash.com/photo-1697284959152-32ef13855932?w=800",
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
    },
    {
        "id": 16,
        "name": "Yoga Mat",
        "description": "Non-slip yoga mat for exercise & meditation.",
        "price": 899.0,
        "category": "Sports",
        "image": "https://images.unsplash.com/photo-1621886178958-be42369fc9e7?w=1400&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8OXx8eW9nYSUyMG1hdHxlbnwwfHwwfHx8MA%3D%3D",
        "rating": 4.5,
        "reviews": 160,
        "inStock": True
    },
    {
        "id": 17,
        "name": "Water Bottle",
        "description": "Stainless steel reusable water bottle.",
        "price": 499.0,
        "category": "Home",
        "image": "https://images.unsplash.com/photo-1625708458528-802ec79b1ed8?w=1400&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NXx8d2F0ZXIlMjBib3R0bGV8ZW58MHx8MHx8fDA%3D",
        "rating": 4.6,
        "reviews": 200,
        "inStock": True
    },
    {
        "id": 18,
        "name": "Sci-Fi Novel",
        "description": "Best-selling science fiction book.",
        "price": 449.0,
        "category": "Books",
        "image": "https://images.unsplash.com/photo-1554357395-dbdc356ca5da?w=1400&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NHx8c2NpJTIwZmklMjBub3ZlbHxlbnwwfHwwfHx8MA%3D%3D",
        "rating": 4.8,
        "reviews": 310,
        "inStock": True
    },
    {
        "id": 19,
        "name": "Ceiling Fan",
        "description": "Energy-efficient ceiling fan with 3 blades.",
        "price": 2499.0,
        "category": "Home",
        "image": "https://images.unsplash.com/photo-1555470100-1728256970aa?w=1400&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NHx8Y2VpbGluZyUyMGZhbnxlbnwwfHwwfHx8MA%3D%3D",
        "rating": 4.3,
        "reviews": 120,
        "inStock": False
    },
    {
        "id": 20,
        "name": "Study Chair",
        "description": "Comfortable ergonomic chair for study & office.",
        "price": 3499.0,
        "category": "Home",
        "image": "https://images.unsplash.com/photo-1619633376278-d8652961ce02?w=1400&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTN8fHN0dWR5JTIwY2hhaXJ8ZW58MHx8MHx8fDA%3D",
        "rating": 4.4,
        "reviews": 75,
        "inStock": True
    },
    {
        "id": 21,
        "name": "Gaming Keyboard",
        "description": "Mechanical RGB keyboard for pro gamers.",
        "price": 3999.0,
        "category": "Electronics",
        "image": "https://images.unsplash.com/photo-1631449061775-c79df03a44f6?w=1400&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NXx8Z2FtaW5nJTIwa2V5Ym9hcmR8ZW58MHx8MHx8fDA%3D",
        "rating": 4.7,
        "reviews": 450,
        "inStock": True
    },
    {
        "id": 22,
        "name": "Smartwatch",
        "description": "Fitness tracking smartwatch with heart rate monitor.",
        "price": 5999.0,
        "category": "Electronics",
        "image": "https://images.unsplash.com/photo-1660844817855-3ecc7ef21f12?w=1400&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NXx8c21hcnR3YXRjaHxlbnwwfHwwfHx8MA%3D%3D",
        "rating": 4.4,
        "reviews": 270,
        "inStock": True
    },
    {
        "id": 23,
        "name": "Cookware Set",
        "description": "Non-stick cookware set for daily cooking needs.",
        "price": 2299.0,
        "category": "Home",
        "image": "https://images.unsplash.com/photo-1584990347449-fd98bc063110?w=1400&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8Y29va3dhcmUlMjBzZXR8ZW58MHx8MHx8fDA%3D",
        "rating": 4.3,
        "reviews": 90,
        "inStock": True
    },
    {
        "id": 24,
        "name": "Men's Jacket",
        "description": "Winter wear jacket with warm lining.",
        "price": 2599.0,
        "category": "Clothing",
        "image": "https://images.unsplash.com/photo-1654719796836-62b889d4598d?w=1400&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8TWVuJ3MlMjBqYWNrZXR8ZW58MHx8MHx8fDA%3D",
        "rating": 4.5,
        "reviews": 110,
        "inStock": True
    },
    {
        "id": 25,
        "name": "Women's Dress",
        "description": "Elegant evening dress for special occasions.",
        "price": 1899.0,
        "category": "Clothing",
        "image" : "https://images.unsplash.com/photo-1753192104240-209f3fb568ef?w=1400&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8N3x8d29tZW4ncyUyMGRyZXNzfGVufDB8fDB8fHww",
        "rating": 4.6,
        "reviews": 95,
        "inStock": True
    },
    {
        "id": 26,
        "name": "Basketball",
        "description": "Official size basketball with durable grip.",
        "price": 799.0,
        "category": "Sports",
        "image": "https://images.unsplash.com/photo-1546519638-68e109498ffc?w=1400&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8QmFza2V0YmFsbHxlbnwwfHwwfHx8MA%3D%3D",
        "rating": 4.4,
        "reviews": 220,
        "inStock": True
    },
    {
        "id": 27,
        "name": "Tennis Racket",
        "description": "Lightweight racket for beginners & pros.",
        "price": 1299.0,
        "category": "Sports",
        "image": "https://plus.unsplash.com/premium_photo-1666913667023-4bfd0f6cff0a?w=1400&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MXx8dGVubmlzJTIwcmFja2V0fGVufDB8fDB8fHww",
        "rating": 4.5,
        "reviews": 140,
        "inStock": True
    },
    {
        "id": 28,
        "name": "Cookbook",
        "description": "Delicious recipes from around the world.",
        "price": 599.0,
        "category": "Books",
        "image": "https://images.unsplash.com/photo-1495546968767-f0573cca821e?w=1400&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8Y29va2Jvb2t8ZW58MHx8MHx8fDA%3D",
        "rating": 4.3,
        "reviews": 80,
        "inStock": True
    },
    {
        "id": 29,
        "name": "Children's Story Book",
        "description": "Illustrated bedtime stories for kids.",
        "price": 299.0,
        "category": "Books",
        "image": "https://images.unsplash.com/photo-1644416598043-11c2816eec28?w=1400&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8Y2hpbGRyZW4ncyUyMHN0b3J5JTIwYm9va3xlbnwwfHwwfHx8MA%3D%3D",
        "rating": 4.8,
        "reviews": 150,
        "inStock": True
    },
    {
        "id": 30,
        "name": "Table Clock",
        "description": "Stylish digital clock with alarm.",
        "price": 799.0,
        "category": "Home",
        "image": "https://images.unsplash.com/photo-1558291038-9e065ab204d5?w=1400&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8VGFibGUlMjBjbG9ja3xlbnwwfHwwfHx8MA%3D%3D",
        "rating": 4.2,
        "reviews": 60,
        "inStock": True
    },
    {
        "id": 31,
        "name": "Laptop Stand",
        "description": "Adjustable laptop stand for better posture.",
        "price": 1299.0,
        "category": "Electronics",
        "image": "https://images.unsplash.com/photo-1623251606108-512c7c4a3507?w=1400&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8TGFwdG9wJTIwc3RhbmR8ZW58MHx8MHx8fDA%3D",
        "rating": 4.6,
        "reviews": 180,
        "inStock": True
    },
    {
        "id": 32,
        "name": "Men's Hoodie",
        "description": "Casual hoodie with front pocket.",
        "price": 1199.0,
        "category": "Clothing",
        "image": "https://images.unsplash.com/photo-1727528772898-10616410003d?w=1400&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NHx8bWVuJ3MlMjBob29kaWV8ZW58MHx8MHx8fDA%3D",
        "rating": 4.5,
        "reviews": 130,
        "inStock": True
    },
    {
        "id": 33,
        "name": "Women's Scarf",
        "description": "Soft woolen scarf for winter season.",
        "price": 699.0,
        "category": "Clothing",
        "image": "https://plus.unsplash.com/premium_photo-1674343618059-926174e2c9b7?w=1400&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTB8fHdvbWVuJ3MlMjBzY2FyZnxlbnwwfHwwfHx8MA%3D%3D",
        "rating": 4.4,
        "reviews": 75,
        "inStock": True
    },
    {
        "id": 34,
        "name": "Vacuum Cleaner",
        "description": "Compact vacuum cleaner for home use.",
        "price": 3999.0,
        "category": "Home",
        "image": "https://images.unsplash.com/photo-1527515637462-cff94eecc1ac?q=80&w=1374&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
        "rating": 4.3,
        "reviews": 100,
        "inStock": True
    },
    {
        "id": 35,
        "name": "E-Reader",
        "description": "Portable e-book reader with long battery life.",
        "price": 7999.0,
        "category": "Electronics",
        "image": "https://images.unsplash.com/photo-1676107779674-f77343861e81?w=1400&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NHx8ZSUyMHJlYWRlcnxlbnwwfHwwfHx8MA%3D%3D",
        "rating": 4.7,
        "reviews": 220,
        "inStock": True
    },
    {
        "id": 36,
        "name": "Lipstick",
        "description": "Matte finish long-lasting lipstick.",
        "price": 499.0,
        "category": "Beauty",
        "image": "https://plus.unsplash.com/premium_photo-1677526496932-1b4bddeee554?w=1400&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MXx8bGlwc3RpY2t8ZW58MHx8MHx8fDA%3D",
        "rating": 4.5,
        "reviews": 210,
        "inStock": True
    },
    {
        "id": 37,
        "name": "Foundation",
        "description": "Liquid foundation with SPF 15.",
        "price": 799.0,
        "category": "Beauty",
        "image": "https://images.unsplash.com/photo-1557205465-f3762edea6d3?w=1400&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8Zm91bmRhdGlvbnxlbnwwfHwwfHx8MA%3D%3D",
        "rating": 4.3,
        "reviews": 180,
        "inStock": True
    },
    {
        "id": 38,
        "name": "Face Cream",
        "description": "Moisturizing face cream for daily use.",
        "price": 699.0,
        "category": "Beauty",
        "image": "https://images.unsplash.com/photo-1629380108660-bd39c778a721?w=1400&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NHx8ZmFjZSUyMGNyZWFtfGVufDB8fDB8fHww",
        "rating": 4.4,
        "reviews": 240,
        "inStock": True
    },
    {
        "id": 39,
        "name": "Perfume",
        "description": "Floral fragrance perfume for women.",
        "price": 1299.0,
        "category": "Beauty",
        "image": "https://images.unsplash.com/photo-1458538977777-0549b2370168?w=1400&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NHx8cGVyZnVtZXxlbnwwfHwwfHx8MA%3D%3D",
        "rating": 4.6,
        "reviews": 310,
        "inStock": True
    },
    {
        "id": 40,
        "name": "Eyeliner",
        "description": "Waterproof black eyeliner pen.",
        "price": 299.0,
        "category": "Beauty",
        "image": "https://images.unsplash.com/photo-1631214524020-7e18db9a8f92?w=1400&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NHx8ZXllbGluZXJ8ZW58MHx8MHx8fDA%3D",
        "rating": 4.2,
        "reviews": 150,
        "inStock": True
    },
    {
        "id": 41,
        "name": "Nail Polish",
        "description": "Glossy finish red nail polish.",
        "price": 199.0,
        "category": "Beauty",
        "image": "https://images.unsplash.com/photo-1723647395168-d916159b78c9?w=1400&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NHx8TmFpbCUyMHBvbGlzaHxlbnwwfHwwfHx8MA%3D%3D",
        "rating": 4.1,
        "reviews": 120,
        "inStock": True
    },
    {
        "id": 42,
        "name": "Face Wash",
        "description": "Herbal face wash for glowing skin.",
        "price": 349.0,
        "category": "Beauty",
        "image": "https://images.unsplash.com/photo-1653919198052-546d44e2458e?w=1400&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8ZmFjZSUyMHdhc2h8ZW58MHx8MHx8fDA%3D",
        "rating": 4.4,
        "reviews": 280,
        "inStock": True
    },
    {
        "id": 43,
        "name": "Hair Serum",
        "description": "Smooth and shiny hair serum.",
        "price": 599.0,
        "category": "Beauty",
        "image": "https://images.unsplash.com/photo-1610595426075-eed5a3f521ee?w=1400&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NHx8aGFpciUyMHNlcnVtfGVufDB8fDB8fHww",
        "rating": 4.3,
        "reviews": 170,
        "inStock": True
    },
    {
        "id": 44,
        "name": "Compact Powder",
        "description": "Oil-control compact powder.",
        "price": 399.0,
        "category": "Beauty",
        "image": "https://images.unsplash.com/photo-1737014892220-4123c7e020a1?w=1400&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8Y29tcGFjdCUyMHBvd2RlcnxlbnwwfHwwfHx8MA%3D%3D",
        "rating": 4.2,
        "reviews": 140,
        "inStock": True
    },
    {
        "id": 45,
        "name": "Makeup Brush Set",
        "description": "Professional 12-piece makeup brush set.",
        "price": 999.0,
        "category": "Beauty",
        "image": "https://images.unsplash.com/photo-1736753365978-0b5090f90095?w=1400&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8bWFrZXVwJTIwYnJ1c2glMjBzZXR8ZW58MHx8MHx8fDA%3D",
        "rating": 4.7,
        "reviews": 390,
        "inStock": True
    }
        ]
        return SAMPLE_PRODUCTS

@app.get("/api/products/{product_id}")
async def get_product(product_id: str):
    """Get single product by ID from MongoDB"""
    try:
        db = get_database()
        
        # Try to find by ObjectId first
        try:
            product = await db.products.find_one({"_id": ObjectId(product_id)})
        except:
            # If not ObjectId, try by integer id
            product = await db.products.find_one({"id": int(product_id)})
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        product["_id"] = str(product["_id"])
        return product
    except Exception as e:
        raise HTTPException(status_code=404, detail="Product not found")

@app.get("/api/categories/", response_model=List[str])
async def get_categories():
    """Get all categories"""
    try:
        return CATEGORIES
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch categories")

# Authentication routes - FIXED
@app.post("/auth/register")
async def register_user(request: RegisterRequest):
    """Register new user in MongoDB - FIXED"""
    try:
        # Enhanced validation
        if not request.name or len(request.name.strip()) < 2:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
                detail="Name must be at least 2 characters long"
            )
        
        if not request.email or "@" not in request.email:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
                detail="Please provide a valid email address"
            )
            
        if not request.password or len(request.password) < 6:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
                detail="Password must be at least 6 characters long"
            )
        
        # Get database
        db = get_database()
        
        # Check if user already exists
        existing_user = await db.users.find_one({"email": request.email.lower().strip()})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="An account with this email already exists"
            )
        
        # Create new user document
        hashed_password = hash_password(request.password)
        
        new_user_data = {
            "name": request.name.strip(),
            "email": request.email.lower().strip(),
            "password": hashed_password,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Insert user into MongoDB
        print(f"Attempting to insert user: {new_user_data['email']}")
        result = await db.users.insert_one(new_user_data)
        
        if not result.inserted_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user account"
            )
        
        # Add the _id to our user data for token creation
        new_user_data["_id"] = result.inserted_id
        
        # Create access token
        access_token = create_access_token(new_user_data)
        
        # Prepare user response (without password)
        user_response = {
            "id": str(new_user_data["_id"]),
            "name": new_user_data["name"],
            "email": new_user_data["email"]
        }
        
        print(f"User registered successfully: {user_response['email']}")
        
        # Return response matching frontend expectations
        return {
            "message": "User registered successfully",
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_response
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Registration error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Registration failed: {str(e)}"
        )

@app.post("/auth/login")
async def login_user(request: LoginRequest):
    """Login user from MongoDB - FIXED"""
    try:
        email = request.email.lower().strip()
        password = request.password
        
        # Basic validation
        if not email or not password:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Email and password are required"
            )
        
        # Get database
        db = get_database()
        
        # Find user in MongoDB
        print(f"Attempting login for email: {email}")
        user = await db.users.find_one({"email": email})
        
        if not user:
            print(f"User not found: {email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid email or password"
            )
        
        # Verify password
        if not verify_password(password, user["password"]):
            print(f"Password mismatch for user: {email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid email or password"
            )
        
        # Create access token
        access_token = create_access_token(user)
        
        # Prepare user response
        user_response = {
            "id": str(user["_id"]),
            "name": user["name"],
            "email": user["email"]
        }
        
        print(f"Login successful for user: {email}")
        
        return {
            "message": "Login successful",
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_response
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Login failed: {str(e)}"
        )

@app.get("/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user data"""
    return current_user

# Database debugging endpoints
@app.get("/auth/users")
async def get_all_users():
    """Get all registered users from MongoDB (for debugging)"""
    try:
        db = get_database()
        users = await db.users.find({}, {"password": 0}).to_list(100)  # Exclude passwords
        
        # Convert ObjectId to string
        for user in users:
            user["_id"] = str(user["_id"])
        
        return {
            "total_users": len(users),
            "users": users
        }
    except Exception as e:
        print(f"Error fetching users: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch users")

@app.get("/debug/db-connection")
async def test_db_connection():
    """Test MongoDB connection"""
    try:
        db = get_database()
        # Try to ping the database
        result = await db.command("ping")
        
        # Count users
        user_count = await db.users.count_documents({})
        
        return {
            "database_connected": True,
            "ping_result": result,
            "total_users": user_count,
            "collections": await db.list_collection_names()
        }
    except Exception as e:
        return {
            "database_connected": False,
            "error": str(e)
        }

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "MegaCart API"}

# Protected route example
@app.get("/api/profile")
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """Get user profile (protected route)"""
    return {
        "message": "This is a protected route",
        "user": current_user
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

# Required packages:
# pip install PyJWT
# pip install python-multipart
# pip install motor  # MongoDB async driver