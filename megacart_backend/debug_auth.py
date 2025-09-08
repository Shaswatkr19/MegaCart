# debug_auth.py - MongoDB Connection and Authentication Debug Script

import asyncio
import sys
import os
from datetime import datetime
import hashlib

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, current_dir)
sys.path.insert(0, parent_dir)

print(f"🔍 Current directory: {current_dir}")
print(f"🔍 Parent directory: {parent_dir}")
print(f"🔍 Python path: {sys.path[:3]}")

# Try different import methods
try:
    from database.mongodb import connect_to_mongo, close_mongo_connection, get_database
    print("✅ Imported from database.mongodb")
except ImportError:
    try:
        from megacart_backend.database.mongodb import connect_to_mongo, close_mongo_connection, get_database
        print("✅ Imported from megacart_backend.database.mongodb")
    except ImportError:
        # If MongoDB modules not found, create a simple test
        print("⚠️  MongoDB modules not found. Creating simple database test...")
        
        async def connect_to_mongo():
            print("Mock: Connecting to MongoDB...")
            
        async def close_mongo_connection():
            print("Mock: Closing MongoDB connection...")
            
        def get_database():
            print("Mock: Getting database...")
            return None

def hash_password(password: str) -> str:
    """Simple password hashing"""
    return hashlib.sha256(password.encode()).hexdigest()

async def debug_mongodb():
    """Debug MongoDB connection and authentication"""
    
    print("🔍 Starting MongoDB Authentication Debug...")
    print("=" * 50)
    
    try:
        # 1. Test MongoDB Connection
        print("1️⃣ Testing MongoDB Connection...")
        await connect_to_mongo()
        db = get_database()
        
        # Ping database
        result = await db.command("ping")
        print(f"✅ MongoDB Connection: SUCCESS")
        print(f"   Ping result: {result}")
        
        # 2. List Collections
        print("\n2️⃣ Checking Collections...")
        collections = await db.list_collection_names()
        print(f"✅ Available Collections: {collections}")
        
        # 3. Check Users Collection
        print("\n3️⃣ Checking Users Collection...")
        user_count = await db.users.count_documents({})
        print(f"✅ Total Users in Database: {user_count}")
        
        # List all users (without passwords)
        if user_count > 0:
            users = await db.users.find({}, {"password": 0}).to_list(10)
            print("👥 Existing Users:")
            for i, user in enumerate(users, 1):
                print(f"   {i}. ID: {user['_id']}")
                print(f"      Name: {user['name']}")
                print(f"      Email: {user['email']}")
                print(f"      Created: {user.get('created_at', 'N/A')}")
        
        # 4. Test User Creation
        print("\n4️⃣ Testing User Creation...")
        test_email = f"test_user_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com"
        
        test_user = {
            "name": "Test User",
            "email": test_email,
            "password": hash_password("testpassword123"),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Check if test user already exists
        existing = await db.users.find_one({"email": test_email})
        if existing:
            print(f"⚠️  Test user already exists: {test_email}")
        else:
            # Insert test user
            result = await db.users.insert_one(test_user)
            if result.inserted_id:
                print(f"✅ Test User Created Successfully!")
                print(f"   ID: {result.inserted_id}")
                print(f"   Email: {test_email}")
                
                # Verify insertion
                created_user = await db.users.find_one({"_id": result.inserted_id})
                if created_user:
                    print(f"✅ User Verification: SUCCESS")
                else:
                    print(f"❌ User Verification: FAILED")
            else:
                print(f"❌ Failed to create test user")
        
        # 5. Test User Authentication
        print("\n5️⃣ Testing User Authentication...")
        auth_user = await db.users.find_one({"email": test_email})
        if auth_user:
            # Test password verification
            stored_hash = auth_user["password"]
            test_password = "testpassword123"
            computed_hash = hash_password(test_password)
            
            if stored_hash == computed_hash:
                print("✅ Password Authentication: SUCCESS")
            else:
                print("❌ Password Authentication: FAILED")
                print(f"   Stored hash: {stored_hash[:20]}...")
                print(f"   Computed hash: {computed_hash[:20]}...")
        
        # 6. Database Indexes (Optional)
        print("\n6️⃣ Checking Database Indexes...")
        try:
            indexes = await db.users.index_information()
            print(f"✅ User Collection Indexes: {list(indexes.keys())}")
        except Exception as e:
            print(f"⚠️  Could not fetch indexes: {e}")
        
        print("\n🎉 MongoDB Debug Complete!")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        await close_mongo_connection()
        print("🔌 Database connection closed.")

async def cleanup_test_users():
    """Clean up test users created during debugging"""
    print("🧹 Cleaning up test users...")
    
    try:
        await connect_to_mongo()
        db = get_database()
        
        # Delete test users
        result = await db.users.delete_many({
            "email": {"$regex": "^test_user_.*@example\\.com$"}
        })
        
        print(f"✅ Cleaned up {result.deleted_count} test users")
        
    except Exception as e:
        print(f"❌ Cleanup error: {e}")
    finally:
        await close_mongo_connection()

def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == "cleanup":
        asyncio.run(cleanup_test_users())
    else:
        asyncio.run(debug_mongodb())

if __name__ == "__main__":
    main()

# Usage:
# python debug_auth.py          # Run debug tests
# python debug_auth.py cleanup  # Clean up test users