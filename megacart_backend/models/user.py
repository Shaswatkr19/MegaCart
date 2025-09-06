# megacart_backend/models/user.py - FIXED VERSION
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from megacart_backend.database import Base  # ✅ Correct import path

class Megacartuser(Base):
    __tablename__ = "megacart_users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())