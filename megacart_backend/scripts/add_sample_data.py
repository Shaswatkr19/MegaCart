import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def add_sample_data():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.megacart
    
    # Sample products data
    sample_products = [
        {
            "name": "iPhone 15 Pro MAX",
            "description": "Latest iPhone with advanced features",
            "price": 99999,
            "category": "Electronics",
            "image": "https://images.unsplash.com/photo-1697284959152-32ef13855932?w=800",
            "rating": 4.8,
            "reviews": 1250,
            "inStock": True,
            "inventory": 50
        },
        {
            "name": "Nike Air Max",
            "description": "Comfortable running shoes",
            "price": 8999,
            "category": "Clothing",
            "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400",
            "rating": 4.4,
            "reviews": 567,
            "inStock": True,
            "inventory": 100
        }
    ]
    
    # Insert sample data
    result = await db.products.insert_many(sample_products)
    print(f"Inserted {len(result.inserted_ids)} products")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(add_sample_data())