# megacart_backend/database/mongodb.py - FIXED MongoDB Configuration

import motor.motor_asyncio
import os
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import asyncio
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB client instance
client = None
database = None

# Connection settings - MOVED TO ENVIRONMENT VARIABLES FOR SECURITY
MONGODB_URL = os.getenv("MONGODB_URL")  # Remove hardcoded credentials
DATABASE_NAME = os.getenv("DATABASE_NAME", "megacart")

# Fallback for local development (if no env var set)
if not MONGODB_URL:
    MONGODB_URL = "mongodb://localhost:27017/megacart"
    logger.warning("⚠️ Using local MongoDB fallback. Set MONGODB_URL environment variable for production.")

async def connect_to_mongo():
    """Create database connection with improved error handling"""
    global client, database
    
    try:
        print("🔄 Attempting MongoDB connection...")
        logger.info(f"Connecting to: {MONGODB_URL[:30]}...")
        
        # FIXED: More reasonable timeout values and SSL settings
        client = motor.motor_asyncio.AsyncIOMotorClient(
            MONGODB_URL,
            serverSelectionTimeoutMS=15000,    # Increased to 15 seconds
            connectTimeoutMS=15000,            # Increased timeout
            socketTimeoutMS=15000,             # Increased timeout
            maxPoolSize=10,
            retryWrites=True,
            w="majority",
            # FIXED SSL settings for MongoDB Atlas
            tls=True,
            tlsAllowInvalidCertificates=False,  # Set to False for better security
            # Removed conflicting SSL options
        )
        
        # Test the connection with longer timeout
        await asyncio.wait_for(client.admin.command('ping'), timeout=15.0)
        
        database = client[DATABASE_NAME]
        
        print("✅ MongoDB connected successfully")
        logger.info("MongoDB connection established")
        
        # Test database access
        try:
            collections = await database.list_collection_names()
            print(f"📄 Available collections: {collections}")
        except Exception as e:
            logger.warning(f"Could not list collections: {e}")
        
        return True
        
    except asyncio.TimeoutError:
        print("❌ MongoDB connection timeout - Check your internet connection")
        logger.error("MongoDB connection timeout")
        return False
    except ConnectionFailure as e:
        print(f"❌ MongoDB connection failed: {e}")
        logger.error(f"Connection failure: {e}")
        return False
    except ServerSelectionTimeoutError as e:
        print(f"❌ MongoDB server selection timeout: {e}")
        logger.error(f"Server selection timeout: {e}")
        return False
    except Exception as e:
        print(f"❌ MongoDB connection error: {e}")
        logger.error(f"Unexpected error: {e}")
        return False

async def close_mongo_connection():
    """Close database connection"""
    global client
    if client:
        try:
            client.close()
            print("✅ Disconnected from MongoDB")
        except Exception as e:
            print(f"❌ Error disconnecting from MongoDB: {e}")

def get_database():
    """Get database instance with error handling"""
    global database
    if database is None:
        raise ConnectionError("Database not connected. Please call connect_to_mongo() first.")
    return database

async def test_database_operations():
    """Test basic database operations"""
    try:
        db = get_database()
        
        # Test user collection
        user_count = await db.users.estimated_document_count()
        print(f"👥 Users in database: {user_count}")
        
        # Test products collection
        product_count = await db.products.estimated_document_count()
        print(f"📦 Products in database: {product_count}")
        
        return True
    except Exception as e:
        print(f"❌ Database operation test failed: {e}")
        return False

# Retry mechanism for database operations
async def execute_with_retry(operation, max_retries=3, delay=1):
    """Execute database operation with retry mechanism"""
    for attempt in range(max_retries):
        try:
            return await operation()
        except Exception as e:
            if attempt == max_retries - 1:  # Last attempt
                print(f"❌ Operation failed after {max_retries} attempts: {e}")
                raise e
            else:
                print(f"⚠️ Attempt {attempt + 1} failed, retrying in {delay}s: {e}")
                await asyncio.sleep(delay)
                delay *= 2  # Exponential backoff
    
    return None

# Health check function
async def health_check():
    """Check MongoDB connection health"""
    try:
        if client:
            await client.admin.command('ping')
            return True
        return False
    except Exception:
        return False