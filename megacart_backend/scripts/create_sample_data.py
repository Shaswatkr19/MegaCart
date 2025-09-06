# scripts/create_sample_data.py - MegaCart Sample Data
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models.user import Base
from models.product import MegacartCategory, MegacartProduct

# Create tables
Base.metadata.create_all(bind=engine)

def create_sample_megacart_data():
    db = SessionLocal()
    
    try:
        # Create categories
        categories = [
            {"name": "Electronics", "description": "Gadgets and electronic items"},
            {"name": "Fashion", "description": "Clothing and accessories"},
            {"name": "Books", "description": "Books and educational material"},
            {"name": "Home & Garden", "description": "Home decor and garden items"},
            {"name": "Sports", "description": "Sports and fitness equipment"}
        ]
        
        for cat_data in categories:
            existing = db.query(MegacartCategory).filter(MegacartCategory.name == cat_data["name"]).first()
            if not existing:
                category = MegacartCategory(**cat_data)
                db.add(category)
        
        db.commit()
        
        # Create sample products
        products = [
            {
                "name": "iPhone 15 Pro",
                "description": "Latest Apple smartphone with advanced features",
                "price": 89999.0,
                "original_price": 99999.0,
                "stock_quantity": 50,
                "category_id": 1,  # Electronics
                "is_featured": True,
                "tags": "apple,iphone,smartphone,mobile"
            },
            {
                "name": "Samsung Smart TV 55 inch",
                "description": "4K Ultra HD Smart LED TV",
                "price": 45999.0,
                "stock_quantity": 25,
                "category_id": 1,
                "tags": "samsung,tv,smart tv,4k"
            },
            {
                "name": "Nike Air Max Shoes",
                "description": "Comfortable running shoes",
                "price": 8999.0,
                "stock_quantity": 100,
                "category_id": 2,  # Fashion
                "is_featured": True,
                "tags": "nike,shoes,running,sports"
            }
        ]
        
        for prod_data in products:
            # Create slug and SKU
            slug = prod_data["name"].lower().replace(" ", "-")
            sku = f"MEGA-{prod_data['category_id']:02d}-{len(products):03d}"
            
            product = MegacartProduct(
                **prod_data,
                slug=slug,
                sku=sku
            )
            db.add(product)
        
        db.commit()
        print("✅ MegaCart sample data created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_megacart_data()