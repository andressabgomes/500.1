import os
from motor.motor_asyncio import AsyncIOMotorClient
import ssl

def get_database_client():
    """Get MongoDB client with proper SSL configuration"""
    mongo_url = os.environ.get('MONGO_URL', os.environ.get('DATABASE_URL', 'mongodb://localhost:27017'))
    
    # SSL configuration for MongoDB Atlas
    if 'mongodb+srv' in mongo_url or 'mongodb.net' in mongo_url:
        # Production MongoDB Atlas with SSL
        return AsyncIOMotorClient(
            mongo_url,
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=10000,
            socketTimeoutMS=10000,
            tls=True,
            tlsAllowInvalidCertificates=False
        )
    else:
        # Local MongoDB without SSL
        return AsyncIOMotorClient(mongo_url)

def get_database():
    """Get database instance"""
    client = get_database_client()
    db_name = os.environ.get('DB_NAME', os.environ.get('DATABASE_NAME', 'starprint_crm'))
    return client[db_name]

# Global instances
client = get_database_client()
db = get_database()