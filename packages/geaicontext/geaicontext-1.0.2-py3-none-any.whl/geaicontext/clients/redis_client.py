"""Redis client wrapper with async support."""

import json
import os
from typing import Optional

from redis.asyncio import Redis
from redis.exceptions import RedisError, ConnectionError as RedisConnectionError

import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
import json
from datetime import datetime
from bson import ObjectId

class MongoJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)
    
class RedisClient:
    """Async Redis client for caching user contexts."""

    def __init__(self):
        """Initialize Redis client (connection established on connect())."""
        self._client: Optional[Redis] = None
        self._connected = False

    async def connect(self) -> None:
        """
        Establish connection to Redis.

        Raises:
            RedisConnectionError: If connection fails
        """
        try:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            self._client = Redis.from_url(
                redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
            
            # Test connection
            await self._client.ping()
            self._connected = True
            
            logger.info(f"Connected to Redis at {redis_url}")
            
        except RedisConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error connecting to Redis: {e}")
            raise

    async def disconnect(self) -> None:
        """Close Redis connection."""
        if self._client:
            await self._client.aclose()
            self._connected = False
            logger.info("Disconnected from Redis")

    async def health_check(self) -> bool:
        """
        Check if Redis connection is healthy.

        Returns:
            True if connected and responsive, False otherwise
        """
        if not self._client or not self._connected:
            return False
        
        try:
            await self._client.ping()
            return True
        except RedisError:
            return False

    def _get_key(self, customer_id: str) -> str:
        """
        Generate Redis key for a customer.

        Args:
            customer_id: Customer identifier

        Returns:
            Redis key string
        """
        return f"context:{customer_id}"

    async def get_context(self, customer_id: str) -> Optional[dict]:
        """
        Retrieve user context from Redis cache.

        Args:
            customer_id: Customer identifier

        Returns:
            Context dictionary if found, None if not found

        Raises:
            RedisError: If Redis operation fails
        """
        if not self._client:
            raise RedisError("Redis client not connected. Call connect() first.")

        key = self._get_key(customer_id)
        
        try:
            data = await self._client.get(key)
            
            if data is None:
                logger.debug(f"Cache miss for customer_id: {customer_id}")
                return None
            
            context = json.loads(data)
            logger.info(
                f"Cache hit for customer_id: {customer_id}",
                extra={"key": key}
            )
            return context
            
        except json.JSONDecodeError as e:
            logger.error(
                f"Invalid JSON in cache for customer_id: {customer_id}",
                extra={"error": str(e)}
            )
            # Delete corrupted data
            await self._client.delete(key)
            return None
            
        except RedisError as e:
            logger.error(
                f"Redis error retrieving context for customer_id: {customer_id}",
                extra={"error": str(e)}
            )
            raise

    async def set_context(self, customer_id: str, context: dict, ttl: Optional[int] = None) -> bool:
        """
        Store user context in Redis cache.

        Args:
            customer_id: Customer identifier
            context: Context data to store
            ttl: Optional time-to-live in seconds

        Returns:
            True if successful, False otherwise

        Raises:
            RedisError: If Redis operation fails
        """
        if not self._client:
            raise RedisError("Redis client not connected. Call connect() first.")
        key = self._get_key(customer_id)
        
        try:
            # Serialize to JSON
            data = json.dumps(context, ensure_ascii=False,cls=MongoJSONEncoder)
            
            # Store in Redis
            if ttl:
                await self._client.setex(key, ttl, data)
            else:
                await self._client.set(key, data)
            
            logger.info(
                f"Cached context for customer_id: {customer_id}",
                extra={"key": key, "ttl": ttl, "size_bytes": len(data)}
            )
            return True
            
        except (json.JSONEncodeError, TypeError) as e:
            logger.error(
                f"Failed to serialize context for customer_id: {customer_id}",
                extra={"error": str(e)}
            )
            return False
            
        except RedisError as e:
            logger.error(
                f"Redis error storing context for customer_id: {customer_id}",
                extra={"error": str(e)}
            )
            raise

    async def delete_context(self, customer_id: str) -> bool:
        """
        Delete user context from Redis cache.

        Args:
            customer_id: Customer identifier

        Returns:
            True if deleted, False if not found

        Raises:
            RedisError: If Redis operation fails
        """
        if not self._client:
            raise RedisError("Redis client not connected. Call connect() first.")

        key = self._get_key(customer_id)
        
        try:
            result = await self._client.delete(key)
            
            if result > 0:
                logger.info(f"Deleted context for customer_id: {customer_id}")
                return True
            else:
                logger.debug(f"No context to delete for customer_id: {customer_id}")
                return False
                
        except RedisError as e:
            logger.error(
                f"Redis error deleting context for customer_id: {customer_id}",
                extra={"error": str(e)}
            )
            raise


# Global client instance
_redis_client: Optional[RedisClient] = None


async def get_redis_client() -> RedisClient:
    """
    Get or create the global Redis client instance.

    Returns:
        RedisClient instance

    Note:
        You must call connect() on the client before using it.
    """
    global _redis_client
    if _redis_client is None:
        _redis_client = RedisClient()
    return _redis_client