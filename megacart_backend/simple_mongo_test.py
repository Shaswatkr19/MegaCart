# simple_mongo_test.py - Simple MongoDB Connection Test

import asyncio
import os
import sys
from datetime import datetime
import hashlib

# Try to import motor directly for MongoDB testing
try:
    from motor.motor_asyncio import AsyncIOMotorClient
    print("✅ Motor MongoDB driver found")
except ImportError:
    print("❌ Motor not installed. Install with: pip install motor")
    sys.exit(1)

# MongoDB connection details (adjust these based on your setup)
MONGODB_URL = "mongodb://localhost:27017"  # Change if different
DATABASE_NAME = "megacart"  # Change if different

def hash_password(password: str) -> str:
    """Simple password hashing"""
    return hashlib.sha256(password.encode()).hexdigest()

async def test_mongodb_simple():
    """Simple MongoDB connection and authentication test"""
    
    print("🔍 Starting Simple MongoDB Test...")
    print("=" * 50)
    
    client = None
    
    try:
        # 1. Connect to MongoDB
        print("1️⃣ Connecting to MongoDB...")
        print(f"   URL: {MONGODB_URL}")
        print(f"   Database: {DATABASE_NAME}")
        
        client = AsyncIOMotorClient(MONGODB_URL)
        db = client[DATABASE_NAME]
        
        # Test connection with ping
        await client.admin.command('ping')
        print("✅ MongoDB Connection: SUCCESS")
        
        # 2. Check collections
        print("\n2️⃣ Checking Collections...")
        collections = await db.list_collection_names()
        print(f"✅ Available Collections: {collections}")
        
        # 3. Check users collection
        print("\n3️⃣ Checking Users Collection...")
        users_collection = db.users
        user_count = await users_collection.count_documents({})
        print(f"✅ Total Users: {user_count}")
        
        if user_count > 0:
            # Show existing users (without passwords)
            print("\n👥 Existing Users:")
            async for user in users_collection.find({}, {"password": 0}).limit(5):
                print(f"   📧 {user.get('email', 'No email')}")
                print(f"   👤 {user.get('name', 'No name')}")
                print(f"   🆔 {user.get('_id')}")
                print(f"   📅 {user.get('created_at', 'No date')}")
                print("   " + "-" * 30)
        
        # 4. Test user creation
        print("\n4️⃣ Testing User Creation...")
        test_email = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}@test.com"
        
        # Check if test user exists
        existing = await users_collection.find_one({"email": test_email})
        if not existing:
            test_user = {
                "name": "Test User",
                "email": test_email,
                "password": hash_password("testpass123"),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = await users_collection.insert_one(test_user)
            if result.inserted_id:
                print(f"✅ Test User Created:")
                print(f"   ID: {result.inserted_id}")
                print(f"   Email: {test_email}")
                print(f"   Password: testpass123 (hashed)")
            else:
                print("❌ Failed to create test user")
        else:
            print(f"⚠️  Test user already exists: {test_email}")
        
        # 5. Test authentication logic
        print("\n5️⃣ Testing Authentication...")
        auth_test_user = await users_collection.find_one({"email": test_email})
        if auth_test_user:
            stored_hash = auth_test_user["password"]
            test_password = "testpass123"
            computed_hash = hash_password(test_password)
            
            if stored_hash == computed_hash:
                print("✅ Password Verification: SUCCESS")
            else:
                print("❌ Password Verification: FAILED")
                print(f"   Stored: {stored_hash[:20]}...")
                print(f"   Computed: {computed_hash[:20]}...")
        
        # 6. Show connection info
        print("\n6️⃣ Connection Info:")
        server_info = await client.server_info()
        print(f"✅ MongoDB Version: {server_info.get('version', 'Unknown')}")
        
        print("\n🎉 MongoDB Test Complete!")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        
        # Common solutions
        print("\n🔧 Common Solutions:")
        print("1. Make sure MongoDB is running:")
        print("   - For macOS with Homebrew: brew services start mongodb-community")
        print("   - For Linux: sudo systemctl start mongod")
        print("   - For Docker: docker run -d -p 27017:27017 mongo:latest")
        print()
        print("2. Check MongoDB URL:")
        print(f"   Current: {MONGODB_URL}")
        print("   Try: mongodb://127.0.0.1:27017")
        print()
        print("3. Install motor: pip install motor")
        
    finally:
        if client:
            client.close()
            print("🔌 Database connection closed")

async def cleanup_test_users():
    """Clean up test users"""
    print("🧹 Cleaning up test users...")
    
    client = None
    try:
        client = AsyncIOMotorClient(MONGODB_URL)
        db = client[DATABASE_NAME]
        
        result = await db.users.delete_many({
            "email": {"$regex": "^test_.*@test\\.com$"}
        })
        
        print(f"✅ Cleaned up {result.deleted_count} test users")
        
    except Exception as e:
        print(f"❌ Cleanup error: {e}")
    finally:
        if client:
            client.close()

async def show_project_structure():
    """Show current project structure"""
    print("📁 Project Structure:")
    current_dir = os.getcwd()
    print(f"Current directory: {current_dir}")
    
    for root, dirs, files in os.walk(current_dir):
        level = root.replace(current_dir, '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 2 * (level + 1)
        for file in files[:10]:  # Show first 10 files only
            if file.endswith(('.py', '.json', '.md', '.txt')):
                print(f"{subindent}{file}")
        if len(files) > 10:
            print(f"{subindent}... and {len(files) - 10} more files")
        
        # Don't go too deep
        if level > 2:
            dirs.clear()

def main():
    """Main function"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "cleanup":
            asyncio.run(cleanup_test_users())
        elif sys.argv[1] == "structure":
            asyncio.run(show_project_structure())
        else:
            print("Available commands:")
            print("  python simple_mongo_test.py          # Run MongoDB test")
            print("  python simple_mongo_test.py cleanup  # Cleanup test users")
            print("  python simple_mongo_test.py structure # Show project structure")
    else:
        asyncio.run(test_mongodb_simple())

if __name__ == "__main__":
    main()