"""MongoDB client wrapper with async support."""

import os
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo.errors import PyMongoError, ConnectionFailure, DuplicateKeyError

import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MongoClient:
    """Async MongoDB client for persistent user context storage."""

    def __init__(self):
        """Initialize MongoDB client (connection established on connect())."""
        self._client: Optional[AsyncIOMotorClient] = None
        self._db: Optional[AsyncIOMotorDatabase] = None
        self._collection: Optional[AsyncIOMotorCollection] = None
        self._connected = False

    async def connect(self) -> None:
        """
        Establish connection to MongoDB and create indexes.

        Raises:
            ConnectionFailure: If connection fails
        """
        try:
            mongodb_url = os.getenv("MONGODB_URL", "mongodb://gfiallos:Passw0rd@localhost:27017")
            self._client = AsyncIOMotorClient(
                mongodb_url,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
            )
            
            # Test connection
            await self._client.admin.command('ping')
            
            # Get database and collection
            mongodb_database = os.getenv("MONGODB_DATABASE", "ctx")
            mongodb_collection = os.getenv("MONGODB_COLLECTION", "gal")
            self._db = self._client[mongodb_database]
            self._collection = self._db[mongodb_collection]
            
            # Create unique index on customer_id
            await self._collection.create_index("customer_id", unique=True)
            
            self._connected = True
            
            logger.info(f"Connected to MongoDB database: {mongodb_database}, collection: {mongodb_collection}>>{self._collection}")
            
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error connecting to MongoDB: {e}")
            raise

    async def disconnect(self) -> None:
        """Close MongoDB connection."""
        if self._client:
            self._client.close()
            self._connected = False
            logger.info("Disconnected from MongoDB")

    async def health_check(self) -> bool:
        """
        Check if MongoDB connection is healthy.

        Returns:
            True if connected and responsive, False otherwise
        """
        if not self._client or not self._connected:
            return False
        
        try:
            await self._client.admin.command('ping')
            return True
        except PyMongoError:
            return False

    async def get_context(self, customer_id: str) -> Optional[dict]:
        """
        Retrieve user context from MongoDB.

        Args:
            customer_id: Customer identifier

        Returns:
            Context dictionary if found, None if not found

        Raises:
            PyMongoError: If MongoDB operation fails
        """
        

        try:
            logger.info(f"Retrieving context from MongoDB for customer_id: {customer_id}>>> {self._collection}>>>>>>>")
            document = await self._collection.find_one({"customer_id": customer_id})
            
            if document is None:
                logger.debug(f"No context found in MongoDB for customer_id: {customer_id}")
                return None
            
            # Remove MongoDB's _id field before returning
            if "_id" in document:
                del document["_id"]
            
            logger.info(
                f"Retrieved context from MongoDB for customer_id: {customer_id}",
                extra={"fields": list(document.keys())}
            )
            return document
            
        except PyMongoError as e:
            logger.error(
                f"MongoDB error retrieving context for customer_id: {customer_id}",
                extra={"error": str(e)}
            )
            raise

    async def save_context(self, customer_id: str, context: dict) -> bool:
        """
        Save user context to MongoDB (upsert operation).

        Args:
            customer_id: Customer identifier
            context: Context data to store

        Returns:
            True if successful, False otherwise

        Raises:
            PyMongoError: If MongoDB operation fails
        """
        logger.info(f"Saving context to MongoDB for customer_id: {customer_id} >>> {context} <<<<<<{self._collection}>>>>>>>")
        
        try:
            # Ensure customer_id is in the document
            context_copy = context.copy()
            context_copy["customer_id"] = customer_id
            logger.info(f"Context copy to save: {context_copy} preparing to upsert.")
            # Upsert: update if exists, insert if not
            result = await self._collection.replace_one({"customer_id": customer_id},context_copy,upsert=True)
            
            if result.upserted_id:
                logger.info(f"Inserted new context in MongoDB for customer_id: {customer_id} upserted_id: {str(result.upserted_id)}")
            else:
                logger.info(f"Updated existing context in MongoDB for customer_id: {customer_id} matched_count: {result.matched_count}")
            return True
            
        except DuplicateKeyError as e:
            logger.error(f"Duplicate key error saving context for customer_id: {customer_id} >> {str(e)}")
            return False
            
        except Exception as e:
            logger.error(f"MongoDB error saving CONTEXT for customer_id: {customer_id} >> {str(e)}")
            raise

    async def delete_context(self, customer_id: str) -> bool:
        """
        Delete user context from MongoDB.

        Args:
            customer_id: Customer identifier

        Returns:
            True if deleted, False if not found

        Raises:
            PyMongoError: If MongoDB operation fails
        """
        if not self._collection:
            raise PyMongoError("MongoDB client not connected. Call connect() first.")

        try:
            result = await self._collection.delete_one({"customer_id": customer_id})
            
            if result.deleted_count > 0:
                logger.info(f"Deleted context from MongoDB for customer_id: {customer_id}")
                return True
            else:
                logger.debug(f"No context to delete in MongoDB for customer_id: {customer_id}")
                return False
                
        except PyMongoError as e:
            logger.error(
                f"MongoDB error deleting context for customer_id: {customer_id}",
                extra={"error": str(e)}
            )
            raise

    async def count_contexts(self) -> int:
        """
        Count total number of contexts in MongoDB.

        Returns:
            Number of context documents

        Raises:
            PyMongoError: If MongoDB operation fails
        """
        if not self._collection:
            raise PyMongoError("MongoDB client not connected. Call connect() first.")

        try:
            count = await self._collection.count_documents({})
            logger.debug(f"Total contexts in MongoDB: {count}")
            return count
            
        except PyMongoError as e:
            logger.error(f"MongoDB error counting contexts: {e}")
            raise


# Global client instance
_mongo_client: Optional[MongoClient] = None


async def get_mongo_client() -> MongoClient:
    """
    Get or create the global MongoDB client instance.

    Returns:
        MongoClient instance

    Note:
        You must call connect() on the client before using it.
    """
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = MongoClient()
    return _mongo_client