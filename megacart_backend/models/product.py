from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class MegaCartCategory(Base):
    __tablename__ = "megacart_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text)
    image_url = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    products = relationship("MegacartProduct", back_populates="category")

class MegacartProduct(Base):
    __tablename__ = "megacart_products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    price = Column(Float)
    original_price = Column(Float)
    stock_quantity = Column(Integer, default=0)
    sku = Column(String, unique=True, index=True)
    image_url = Column(String)
    images = Column(Text)

    category_id = Column(Integer, ForeignKey("megacart_categories.id"))
    category = relationship("MegacartCategory", back_populates="products")
    
    # Product status
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)  # For homepage
    
    # SEO & extras
    slug = Column(String, unique=True, index=True)  # URL friendly name
    tags = Column(String)  # Comma separated tags
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


