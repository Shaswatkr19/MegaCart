# routers/auth.py - Fixed version
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from megacart_backend.database import get_db  # ✅ Add this import
from megacart_backend.models.user import Megacartuser
from megacart_backend.schemas.user import UserCreate, UserResponse, Token
from passlib.context import CryptContext
from megacart_backend.core.security import create_access_token, verify_token
from datetime import timedelta

# Password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

megacart_auth = APIRouter(prefix="/api/auth", tags=["MegaCart Authentication"])

@megacart_auth.post("/signup", response_model=UserResponse)
async def megacart_signup(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check existing user
    existing_user = db.query(Megacartuser).filter(
        (Megacartuser.email == user_data.email) |
        (Megacartuser.username == user_data.username)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Username or email already registered in MegaCart"
        )
    
    # Hash password
    hashed_password = pwd_context.hash(user_data.password)
    
    # Create new MegaCart user
    new_user = Megacartuser(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@megacart_auth.post("/login", response_model=Token)
async def megacart_login(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    """MegaCart User Login"""
    # Find MegaCart user
    user = db.query(Megacartuser).filter(
        Megacartuser.username == form_data.username
    ).first()
    
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid MegaCart credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create JWT token
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=30)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active
        }
    }

# Get current user helper
async def get_current_megacart_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate MegaCart credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    username = verify_token(token)
    if username is None:
        raise credentials_exception
        
    user = db.query(Megacartuser).filter(Megacartuser.username == username).first()
    if user is None:
        raise credentials_exception
        
    return user

@megacart_auth.get("/me", response_model=UserResponse)
async def get_megacart_profile(current_user: Megacartuser = Depends(get_current_megacart_user)):
    """Get current MegaCart user profile"""
    return current_user