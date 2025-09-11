# main.py - IMPROVED FastAPI Backend with Better MongoDB Handling

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Any, List, Optional
from pydantic import BaseModel
import json
import hashlib
import os
from datetime import datetime, timedelta
import jwt
from bson import ObjectId
import traceback
import asyncio

# MongoDB imports with error handling
try:
    from megacart_backend.database.mongodb import connect_to_mongo, close_mongo_connection, get_database, execute_with_retry
    MONGODB_AVAILABLE = True
    print("✅ MongoDB modules loaded successfully")
except ImportError as e:
    print(f"❌ MongoDB modules not available: {e}")
    MONGODB_AVAILABLE = False

# Create FastAPI app
app = FastAPI(
    title="MegaCart API",
    description="E-commerce API for MegaCart",
    version="1.0.0"
)

# CORS middleware - More permissive for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication setup
security = HTTPBearer(auto_error=False)
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
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    name: str
    email: str

# Categories and Enhanced Sample Data
CATEGORIES = ["Electronics", "Clothing", "Books", "Home", "Sports", "Beauty"]

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
        "description": "Smartwatch with fitness tracking",
        "price": 45999,
        "category": "Electronics",
        "image": "https://images.unsplash.com/photo-1644235779485-e4d021d8edab?w=400",
        "rating": 4.6,
        "reviews": 870,
        "inStock": True
    },
    {
        "id": 7,
        "name": "Gaming Headset",
        "description": "High-quality gaming headphones",
        "price": 5999,
        "category": "Electronics",
        "image": "https://images.unsplash.com/photo-1583394838336-acd977736f90?w=400",
        "rating": 4.5,
        "reviews": 320,
        "inStock": True
    },
    {
        "id": 8,
        "name": "Casual T-Shirt",
        "description": "Comfortable cotton t-shirt",
        "price": 999,
        "category": "Clothing",
        "image": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400",
        "rating": 4.3,
        "reviews": 150,
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
    },
    {
        "id": 46,
        "name": "Apple iPhone 17 Pro",
        "description": "Next-generation iPhone with A19 Bionic chip, advanced cameras, and ProMotion display.",
        "price": 139999,
        "category": "Mobiles",
        "image": "https://images.unsplash.com/photo-1695048132545-3f879a3d1234?w=800",
        "rating": 4.9,
        "reviews": 1200,
        "inStock": True
    },
    {
        "id": 47,
        "name": "Samsung Galaxy Z Fold 6",
        "description": "Next-gen foldable smartphone with multitasking features.",
        "price": 154999,
        "category": "Mobiles",
        "image": "https://images.unsplash.com/photo-1592899677977-9e04b2e5f73d?w=800",
        "rating": 4.7,
        "reviews": 890,
        "inStock": True
    },
    {
        "id": 48,
        "name": "Puma Sports T-Shirt",
        "description": "Breathable and lightweight t-shirt for workouts and casual wear.",
        "price": 1299,
        "category": "Clothing",
        "image": "https://images.unsplash.com/photo-1512436991641-6745cdb1723f?w=800",
        "rating": 4.3,
        "reviews": 210,
        "inStock": True
    },
    {
        "id": 49,
        "name": "Woodland Leather Boots",
        "description": "Durable outdoor boots with rugged sole for trekking.",
        "price": 4999,
        "category": "Footwear",
        "image": "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=800",
        "rating": 4.5,
        "reviews": 340,
        "inStock": True
    },
    {
        "id": 50,
        "name": "Nike Backpack Pro",
        "description": "Stylish and spacious backpack for college and travel.",
        "price": 3499,
        "category": "Bags",
        "image": "https://images.unsplash.com/photo-1622560480605-d83c853bc5c4?w=800",
        "rating": 4.6,
        "reviews": 270,
        "inStock": True
    },
    {
        "id": 51,
        "name": "Philips Air Fryer XL",
        "description": "Oil-free air fryer for healthy and tasty cooking.",
        "price": 11999,
        "category": "Home Appliances",
        "image": "https://images.unsplash.com/photo-1617196038435-6cdd9d8a8d89?w=800",
        "rating": 4.7,
        "reviews": 510,
        "inStock": True
    },
    {
        "id": 52,
        "name": "Yonex Badminton Racket",
        "description": "Lightweight graphite racket for professional gameplay.",
        "price": 3999,
        "category": "Sports",
        "image": "https://images.unsplash.com/photo-1587385789096-019d2908b00b?w=800",
        "rating": 4.5,
        "reviews": 190,
        "inStock": True
    },
    {
        "id": 53,
        "name": "Allen Solly Formal Shirt",
        "description": "Cotton slim-fit shirt perfect for office wear.",
        "price": 2199,
        "category": "Clothing",
        "image": "https://images.unsplash.com/photo-1523381210434-271e8be1f52b?w=800",
        "rating": 4.4,
        "reviews": 300,
        "inStock": True
    },
    {
        "id": 54,
        "name": "Prestige Mixer Grinder",
        "description": "500W mixer grinder with 3 jars for multipurpose kitchen use.",
        "price": 4999,
        "category": "Kitchen",
        "image": "https://images.unsplash.com/photo-1606787366850-de6330128bfc?w=800",
        "rating": 4.6,
        "reviews": 280,
        "inStock": True
    },
    {
        "id": 55,
        "name": "Fossil Gen 7 Smartwatch",
        "description": "Smartwatch with heart rate monitor and fitness tracking.",
        "price": 18999,
        "category": "Watches",
        "image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800",
        "rating": 4.5,
        "reviews": 420,
        "inStock": True
    },
    {
        "id": 56,
        "name": "Wildcraft Travel Duffel",
        "description": "Durable duffel bag with 3 compartments for travel.",
        "price": 2599,
        "category": "Bags",
        "image": "https://images.unsplash.com/photo-1600180758895-6d09c0e7a94f?w=800",
        "rating": 4.4,
        "reviews": 180,
        "inStock": True
    },
    {
        "id": 57,
        "name": "Adidas Football",
        "description": "FIFA quality pro football with excellent grip and durability.",
        "price": 2499,
        "category": "Sports",
        "image": "https://images.unsplash.com/photo-1551958219-acbc608c6377?w=800",
        "rating": 4.7,
        "reviews": 390,
        "inStock": True
        },
        {
        "id": 58,
        "name": "Cannon DSLR Camera Bag",
        "description": "Protective and stylish camera bag with waterproof coating.",
        "price": 2999,
        "category": "Accessories",
        "image": "https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=800",
        "rating": 4.6,
        "reviews": 210,
        "inStock": True
    },
    {
        "id": 59,
        "name": "Levi's Denim Jacket",
        "description": "Classic denim jacket with modern slim fit.",
        "price": 5499,
        "category": "Clothing",
        "image": "https://images.unsplash.com/photo-1520975918319-9de52b3f91b8?w=800",
        "rating": 4.8,
        "reviews": 370,
        "inStock": True
    },
    {
        "id": 60,
        "name": "Butterfly Gas Stove 3 Burner",
        "description": "Stainless steel gas stove with 3 high-efficiency burners.",
        "price": 7499,
        "category": "Kitchen",
        "image": "https://images.unsplash.com/photo-1601050690685-f3e4f0b3f6d6?w=800",
        "rating": 4.5,
        "reviews": 260,
        "inStock": True
    },
    {
        "id": 61,
        "name": "Skybags Laptop Bag",
        "description": "Ergonomic laptop bag with water-resistant fabric.",
        "price": 3299,
        "category": "Bags",
        "image": "https://images.unsplash.com/photo-1522199710521-72d69614c702?w=800",
        "rating": 4.6,
        "reviews": 310,
        "inStock": True
    },
    {
        "id": 62,
        "name": "Decathlon Yoga Mat",
        "description": "Eco-friendly yoga mat with non-slip surface.",
        "price": 1599,
        "category": "Sports",
        "image": "https://images.unsplash.com/photo-1599058917212-d750089bc07a?w=800",
        "rating": 4.7,
        "reviews": 420,
        "inStock": True
    },
    {
        "id": 63,
        "name": "Ray-Ban Wayfarer",
        "description": "Classic sunglasses with UV protection.",
        "price": 7999,
        "category": "Accessories",
        "image": "https://images.unsplash.com/photo-1602524812106-3f2e2a6b9d9d?w=800",
        "rating": 4.6,
        "reviews": 500,
        "inStock": True
    },
    {
        "id": 64,
        "name": "Nike Running Shorts",
        "description": "Comfortable and lightweight shorts for running and gym.",
        "price": 1799,
        "category": "Clothing",
        "image": "https://images.unsplash.com/photo-1533000971552-6a962ff0b9f8?w=800",
        "rating": 4.4,
        "reviews": 230,
        "inStock": True
    }
]

# In-memory user storage (fallback)
FALLBACK_USERS = {}

# Global database connection flag
DB_CONNECTED = False

# Authentication helper functions
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password

def create_access_token(user_data: dict) -> str:
    user_id = str(user_data.get("_id", user_data.get("id", "fallback_id")))
    payload = {
        "user_id": user_id,
        "email": user_data["email"],
        "exp": datetime.utcnow() + timedelta(days=30)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    try:
        payload = verify_token(credentials.credentials)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        user_id = payload.get("user_id")
        email = payload.get("email")
        
        # Try MongoDB with retry mechanism
        if DB_CONNECTED and MONGODB_AVAILABLE:
            try:
                async def find_user():
                    db = get_database()
                    try:
                        return await db.users.find_one({"_id": ObjectId(user_id)})
                    except:
                        return await db.users.find_one({"email": email})
                
                user = await execute_with_retry(find_user, max_retries=2, delay=0.5)
                
                if user:
                    return {
                        "id": str(user["_id"]),
                        "name": user["name"],
                        "email": user["email"]
                    }
            except Exception as e:
                print(f"❌ MongoDB user fetch error: {e}")
        
        # Fallback to in-memory storage
        if email in FALLBACK_USERS:
            user = FALLBACK_USERS[email]
            return {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"]
            }
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Auth error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )

# Database connection events with better error handling
@app.on_event("startup")
async def startup_db_client():
    global DB_CONNECTED
    print("🚀 Starting MegaCart API...")
    
    if MONGODB_AVAILABLE:
        try:
            # Give MongoDB connection a bit more time but with timeout
            connection_successful = await asyncio.wait_for(
                connect_to_mongo(), 
                timeout=10.0
            )
            
            if connection_successful:
                DB_CONNECTED = True
                print("✅ MongoDB connected and ready")
                
                # Test a simple operation
                try:
                    db = get_database()
                    await db.admin.command('ping')
                    print("✅ MongoDB ping successful")
                except Exception as e:
                    print(f"⚠️ MongoDB ping failed: {e}")
                    
            else:
                print("❌ MongoDB connection failed, using fallback mode")
                DB_CONNECTED = False
                
        except asyncio.TimeoutError:
            print("❌ MongoDB connection timeout, using fallback mode")
            DB_CONNECTED = False
        except Exception as e:
            print(f"❌ MongoDB connection error: {e}")
            print("🔄 Using fallback mode")
            DB_CONNECTED = False
    else:
        print("⚠️ MongoDB not available, using fallback storage")
        DB_CONNECTED = False
    
    print(f"🏪 MegaCart API started in {'MongoDB' if DB_CONNECTED else 'Fallback'} mode")

@app.on_event("shutdown") 
async def shutdown_db_client():
    global DB_CONNECTED
    if MONGODB_AVAILABLE and DB_CONNECTED:
        try:
            await close_mongo_connection()
        except Exception as e:
            print(f"❌ Error closing MongoDB: {e}")
    DB_CONNECTED = False

# Routes
@app.get("/")
async def root():
    return {
        "message": "MegaCart API is running!", 
        "status": "success",
        "database_mode": "MongoDB" if DB_CONNECTED else "Fallback",
        "mongodb_available": MONGODB_AVAILABLE,
        "fallback_users": len(FALLBACK_USERS),
        "sample_products": len(SAMPLE_PRODUCTS)
    }

# Product routes with improved error handling
@app.get("/api/products/", response_model=List[Any])
async def get_products():
    """Get all products - Always works with fallback"""
    print("🛒 Fetching products...")
    
    # Try MongoDB first if available
    if DB_CONNECTED and MONGODB_AVAILABLE:
        try:
            async def fetch_products():
                db = get_database()
                return await db.products.find().to_list(1000)
            
            # Use retry mechanism for MongoDB
            products = await execute_with_retry(fetch_products, max_retries=2, delay=0.5)
            
            if products and len(products) > 0:
                for product in products:
                    product["_id"] = str(product["_id"])
                print(f"✅ Returned {len(products)} products from MongoDB")
                return products
            else:
                print("⚠️ No products found in MongoDB, using fallback")
                
        except Exception as e:
            print(f"❌ MongoDB products fetch failed: {e}")
    
    # Always return sample data as fallback
    print(f"✅ Returned {len(SAMPLE_PRODUCTS)} sample products (fallback)")
    return SAMPLE_PRODUCTS

@app.get("/api/products/{product_id}")
async def get_product(product_id: str):
    """Get single product by ID"""
    print(f"🔍 Fetching product ID: {product_id}")
    
    # Try MongoDB first if available
    if DB_CONNECTED and MONGODB_AVAILABLE:
        try:
            async def fetch_single_product():
                db = get_database()
                try:
                    return await db.products.find_one({"_id": ObjectId(product_id)})
                except:
                    return await db.products.find_one({"id": int(product_id)})
            
            product = await execute_with_retry(fetch_single_product, max_retries=2, delay=0.5)
            
            if product:
                product["_id"] = str(product["_id"])
                print(f"✅ Found product in MongoDB: {product.get('name', 'Unknown')}")
                return product
                
        except Exception as e:
            print(f"❌ MongoDB single product fetch failed: {e}")
    
    # Fallback to sample data
    try:
        product_id_int = int(product_id)
        for product in SAMPLE_PRODUCTS:
            if product["id"] == product_id_int:
                print(f"✅ Found product in fallback: {product['name']}")
                return product
    except ValueError:
        pass
    
    print(f"❌ Product not found: {product_id}")
    raise HTTPException(status_code=404, detail="Product not found")

@app.get("/api/categories/", response_model=List[str])
async def get_categories():
    """Get all categories - Always works"""
    return CATEGORIES

# Authentication routes - IMPROVED with better error handling
@app.post("/auth/register")
async def register_user(request: RegisterRequest):
    """Register new user - Works with fallback"""
    try:
        print(f"📝 Registration attempt for: {request.email}")
        
        # Enhanced validation
        if not request.name or len(request.name.strip()) < 2:
            raise HTTPException(
                status_code=422, 
                detail="Name must be at least 2 characters long"
            )
        
        if not request.email or "@" not in request.email:
            raise HTTPException(
                status_code=422, 
                detail="Please provide a valid email address"
            )
            
        if not request.password or len(request.password) < 6:
            raise HTTPException(
                status_code=422, 
                detail="Password must be at least 6 characters long"
            )
        
        email = request.email.lower().strip()
        name = request.name.strip()
        hashed_password = hash_password(request.password)
        
        # Try MongoDB first if available
        if DB_CONNECTED and MONGODB_AVAILABLE:
            try:
                async def register_in_mongodb():
                    db = get_database()
                    
                    # Check if user exists
                    existing_user = await db.users.find_one({"email": email})
                    if existing_user:
                        raise HTTPException(status_code=400, detail="User already exists")
                    
                    # Create user
                    new_user_data = {
                        "name": name,
                        "email": email,
                        "password": hashed_password,
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                    
                    result = await db.users.insert_one(new_user_data)
                    new_user_data["_id"] = result.inserted_id
                    return new_user_data
                
                user_data = await execute_with_retry(register_in_mongodb, max_retries=2, delay=0.5)
                
                if user_data:
                    access_token = create_access_token(user_data)
                    user_response = {
                        "id": str(user_data["_id"]),
                        "name": name,
                        "email": email
                    }
                    
                    print(f"✅ User registered in MongoDB: {email}")
                    
                    return {
                        "message": "User registered successfully",
                        "access_token": access_token,
                        "token_type": "bearer",
                        "user": user_response
                    }
                    
            except HTTPException:
                raise
            except Exception as e:
                print(f"❌ MongoDB registration failed: {e}")
        
        # Fallback to in-memory storage
        if email in FALLBACK_USERS:
            raise HTTPException(
                status_code=400, 
                detail="An account with this email already exists"
            )
        
        # Create user in fallback storage
        user_id = f"user_{len(FALLBACK_USERS) + 1}"
        user_data = {
            "id": user_id,
            "_id": user_id,
            "name": name,
            "email": email,
            "password": hashed_password,
            "created_at": datetime.utcnow()
        }
        
        FALLBACK_USERS[email] = user_data
        
        access_token = create_access_token(user_data)
        user_response = {
            "id": user_id,
            "name": name,
            "email": email
        }
        
        print(f"✅ User registered in fallback storage: {email}")
        
        return {
            "message": "User registered successfully (fallback mode)",
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_response
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Registration error: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500, 
            detail=f"Registration failed: {str(e)}"
        )

@app.post("/auth/login")
async def login_user(request: LoginRequest):
    """Login user - Works with fallback"""
    try:
        print(f"🔐 Login attempt for: {request.email}")
        
        email = request.email.lower().strip()
        password = request.password
        
        if not email or not password:
            raise HTTPException(
                status_code=422,
                detail="Email and password are required"
            )
        
        # Try MongoDB first if available
        if DB_CONNECTED and MONGODB_AVAILABLE:
            try:
                async def login_from_mongodb():
                    db = get_database()
                    return await db.users.find_one({"email": email})
                
                user = await execute_with_retry(login_from_mongodb, max_retries=2, delay=0.5)
                
                if user and verify_password(password, user["password"]):
                    access_token = create_access_token(user)
                    user_response = {
                        "id": str(user["_id"]),
                        "name": user["name"],
                        "email": user["email"]
                    }
                    
                    print(f"✅ MongoDB login successful: {email}")
                    
                    return {
                        "message": "Login successful",
                        "access_token": access_token,
                        "token_type": "bearer",
                        "user": user_response
                    }
                    
            except Exception as e:
                print(f"❌ MongoDB login error: {e}")
        
        # Fallback to in-memory storage
        if email in FALLBACK_USERS:
            user = FALLBACK_USERS[email]
            
            if verify_password(password, user["password"]):
                access_token = create_access_token(user)
                user_response = {
                    "id": user["id"],
                    "name": user["name"],
                    "email": user["email"]
                }
                
                print(f"✅ Fallback login successful: {email}")
                
                return {
                    "message": "Login successful (fallback mode)",
                    "access_token": access_token,
                    "token_type": "bearer",
                    "user": user_response
                }
        
        print(f"❌ Login failed for: {email}")
        raise HTTPException(
            status_code=401, 
            detail="Invalid email or password"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Login error: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500, 
            detail=f"Login failed: {str(e)}"
        )

@app.get("/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user data"""
    return current_user

# Database debugging endpoints
@app.get("/auth/users")
async def get_all_users():
    """Get all registered users (for debugging)"""
    try:
        users = []
        
        # Try MongoDB first
        if DB_CONNECTED and MONGODB_AVAILABLE:
            try:
                async def fetch_mongo_users():
                    db = get_database()
                    return await db.users.find({}, {"password": 0}).to_list(100)
                
                mongo_users = await execute_with_retry(fetch_mongo_users, max_retries=2, delay=0.5)
                
                if mongo_users:
                    for user in mongo_users:
                        user["_id"] = str(user["_id"])
                        user["source"] = "MongoDB"
                    users.extend(mongo_users)
                    
            except Exception as e:
                print(f"❌ Error fetching MongoDB users: {e}")
        
        # Add fallback users
        for email, user in FALLBACK_USERS.items():
            users.append({
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "source": "Fallback",
                "created_at": user.get("created_at")
            })
        
        return {
            "total_users": len(users),
            "database_connected": DB_CONNECTED,
            "mongodb_available": MONGODB_AVAILABLE,
            "users": users
        }
        
    except Exception as e:
        print(f"❌ Error in get_all_users: {e}")
        return {
            "total_users": len(FALLBACK_USERS),
            "database_connected": False,
            "error": str(e),
            "users": [
                {
                    "id": user["id"],
                    "name": user["name"],
                    "email": user["email"],
                    "source": "Fallback"
                }
                for user in FALLBACK_USERS.values()
            ]
        }

@app.get("/debug/db-connection")
async def test_db_connection():
    """Test MongoDB connection"""
    return {
        "mongodb_modules_available": MONGODB_AVAILABLE,
        "database_connected": DB_CONNECTED,
        "fallback_users_count": len(FALLBACK_USERS),
        "sample_products_count": len(SAMPLE_PRODUCTS),
        "status": "MongoDB" if DB_CONNECTED else "Fallback Mode"
    }

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "MegaCart API",
        "database_mode": "MongoDB" if DB_CONNECTED else "Fallback Mode",
        "fallback_users": len(FALLBACK_USERS),
        "mongodb_available": MONGODB_AVAILABLE
    }

# Protected route example
@app.get("/api/profile")
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """Get user profile (protected route)"""
    return {
        "message": "This is a protected route",
        "user": current_user,
        "source": "MongoDB" if DB_CONNECTED else "Fallback"
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting MegaCart API...")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)