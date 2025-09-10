# mongodb.py - Debug version with multiple connection attempts

import motor.motor_asyncio
import os
import pymongo
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import asyncio
import logging
from datetime import datetime
from urllib.parse import quote_plus

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB client instance
client = None
database = None

# Connection settings
MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME", "megacart")

def debug_connection_string():
    """Debug and validate connection string"""
    if not MONGODB_URL:
        print("❌ MONGODB_URL not set in environment variables")
        return False
    
    print(f"🔍 Connection string analysis:")
    print(f"   Length: {len(MONGODB_URL)}")
    print(f"   Starts with: {MONGODB_URL[:20]}...")
    print(f"   Contains +srv: {'mongodb+srv://' in MONGODB_URL}")
    print(f"   Contains cluster name: {'cluster' in MONGODB_URL.lower()}")
    
    # Check for common issues
    issues = []
    if ' ' in MONGODB_URL:
        issues.append("Contains spaces")
    if not MONGODB_URL.startswith(('mongodb://', 'mongodb+srv://')):
        issues.append("Invalid protocol")
    if '@' not in MONGODB_URL:
        issues.append("Missing credentials section")
    
    if issues:
        print(f"⚠️ Potential issues found: {', '.join(issues)}")
        return False
    
    print("✅ Connection string format looks valid")
    return True

async def test_direct_connection():
    """Test direct MongoDB connection without Motor"""
    try:
        print("🧪 Testing direct PyMongo connection...")
        
        # Create direct client for testing
        direct_client = pymongo.MongoClient(
            MONGODB_URL,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000
        )
        
        # Test connection
        direct_client.admin.command('ping')
        print("✅ Direct PyMongo connection successful")
        
        # List databases
        db_names = direct_client.list_database_names()
        print(f"📄 Available databases: {db_names}")
        
        direct_client.close()
        return True
        
    except Exception as e:
        print(f"❌ Direct connection failed: {e}")
        return False

async def connect_with_different_formats():
    """Try different connection string formats"""
    global client, database
    
    if not MONGODB_URL:
        return False
    
    # Extract components from original URL
    base_url = MONGODB_URL
    
    # Different connection formats to try
    formats = []
    
    # Original format
    formats.append({
        "name": "Original URL",
        "url": base_url
    })
    
    # With specific options
    if '?' not in base_url:
        formats.append({
            "name": "With SSL options",
            "url": base_url + "?ssl=true&ssl_cert_reqs=CERT_NONE"
        })
        formats.append({
            "name": "With retry options", 
            "url": base_url + "?retryWrites=true&w=majority"
        })
        formats.append({
            "name": "Without SSL",
            "url": base_url + "?ssl=false"
        })
    
    for attempt_num, format_config in enumerate(formats, 1):
        try:
            print(f"🔄 Attempt {attempt_num}: {format_config['name']}")
            
            client = motor.motor_asyncio.AsyncIOMotorClient(
                format_config['url'],
                serverSelectionTimeoutMS=8000,
                connectTimeoutMS=8000,
                socketTimeoutMS=8000,
                maxPoolSize=5,
                retryWrites=True
            )
            
            # Test connection
            await asyncio.wait_for(client.admin.command('ping'), timeout=8.0)
            
            database = client[DATABASE_NAME]
            print(f"✅ Connected with {format_config['name']}")
            
            return True
            
        except Exception as e:
            print(f"❌ {format_config['name']} failed: {str(e)[:80]}...")
            if client:
                client.close()
                client = None
            continue
    
    return False

async def connect_to_mongo():
    """Main connection function with comprehensive debugging"""
    global client, database
    
    print("🚀 Starting MongoDB connection process...")
    
    # Step 1: Debug connection string
    if not debug_connection_string():
        print("❌ Connection string validation failed")
        return False
    
    # Step 2: Test direct connection first
    direct_test = await test_direct_connection()
    if not direct_test:
        print("❌ Direct connection test failed - cluster may be down")
        return False
    
    # Step 3: Try Motor connections with different formats
    motor_success = await connect_with_different_formats()
    if motor_success:
        print("✅ Motor connection established")
        return True
    
    print("❌ All connection attempts failed")
    return False

async def close_mongo_connection():
    """Close database connection"""
    global client, database
    if client:
        try:
            client.close()
            client = None
            database = None
            print("✅ MongoDB connection closed")
        except Exception as e:
            print(f"❌ Error closing connection: {e}")

def get_database():
    """Get database instance"""
    global database
    if database is None:
        raise ConnectionError("Database not connected")
    return database

async def health_check():
    """Check connection health"""
    try:
        if client and database:
            await asyncio.wait_for(client.admin.command('ping'), timeout=5.0)
            return {"status": "connected", "connected": True}
        return {"status": "disconnected", "connected": False}
    except Exception as e:
        return {"status": "error", "connected": False, "error": str(e)}

# Retry mechanism
async def execute_with_retry(operation, max_retries=3, delay=1):
    """Execute with retry"""
    for attempt in range(max_retries):
        try:
            return await operation()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            else:
                await asyncio.sleep(delay)
                delay *= 2
    return None

def is_connected():
    """Check if connected"""
    return client is not None and database is not None

# Environment check
def check_environment():
    """Check environment setup"""
    print("🔍 Environment Check:")
    print(f"   MONGODB_URL set: {bool(MONGODB_URL)}")
    print(f"   DATABASE_NAME: {DATABASE_NAME}")
    
    if MONGODB_URL:
        # Hide password but show structure
        if '@' in MONGODB_URL:
            parts = MONGODB_URL.split('@')
            if len(parts) > 1:
                hidden_url = parts[0].split('//')[0] + '//***:***@' + '@'.join(parts[1:])
                print(f"   URL structure: {hidden_url}")
    
    return bool(MONGODB_URL)