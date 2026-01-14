"""Integration tests for MCP tools."""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch

from geaicontext.tools.retrieve import retrieve_user_context
from geaicontext.tools.save import save_user_context


@pytest.fixture
def sample_context():
    """Sample context data for testing."""
    return {
        "customer_id": "test_customer_123",
        "customer_name": {
            "first_name": "John",
            "last_name": "Doe",
            "preferred_name": "Johnny"
        },
        "user_preferences": {
            "theme": "dark",
            "language": "en-US"
        }
    }


@pytest.fixture
def mock_redis_client():
    """Mock Redis client."""
    mock = AsyncMock()
    mock.get_context = AsyncMock(return_value=None)
    mock.set_context = AsyncMock(return_value=True)
    return mock


@pytest.fixture
def mock_mongo_client():
    """Mock MongoDB client."""
    mock = AsyncMock()
    mock.get_context = AsyncMock(return_value=None)
    mock.save_context = AsyncMock(return_value=True)
    return mock


class TestRetrieveUserContext:
    """Test retrieve_user_context tool."""

    @pytest.mark.asyncio
    async def test_retrieve_cache_hit(self, mock_redis_client, mock_mongo_client, sample_context):
        """Test successful retrieval from Redis cache."""
        mock_redis_client.get_context = AsyncMock(return_value=sample_context)
        
        with patch('geaicontext.tools.retrieve.get_redis_client', return_value=mock_redis_client):
            with patch('geaicontext.tools.retrieve.get_mongo_client', return_value=mock_mongo_client):
                result = await retrieve_user_context("test_customer_123")
        
        assert result == sample_context
        mock_redis_client.get_context.assert_called_once_with("test_customer_123")
        # MongoDB should not be called on cache hit
        mock_mongo_client.get_context.assert_not_called()

    @pytest.mark.asyncio
    async def test_retrieve_cache_miss_db_hit(self, mock_redis_client, mock_mongo_client, sample_context):
        """Test retrieval from MongoDB when cache misses."""
        mock_redis_client.get_context = AsyncMock(return_value=None)
        mock_mongo_client.get_context = AsyncMock(return_value=sample_context)
        mock_redis_client.set_context = AsyncMock(return_value=True)
        
        with patch('geaicontext.tools.retrieve.get_redis_client', return_value=mock_redis_client):
            with patch('geaicontext.tools.retrieve.get_mongo_client', return_value=mock_mongo_client):
                result = await retrieve_user_context("test_customer_123")
        
        assert result == sample_context
        mock_redis_client.get_context.assert_called_once_with("test_customer_123")
        mock_mongo_client.get_context.assert_called_once_with("test_customer_123")
        # Should populate cache
        mock_redis_client.set_context.assert_called_once_with("test_customer_123", sample_context)

    @pytest.mark.asyncio
    async def test_retrieve_complete_miss(self, mock_redis_client, mock_mongo_client):
        """Test retrieval when context doesn't exist anywhere."""
        mock_redis_client.get_context = AsyncMock(return_value=None)
        mock_mongo_client.get_context = AsyncMock(return_value=None)
        
        with patch('geaicontext.tools.retrieve.get_redis_client', return_value=mock_redis_client):
            with patch('geaicontext.tools.retrieve.get_mongo_client', return_value=mock_mongo_client):
                result = await retrieve_user_context("nonexistent_customer")
        
        assert result is None
        mock_redis_client.get_context.assert_called_once()
        mock_mongo_client.get_context.assert_called_once()

    @pytest.mark.asyncio
    async def test_retrieve_empty_customer_id(self, mock_redis_client, mock_mongo_client):
        """Test retrieval with empty customer_id."""
        with patch('geaicontext.tools.retrieve.get_redis_client', return_value=mock_redis_client):
            with patch('geaicontext.tools.retrieve.get_mongo_client', return_value=mock_mongo_client):
                result = await retrieve_user_context("")
        
        assert result is None
        # Should not call any clients
        mock_redis_client.get_context.assert_not_called()
        mock_mongo_client.get_context.assert_not_called()

    @pytest.mark.asyncio
    async def test_retrieve_redis_error_fallback_to_mongo(self, mock_redis_client, mock_mongo_client, sample_context):
        """Test fallback to MongoDB when Redis fails."""
        from redis.exceptions import RedisError
        
        mock_redis_client.get_context = AsyncMock(side_effect=RedisError("Redis error"))
        mock_mongo_client.get_context = AsyncMock(return_value=sample_context)
        
        with patch('geaicontext.tools.retrieve.get_redis_client', return_value=mock_redis_client):
            with patch('geaicontext.tools.retrieve.get_mongo_client', return_value=mock_mongo_client):
                result = await retrieve_user_context("test_customer_123")
        
        # Should still return data from MongoDB
        assert result == sample_context
        mock_mongo_client.get_context.assert_called_once()

    @pytest.mark.asyncio
    async def test_retrieve_mongo_error_returns_none(self, mock_redis_client, mock_mongo_client):
        """Test graceful failure when MongoDB errors."""
        from pymongo.errors import PyMongoError
        
        mock_redis_client.get_context = AsyncMock(return_value=None)
        mock_mongo_client.get_context = AsyncMock(side_effect=PyMongoError("Database error"))
        
        with patch('geaicontext.tools.retrieve.get_redis_client', return_value=mock_redis_client):
            with patch('geaicontext.tools.retrieve.get_mongo_client', return_value=mock_mongo_client):
                result = await retrieve_user_context("test_customer_123")
        
        # Should return None gracefully
        assert result is None

    @pytest.mark.asyncio
    async def test_retrieve_cache_population_failure(self, mock_redis_client, mock_mongo_client, sample_context):
        """Test that cache population failure doesn't affect result."""
        from redis.exceptions import RedisError
        
        mock_redis_client.get_context = AsyncMock(return_value=None)
        mock_mongo_client.get_context = AsyncMock(return_value=sample_context)
        mock_redis_client.set_context = AsyncMock(side_effect=RedisError("Cache write failed"))
        
        with patch('geaicontext.tools.retrieve.get_redis_client', return_value=mock_redis_client):
            with patch('geaicontext.tools.retrieve.get_mongo_client', return_value=mock_mongo_client):
                result = await retrieve_user_context("test_customer_123")
        
        # Should still return data even if cache population fails
        assert result == sample_context


class TestSaveUserContext:
    """Test save_user_context tool."""

    @pytest.mark.asyncio
    async def test_save_success(self, mock_redis_client, mock_mongo_client, sample_context):
        """Test successful context save."""
        mock_redis_client.set_context = AsyncMock(return_value=True)
        mock_mongo_client.save_context = AsyncMock(return_value=True)
        
        with patch('geaicontext.tools.save.get_redis_client', return_value=mock_redis_client):
            with patch('geaicontext.tools.save.get_mongo_client', return_value=mock_mongo_client):
                with patch('geaicontext.tools.save.validate_context', return_value=(True, None)):
                    success, message = await save_user_context("test_customer_123", sample_context)
        
        assert success is True
        assert "successfully" in message.lower()
        mock_redis_client.set_context.assert_called_once_with("test_customer_123", sample_context)

    @pytest.mark.asyncio
    async def test_save_validation_failure(self, mock_redis_client, mock_mongo_client):
        """Test save with invalid context data."""
        invalid_context = {"invalid": "data"}
        
        with patch('geaicontext.tools.save.get_redis_client', return_value=mock_redis_client):
            with patch('geaicontext.tools.save.get_mongo_client', return_value=mock_mongo_client):
                with patch('geaicontext.tools.save.validate_context', return_value=(False, "Missing required field: customer_id")):
                    success, message = await save_user_context("test_customer_123", invalid_context)
        
        assert success is False
        assert "validation error" in message.lower()
        # Should not call Redis or MongoDB
        mock_redis_client.set_context.assert_not_called()

    @pytest.mark.asyncio
    async def test_save_empty_customer_id(self, mock_redis_client, mock_mongo_client, sample_context):
        """Test save with empty customer_id."""
        with patch('geaicontext.tools.save.get_redis_client', return_value=mock_redis_client):
            with patch('geaicontext.tools.save.get_mongo_client', return_value=mock_mongo_client):
                success, message = await save_user_context("", sample_context)
        
        assert success is False
        assert "customer_id is required" in message

    @pytest.mark.asyncio
    async def test_save_empty_context(self, mock_redis_client, mock_mongo_client):
        """Test save with empty context."""
        with patch('geaicontext.tools.save.get_redis_client', return_value=mock_redis_client):
            with patch('geaicontext.tools.save.get_mongo_client', return_value=mock_mongo_client):
                success, message = await save_user_context("test_customer_123", {})
        
        assert success is False
        assert "context data is required" in message

    @pytest.mark.asyncio
    async def test_save_redis_failure(self, mock_redis_client, mock_mongo_client, sample_context):
        """Test save when Redis write fails."""
        from redis.exceptions import RedisError
        
        mock_redis_client.set_context = AsyncMock(side_effect=RedisError("Redis error"))
        
        with patch('geaicontext.tools.save.get_redis_client', return_value=mock_redis_client):
            with patch('geaicontext.tools.save.get_mongo_client', return_value=mock_mongo_client):
                with patch('geaicontext.tools.save.validate_context', return_value=(True, None)):
                    success, message = await save_user_context("test_customer_123", sample_context)
        
        assert success is False
        assert "redis error" in message.lower()

    @pytest.mark.asyncio
    async def test_save_redis_returns_false(self, mock_redis_client, mock_mongo_client, sample_context):
        """Test save when Redis set_context returns False."""
        mock_redis_client.set_context = AsyncMock(return_value=False)
        
        with patch('geaicontext.tools.save.get_redis_client', return_value=mock_redis_client):
            with patch('geaicontext.tools.save.get_mongo_client', return_value=mock_mongo_client):
                with patch('geaicontext.tools.save.validate_context', return_value=(True, None)):
                    success, message = await save_user_context("test_customer_123", sample_context)
        
        assert success is False
        assert "failed to write to redis" in message.lower()

    @pytest.mark.asyncio
    async def test_save_async_mongo_write(self, mock_redis_client, mock_mongo_client, sample_context):
        """Test that MongoDB write happens asynchronously."""
        mock_redis_client.set_context = AsyncMock(return_value=True)
        mock_mongo_client.save_context = AsyncMock(return_value=True)
        
        with patch('geaicontext.tools.save.get_redis_client', return_value=mock_redis_client):
            with patch('geaicontext.tools.save.get_mongo_client', return_value=mock_mongo_client):
                with patch('geaicontext.tools.save.validate_context', return_value=(True, None)):
                    success, message = await save_user_context("test_customer_123", sample_context)
        
        assert success is True
        
        # Give async task time to complete
        await asyncio.sleep(0.1)
        
        # MongoDB should have been called asynchronously
        mock_mongo_client.save_context.assert_called_once_with("test_customer_123", sample_context)

    @pytest.mark.asyncio
    async def test_save_mongo_async_failure_doesnt_affect_response(self, mock_redis_client, mock_mongo_client, sample_context):
        """Test that async MongoDB failure doesn't affect the response."""
        from pymongo.errors import PyMongoError
        
        mock_redis_client.set_context = AsyncMock(return_value=True)
        mock_mongo_client.save_context = AsyncMock(side_effect=PyMongoError("Database error"))
        
        with patch('geaicontext.tools.save.get_redis_client', return_value=mock_redis_client):
            with patch('geaicontext.tools.save.get_mongo_client', return_value=mock_mongo_client):
                with patch('geaicontext.tools.save.validate_context', return_value=(True, None)):
                    success, message = await save_user_context("test_customer_123", sample_context)
        
        # Should still return success because Redis write succeeded
        assert success is True
        
        # Give async task time to fail
        await asyncio.sleep(0.1)


class TestIntegrationScenarios:
    """Test complete integration scenarios."""

    @pytest.mark.asyncio
    async def test_save_then_retrieve_workflow(self, mock_redis_client, mock_mongo_client, sample_context):
        """Test complete save and retrieve workflow."""
        # Setup mocks
        mock_redis_client.set_context = AsyncMock(return_value=True)
        mock_redis_client.get_context = AsyncMock(return_value=sample_context)
        mock_mongo_client.save_context = AsyncMock(return_value=True)
        
        with patch('geaicontext.tools.save.get_redis_client', return_value=mock_redis_client):
            with patch('geaicontext.tools.save.get_mongo_client', return_value=mock_mongo_client):
                with patch('geaicontext.tools.save.validate_context', return_value=(True, None)):
                    # Save context
                    success, message = await save_user_context("test_customer_123", sample_context)
                    assert success is True
        
        # Give async MongoDB write time to complete
        await asyncio.sleep(0.1)
        
        with patch('geaicontext.tools.retrieve.get_redis_client', return_value=mock_redis_client):
            with patch('geaicontext.tools.retrieve.get_mongo_client', return_value=mock_mongo_client):
                # Retrieve context
                result = await retrieve_user_context("test_customer_123")
                assert result == sample_context

    @pytest.mark.asyncio
    async def test_cache_miss_populates_cache(self, mock_redis_client, mock_mongo_client, sample_context):
        """Test that cache miss from MongoDB populates Redis."""
        # First call: cache miss, DB hit
        mock_redis_client.get_context = AsyncMock(return_value=None)
        mock_mongo_client.get_context = AsyncMock(return_value=sample_context)
        mock_redis_client.set_context = AsyncMock(return_value=True)
        
        with patch('geaicontext.tools.retrieve.get_redis_client', return_value=mock_redis_client):
            with patch('geaicontext.tools.retrieve.get_mongo_client', return_value=mock_mongo_client):
                result1 = await retrieve_user_context("test_customer_123")
        
        assert result1 == sample_context
        mock_redis_client.set_context.assert_called_once_with("test_customer_123", sample_context)
        
        # Second call: should hit cache
        mock_redis_client.get_context = AsyncMock(return_value=sample_context)
        mock_redis_client.set_context.reset_mock()
        mock_mongo_client.get_context.reset_mock()
        
        with patch('geaicontext.tools.retrieve.get_redis_client', return_value=mock_redis_client):
            with patch('geaicontext.tools.retrieve.get_mongo_client', return_value=mock_mongo_client):
                result2 = await retrieve_user_context("test_customer_123")
        
        assert result2 == sample_context
        # MongoDB should not be called on second retrieval
        mock_mongo_client.get_context.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_existing_context(self, mock_redis_client, mock_mongo_client, sample_context):
        """Test updating an existing context."""
        # Save initial context
        mock_redis_client.set_context = AsyncMock(return_value=True)
        mock_mongo_client.save_context = AsyncMock(return_value=True)
        
        with patch('geaicontext.tools.save.get_redis_client', return_value=mock_redis_client):
            with patch('geaicontext.tools.save.get_mongo_client', return_value=mock_mongo_client):
                with patch('geaicontext.tools.save.validate_context', return_value=(True, None)):
                    success1, _ = await save_user_context("test_customer_123", sample_context)
        
        assert success1 is True
        
        # Update context
        updated_context = sample_context.copy()
        updated_context["user_preferences"]["theme"] = "light"
        
        mock_redis_client.set_context.reset_mock()
        
        with patch('geaicontext.tools.save.get_redis_client', return_value=mock_redis_client):
            with patch('geaicontext.tools.save.get_mongo_client', return_value=mock_mongo_client):
                with patch('geaicontext.tools.save.validate_context', return_value=(True, None)):
                    success2, _ = await save_user_context("test_customer_123", updated_context)
        
        assert success2 is True
        mock_redis_client.set_context.assert_called_with("test_customer_123", updated_context)


class TestErrorRecovery:
    """Test error recovery scenarios."""

    @pytest.mark.asyncio
    async def test_both_redis_and_mongo_fail_on_retrieve(self, mock_redis_client, mock_mongo_client):
        """Test graceful failure when both Redis and MongoDB fail."""
        from redis.exceptions import RedisError
        from pymongo.errors import PyMongoError
        
        mock_redis_client.get_context = AsyncMock(side_effect=RedisError("Redis down"))
        mock_mongo_client.get_context = AsyncMock(side_effect=PyMongoError("MongoDB down"))
        
        with patch('geaicontext.tools.retrieve.get_redis_client', return_value=mock_redis_client):
            with patch('geaicontext.tools.retrieve.get_mongo_client', return_value=mock_mongo_client):
                result = await retrieve_user_context("test_customer_123")
        
        # Should return None gracefully
        assert result is None

    @pytest.mark.asyncio
    async def test_unexpected_error_handling(self, mock_redis_client, mock_mongo_client):
        """Test handling of unexpected errors."""
        mock_redis_client.get_context = AsyncMock(side_effect=Exception("Unexpected error"))
        
        with patch('geaicontext.tools.retrieve.get_redis_client', return_value=mock_redis_client):
            with patch('geaicontext.tools.retrieve.get_mongo_client', return_value=mock_mongo_client):
                result = await retrieve_user_context("test_customer_123")
        
        # Should handle gracefully and try MongoDB
        assert result is None or isinstance(result, dict)