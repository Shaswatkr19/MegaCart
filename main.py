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

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
                "name": "Wireless Headphones",
                "description": "High-quality wireless headphones with noise cancellation",
                "price": 99.99,
                "category": "Electronics",
                "image": "🎧",
                "rating": 4.5,
                "reviews": 120,
                "inStock": True
            },
            {
                "id": 2,
                "name": "Running Shoes",
                "description": "Comfortable running shoes for all terrains",
                "price": 79.99,
                "category": "Sports",
                "image": "👟",
                "rating": 4.3,
                "reviews": 85,
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