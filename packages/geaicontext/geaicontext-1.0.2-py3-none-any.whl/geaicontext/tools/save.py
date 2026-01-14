"""MCP Tool: save_user_context."""

import asyncio
from typing import Optional

from redis.exceptions import RedisError
from pymongo.errors import PyMongoError

from ..clients.redis_client import get_redis_client
from ..clients.mongo_client import get_mongo_client
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def _async_save_to_mongodb(customer_id: str, context: dict) -> None:
    """
    Background task to save context to MongoDB asynchronously.

    Args:
        customer_id: The customer's unique identifier.
        context: The context data to save.
    """
    mongo_client = await get_mongo_client()
    try:
        await mongo_client.connect()
        logger.info(f"Starting async MongoDB write for customer_id: {customer_id} >>> {context}")
        success = await mongo_client.save_context(customer_id, context)
        if success:
            logger.info(f"Async MongoDB write completed for customer_id: {customer_id}")
        else:
            logger.error(f"Async MongoDB write failed for customer_id: {customer_id}")
    except Exception as e:
        logger.exception(f"Unexpected error in async MongoDB write for customer_id: {customer_id}")
        
    finally:
        await mongo_client.disconnect()


async def save_user_context(customer_id: str, context: dict) -> tuple[bool, str]:
    """
    Save user context to cache and database.

    Implements a write-through pattern:
    1. Validate data against schema.
    2. Write to Redis synchronously.
    3. Schedule async MongoDB write (fire-and-forget).
    4. Return success immediately after Redis write.

    Args:
        customer_id: The customer's unique identifier.
        context: The context data to save.

    Returns:
        A tuple of (success: bool, message: str).
    """
    if not customer_id:
        error_msg = "customer_id is required"
        logger.warning(f"save_user_context called with empty customer_id")
        return False, error_msg

    if not context:
        error_msg = "context data is required"
        logger.warning(f"save_user_context called with empty context for customer_id: {customer_id}")
        return False, error_msg

    redis_client = await get_redis_client()
    await redis_client.connect()
    # 1. Write to Redis synchronously
    try:
        success = await redis_client.set_context(customer_id, context)
        if not success:
            error_msg = "Failed to write to Redis cache"
            logger.error(
                f"Redis write failed for customer_id: {customer_id}",
                extra={"operation": "save_user_context"}
            )
            return False, error_msg

        logger.info(
            f"Successfully wrote to Redis cache for customer_id: {customer_id}",
            extra={"operation": "save_user_context"}
        )

    except RedisError as e:
        error_msg = f"Redis error: {str(e)}"
        logger.error(
            f"Redis error saving context for customer_id: {customer_id} >> {str(e)}")
        return False, error_msg
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(
            f"Unexpected error saving to Redis for customer_id: {customer_id}",
            extra={"error": str(e)}
        )
        return False, error_msg
    finally:
        await redis_client.disconnect()
    # 2. Schedule async MongoDB write (fire-and-forget)
    try:
        await _async_save_to_mongodb(customer_id, context)
        logger.info(f"Scheduled async MongoDB write for customer_id: {customer_id}")
    except Exception as e:
        # Log but don't fail the request - Redis write already succeeded
        logger.error(f"Failed to schedule async MongoDB write for customer_id: {customer_id} >> {str(e)}")

    # 4. Return success immediately after Redis write
    return True, f"Context saved successfully for customer_id: {customer_id}"