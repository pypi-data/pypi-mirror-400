"""MCP Tool: retrieve_user_context."""

from typing import Optional

from redis.exceptions import RedisError
from pymongo.errors import PyMongoError
from ..clients.redis_client import get_redis_client
from ..clients.mongo_client import get_mongo_client
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



async def retrieve_user_context(customer_id: str) -> Optional[dict]:
    """
    Retrieve user context from cache or database.

    Implements a cache-aside pattern:
    1. Check Redis cache first.
    2. If cache miss, query MongoDB.
    3. If found in MongoDB, populate Redis cache for future requests.

    Args:
        customer_id: The customer's unique identifier.

    Returns:
        A dictionary containing the user context if found, otherwise None.
    """
    if not customer_id:
        logger.warning("retrieve_user_context called with empty customer_id")
        return None
    logger.warning(f">>>> FROM REDIS: Retrieving context for customer_id: {customer_id}")
    redis_client = await get_redis_client()
    await redis_client.connect()

    # 1. Try to get from Redis cache
    try:
        cached_context = await redis_client.get_context(customer_id)
        if cached_context is not None:
            logger.info(f"Cache hit for customer_id: {customer_id}")
            return cached_context
    except RedisError as e:
        logger.error(f"Redis error during cache lookup for customer_id: {customer_id} >> {str(e)}")
        # If Redis fails, proceed to MongoDB but don't block the user
    except Exception as e:
        logger.error(f"Unexpected error during cache lookup for customer_id: {customer_id}")

    logger.info(f"Cache miss for customer_id: {customer_id}. Querying database.")
    mongo_client = await get_mongo_client()
    await mongo_client.connect()
    # 2. If cache miss, get from MongoDB
    try:
        db_context = await mongo_client.get_context(customer_id)
        if db_context is None:
            logger.warning(f"No context found in database for customer_id: {customer_id}")
            return None

        logger.info(f"Database hit for customer_id: {customer_id}")

        # 3. Populate Redis cache for next time
        try:
            
            await redis_client.set_context(customer_id, db_context)
            logger.info(f"Populated cache for customer_id: {customer_id}")
        except RedisError as e:
            logger.exception(f"Failed to populate cache for customer_id: {customer_id}: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error populating cache for customer_id: {customer_id}: {str(e)}")
        return db_context

    except PyMongoError as e:
        logger.error(f"MongoDB error retrieving context for customer_id: {customer_id}>>{str(e)}")
        return None  # Fail gracefully if database is down
    except Exception as e:
        logger.error(f"Unexpected error retrieving context from database for customer_id: {customer_id} >> {str(e)}")
        return None
    finally:
       await redis_client.disconnect()
       await mongo_client.disconnect()
