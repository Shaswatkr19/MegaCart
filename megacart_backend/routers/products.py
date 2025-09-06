# routers/products.py - MegaCart Product APIs
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models.product import MegacartProduct, MegacartCategory
from schemas.product import (
    ProductResponse, ProductCreate, ProductUpdate, 
    CategoryResponse, CategoryCreate, ProductListResponse
)
import re
from math import ceil

megacart_products = APIRouter(prefix="/api/products", tags=["MegaCart Products"])

# Helper function to create slug
def create_slug(name: str) -> str:
    slug = re.sub(r'[^\w\s-]', '', name.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')

# ========== CATEGORIES ==========

@megacart_products.get("/categories", response_model=List[CategoryResponse])
async def get_megacart_categories(db: Session = Depends(get_db)):
    """Get all MegaCart categories"""
    categories = db.query(MegacartCategory).filter(MegacartCategory.is_active == True).all()
    return categories

@megacart_products.post("/categories", response_model=CategoryResponse)
async def create_megacart_category(
    category_data: CategoryCreate, 
    db: Session = Depends(get_db)
):
    """Create new MegaCart category"""
    # Check if category exists
    existing = db.query(MegacartCategory).filter(MegacartCategory.name == category_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists in MegaCart")
    
    new_category = MegacartCategory(**category_data.dict())
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    
    return new_category

# ========== PRODUCTS ==========

@megacart_products.get("/", response_model=ProductListResponse)
async def get_megacart_products(
    category_id: Optional[int] = Query(None, description="Filter by MegaCart category"),
    search: Optional[str] = Query(None, description="Search MegaCart products"),
    min_price: Optional[float] = Query(None, description="Minimum price"),
    max_price: Optional[float] = Query(None, description="Maximum price"),
    featured_only: Optional[bool] = Query(False, description="Featured products only"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """Get MegaCart products with filters"""
    
    # Base query
    query = db.query(MegacartProduct).filter(MegacartProduct.is_active == True)
    
    # Apply filters
    if category_id:
        query = query.filter(MegacartProduct.category_id == category_id)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            MegacartProduct.name.ilike(search_term) |
            MegacartProduct.description.ilike(search_term) |
            MegacartProduct.tags.ilike(search_term)
        )
    
    if min_price:
        query = query.filter(MegacartProduct.price >= min_price)
    
    if max_price:
        query = query.filter(MegacartProduct.price <= max_price)
        
    if featured_only:
        query = query.filter(MegacartProduct.is_featured == True)
    
    # Get total count
    total_count = query.count()
    
    # Apply pagination
    skip = (page - 1) * per_page
    products = query.offset(skip).limit(per_page).all()
    
    # Calculate total pages
    total_pages = ceil(total_count / per_page)
    
    return {
        "products": products,
        "total_count": total_count,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages
    }

@megacart_products.get("/{product_id}", response_model=ProductResponse)
async def get_megacart_product(product_id: int, db: Session = Depends(get_db)):
    """Get single MegaCart product by ID"""
    product = db.query(MegacartProduct).filter(
        MegacartProduct.id == product_id,
        MegacartProduct.is_active == True
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found in MegaCart")
    
    return product

@megacart_products.get("/slug/{product_slug}", response_model=ProductResponse)
async def get_megacart_product_by_slug(product_slug: str, db: Session = Depends(get_db)):
    """Get MegaCart product by slug (URL friendly)"""
    product = db.query(MegacartProduct).filter(
        MegacartProduct.slug == product_slug,
        MegacartProduct.is_active == True
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found in MegaCart")
    
    return product

@megacart_products.post("/", response_model=ProductResponse)
async def create_megacart_product(
    product_data: ProductCreate, 
    db: Session = Depends(get_db)
):
    """Create new MegaCart product"""
    
    # Check if category exists
    category = db.query(MegacartCategory).filter(MegacartCategory.id == product_data.category_id).first()
    if not category:
        raise HTTPException(status_code=400, detail="Category not found in MegaCart")
    
    # Create slug and SKU
    slug = create_slug(product_data.name)
    
    # Ensure unique slug
    existing_slug = db.query(MegacartProduct).filter(MegacartProduct.slug == slug).first()
    if existing_slug:
        slug += f"-{existing_slug.id + 1}"
    
    # Generate SKU (simple format: CAT-001, CAT-002, etc.)
    category_products_count = db.query(MegacartProduct).filter(MegacartProduct.category_id == product_data.category_id).count()
    sku = f"{category.name[:3].upper()}-{category_products_count + 1:03d}"
    
    # Create product
    new_product = MegacartProduct(
        **product_data.dict(),
        slug=slug,
        sku=sku
    )
    
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    return new_product

@megacart_products.put("/{product_id}", response_model=ProductResponse)
async def update_megacart_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db)
):
    """Update MegaCart product"""
    product = db.query(MegacartProduct).filter(MegacartProduct.id == product_id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found in MegaCart")
    
    # Update only provided fields
    update_data = product_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    
    # Update slug if name changed
    if "name" in update_data:
        product.slug = create_slug(product.name)
    
    db.commit()
    db.refresh(product)
    
    return product

@megacart_products.get("/featured/list", response_model=List[ProductResponse])
async def get_megacart_featured_products(db: Session = Depends(get_db)):
    """Get featured MegaCart products for homepage"""
    products = db.query(MegacartProduct).filter(
        MegacartProduct.is_active == True,
        MegacartProduct.is_featured == True
    ).limit(8).all()  # Show 8 featured products
    
    return products