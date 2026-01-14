"""Unit tests for the Redis client."""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from redis.exceptions import RedisError, ConnectionError as RedisConnectionError

from geaicontext.clients.redis_client import RedisClient




@pytest.fixture
def sample_context():
    """Sample context data for testing."""
    return {
        "customer_id": "test_customer_123",
        "customer_name": {
            "first_name": "John",
            "last_name": "Doe"
        },
        "user_preferences": {
            "theme": "dark"
        }
    }


@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    mock = AsyncMock()
    mock.ping = AsyncMock(return_value=True)
    mock.get = AsyncMock(return_value=None)
    mock.set = AsyncMock(return_value=True)
    mock.setex = AsyncMock(return_value=True)
    mock.delete = AsyncMock(return_value=1)
    mock.aclose = AsyncMock()
    return mock


@pytest.fixture
async def redis_client(mock_redis):
    """Create a Redis client with mocked connection."""
    client = RedisClient()
    
    with patch('geaicontext.clients.redis_client.Redis.from_url', return_value=mock_redis):
        await client.connect()
    
    yield client
    
    await client.disconnect()


class TestRedisClientInitialization:
    """Test Redis client initialization and connection."""

    @pytest.mark.asyncio
    async def test_client_initialization(self):
        """Test that client initializes without connection."""
        client = RedisClient()
        assert client._client is None
        assert client._connected is False

    @pytest.mark.asyncio
    async def test_successful_connection(self, mock_redis):
        """Test successful connection to Redis."""
        client = RedisClient()
        
        with patch('geaicontext.clients.redis_client.Redis.from_url', return_value=mock_redis):
            await client.connect()
        
        assert client._client is not None
        assert client._connected is True
        mock_redis.ping.assert_called_once()

    @pytest.mark.asyncio
    async def test_connection_failure(self):
        """Test connection failure handling."""
        client = RedisClient()
        
        mock_redis = AsyncMock()
        mock_redis.ping = AsyncMock(side_effect=RedisConnectionError("Connection failed"))
        
        with patch('geaicontext.clients.redis_client.Redis.from_url', return_value=mock_redis):
            with pytest.raises(RedisConnectionError):
                await client.connect()

    @pytest.mark.asyncio
    async def test_disconnect(self, redis_client):
        """Test disconnection from Redis."""
        await redis_client.disconnect()
        assert redis_client._connected is False

    @pytest.mark.asyncio
    async def test_health_check_connected(self, redis_client):
        """Test health check when connected."""
        result = await redis_client.health_check()
        assert result is True

    @pytest.mark.asyncio
    async def test_health_check_not_connected(self):
        """Test health check when not connected."""
        client = RedisClient()
        result = await client.health_check()
        assert result is False

    @pytest.mark.asyncio
    async def test_health_check_connection_error(self, redis_client):
        """Test health check when ping fails."""
        redis_client._client.ping = AsyncMock(side_effect=RedisError("Ping failed"))
        result = await redis_client.health_check()
        assert result is False


class TestRedisClientGetContext:
    """Test get_context method."""

    @pytest.mark.asyncio
    async def test_get_context_success(self, redis_client, sample_context):
        """Test successful context retrieval."""
        redis_client._client.get = AsyncMock(return_value=json.dumps(sample_context))
        
        result = await redis_client.get_context("test_customer_123")
        
        assert result == sample_context
        redis_client._client.get.assert_called_once_with("context:test_customer_123")

    @pytest.mark.asyncio
    async def test_get_context_cache_miss(self, redis_client):
        """Test cache miss (key not found)."""
        redis_client._client.get = AsyncMock(return_value=None)
        
        result = await redis_client.get_context("nonexistent_customer")
        
        assert result is None

    @pytest.mark.asyncio
    async def test_get_context_invalid_json(self, redis_client):
        """Test handling of corrupted JSON data."""
        redis_client._client.get = AsyncMock(return_value="invalid json {")
        redis_client._client.delete = AsyncMock(return_value=1)
        
        result = await redis_client.get_context("test_customer_123")
        
        assert result is None
        # Should delete corrupted data
        redis_client._client.delete.assert_called_once_with("context:test_customer_123")

    @pytest.mark.asyncio
    async def test_get_context_not_connected(self):
        """Test get_context when not connected."""
        client = RedisClient()
        
        with pytest.raises(RedisError, match="not connected"):
            await client.get_context("test_customer_123")

    @pytest.mark.asyncio
    async def test_get_context_redis_error(self, redis_client):
        """Test handling of Redis errors during get."""
        redis_client._client.get = AsyncMock(side_effect=RedisError("Redis error"))
        
        with pytest.raises(RedisError):
            await redis_client.get_context("test_customer_123")

    @pytest.mark.asyncio
    async def test_get_key_format(self, redis_client):
        """Test that keys are formatted correctly."""
        key = redis_client._get_key("test_123")
        assert key == "context:test_123"


class TestRedisClientSetContext:
    """Test set_context method."""

    @pytest.mark.asyncio
    async def test_set_context_success(self, redis_client, sample_context):
        """Test successful context storage."""
        redis_client._client.set = AsyncMock(return_value=True)
        
        result = await redis_client.set_context("test_customer_123", sample_context)
        
        assert result is True
        redis_client._client.set.assert_called_once()
        
        # Verify JSON serialization
        call_args = redis_client._client.set.call_args
        assert call_args[0][0] == "context:test_customer_123"
        stored_data = json.loads(call_args[0][1])
        assert stored_data == sample_context

    @pytest.mark.asyncio
    async def test_set_context_with_ttl(self, redis_client, sample_context):
        """Test context storage with TTL."""
        redis_client._client.setex = AsyncMock(return_value=True)
        
        result = await redis_client.set_context("test_customer_123", sample_context, ttl=3600)
        
        assert result is True
        redis_client._client.setex.assert_called_once()
        
        # Verify TTL and data
        call_args = redis_client._client.setex.call_args
        assert call_args[0][0] == "context:test_customer_123"
        assert call_args[0][1] == 3600
        stored_data = json.loads(call_args[0][2])
        assert stored_data == sample_context

    @pytest.mark.asyncio
    async def test_set_context_serialization_error(self, redis_client):
        """Test handling of non-serializable data."""
        # Create non-serializable object
        class NonSerializable:
            pass
        
        invalid_context = {
            "customer_id": "test_123",
            "data": NonSerializable()
        }
        
        result = await redis_client.set_context("test_customer_123", invalid_context)
        
        assert result is False

    @pytest.mark.asyncio
    async def test_set_context_not_connected(self):
        """Test set_context when not connected."""
        client = RedisClient()
        
        with pytest.raises(RedisError, match="not connected"):
            await client.set_context("test_customer_123", {"data": "value"})

    @pytest.mark.asyncio
    async def test_set_context_redis_error(self, redis_client, sample_context):
        """Test handling of Redis errors during set."""
        redis_client._client.set = AsyncMock(side_effect=RedisError("Redis error"))
        
        with pytest.raises(RedisError):
            await redis_client.set_context("test_customer_123", sample_context)

    @pytest.mark.asyncio
    async def test_set_context_unicode(self, redis_client):
        """Test storing context with Unicode characters."""
        unicode_context = {
            "customer_id": "test_123",
            "name": "José García",
            "message": "¡Hola! 你好"
        }
        
        redis_client._client.set = AsyncMock(return_value=True)
        
        result = await redis_client.set_context("test_customer_123", unicode_context)
        
        assert result is True
        
        # Verify Unicode is preserved
        call_args = redis_client._client.set.call_args
        stored_data = json.loads(call_args[0][1])
        assert stored_data["name"] == "José García"
        assert stored_data["message"] == "¡Hola! 你好"


class TestRedisClientDeleteContext:
    """Test delete_context method."""

    @pytest.mark.asyncio
    async def test_delete_context_success(self, redis_client):
        """Test successful context deletion."""
        redis_client._client.delete = AsyncMock(return_value=1)
        
        result = await redis_client.delete_context("test_customer_123")
        
        assert result is True
        redis_client._client.delete.assert_called_once_with("context:test_customer_123")

    @pytest.mark.asyncio
    async def test_delete_context_not_found(self, redis_client):
        """Test deletion when key doesn't exist."""
        redis_client._client.delete = AsyncMock(return_value=0)
        
        result = await redis_client.delete_context("nonexistent_customer")
        
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_context_not_connected(self):
        """Test delete_context when not connected."""
        client = RedisClient()
        
        with pytest.raises(RedisError, match="not connected"):
            await client.delete_context("test_customer_123")

    @pytest.mark.asyncio
    async def test_delete_context_redis_error(self, redis_client):
        """Test handling of Redis errors during delete."""
        redis_client._client.delete = AsyncMock(side_effect=RedisError("Redis error"))
        
        with pytest.raises(RedisError):
            await redis_client.delete_context("test_customer_123")


class TestGlobalRedisClient:
    """Test global client instance."""

    @pytest.mark.asyncio
    async def test_get_redis_client_singleton(self):
        """Test that get_redis_client returns singleton instance."""
        client1 = await get_redis_client()
        client2 = await get_redis_client()
        assert client1 is client2

    @pytest.mark.asyncio
    async def test_get_redis_client_not_connected(self):
        """Test that get_redis_client returns unconnected client."""
        client = await get_redis_client()
        # Client should exist but not be connected yet
        assert client is not None


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.mark.asyncio
    async def test_empty_customer_id(self, redis_client):
        """Test operations with empty customer_id."""
        key = redis_client._get_key("")
        assert key == "context:"

    @pytest.mark.asyncio
    async def test_special_characters_in_customer_id(self, redis_client):
        """Test customer_id with special characters."""
        special_id = "customer:123:test@example.com"
        key = redis_client._get_key(special_id)
        assert key == f"context:{special_id}"

    @pytest.mark.asyncio
    async def test_large_context_data(self, redis_client):
        """Test storing large context data."""
        large_context = {
            "customer_id": "test_123",
            "data": "x" * 1000000  # 1MB of data
        }
        
        redis_client._client.set = AsyncMock(return_value=True)
        
        result = await redis_client.set_context("test_customer_123", large_context)
        
        assert result is True

    @pytest.mark.asyncio
    async def test_empty_context_data(self, redis_client):
        """Test storing empty context."""
        empty_context = {}
        
        redis_client._client.set = AsyncMock(return_value=True)
        
        result = await redis_client.set_context("test_customer_123", empty_context)
        
        assert result is True

    @pytest.mark.asyncio
    async def test_multiple_operations_sequence(self, redis_client, sample_context):
        """Test sequence of operations."""
        # Set
        redis_client._client.set = AsyncMock(return_value=True)
        set_result = await redis_client.set_context("test_customer_123", sample_context)
        assert set_result is True
        
        # Get
        redis_client._client.get = AsyncMock(return_value=json.dumps(sample_context))
        get_result = await redis_client.get_context("test_customer_123")
        assert get_result == sample_context
        
        # Delete
        redis_client._client.delete = AsyncMock(return_value=1)
        delete_result = await redis_client.delete_context("test_customer_123")
        assert delete_result is True
        
        # Get after delete
        redis_client._client.get = AsyncMock(return_value=None)
        get_after_delete = await redis_client.get_context("test_customer_123")
        assert get_after_delete is None