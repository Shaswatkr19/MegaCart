import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def add_sample_data():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.megacart
    
    # Delete existing products
    await db.products.delete_many({})
    
    # Add your PRODUCTS data to MongoDB
    sample_products = [
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
        }
        # Add more products from your PRODUCTS list
    ]
    
    await db.products.insert_many(sample_products)
    print(f"Added {len(sample_products)} products")
    client.close()

if __name__ == "__main__":
    asyncio.run(add_sample_data())