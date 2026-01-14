"""Unit tests for the MongoDB client."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pymongo.errors import PyMongoError, ConnectionFailure, DuplicateKeyError

from geaicontext.clients.mongo_client import MongoClient, get_mongo_client


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
def sample_document(sample_context):
    """Sample MongoDB document (includes _id)."""
    doc = sample_context.copy()
    doc["_id"] = "507f1f77bcf86cd799439011"
    return doc


@pytest.fixture
def mock_collection():
    """Mock MongoDB collection."""
    mock = AsyncMock()
    mock.find_one = AsyncMock(return_value=None)
    mock.replace_one = AsyncMock()
    mock.delete_one = AsyncMock()
    mock.count_documents = AsyncMock(return_value=0)
    mock.create_index = AsyncMock()
    return mock


@pytest.fixture
def mock_db(mock_collection):
    """Mock MongoDB database."""
    mock = MagicMock()
    mock.__getitem__ = MagicMock(return_value=mock_collection)
    return mock


@pytest.fixture
def mock_motor_client(mock_db):
    """Mock Motor client."""
    mock = AsyncMock()
    mock.admin.command = AsyncMock(return_value={"ok": 1})
    mock.__getitem__ = MagicMock(return_value=mock_db)
    mock.close = MagicMock()
    return mock


@pytest.fixture
async def mongo_client(mock_motor_client, mock_db, mock_collection):
    """Create a MongoDB client with mocked connection."""
    client = MongoClient()
    
    with patch('geaicontext.clients.mongo_client.AsyncIOMotorClient', return_value=mock_motor_client):
        await client.connect()
    
    # Manually set the collection for testing
    client._collection = mock_collection
    
    yield client
    
    await client.disconnect()


class TestMongoClientInitialization:
    """Test MongoDB client initialization and connection."""

    @pytest.mark.asyncio
    async def test_client_initialization(self):
        """Test that client initializes without connection."""
        client = MongoClient()
        assert client._client is None
        assert client._db is None
        assert client._collection is None
        assert client._connected is False

    @pytest.mark.asyncio
    async def test_successful_connection(self, mock_motor_client):
        """Test successful connection to MongoDB."""
        client = MongoClient()
        
        with patch('geaicontext.clients.mongo_client.AsyncIOMotorClient', return_value=mock_motor_client):
            await client.connect()
        
        assert client._client is not None
        assert client._connected is True
        mock_motor_client.admin.command.assert_called_once_with('ping')

    @pytest.mark.asyncio
    async def test_connection_failure(self):
        """Test connection failure handling."""
        client = MongoClient()
        
        mock_client = AsyncMock()
        mock_client.admin.command = AsyncMock(side_effect=ConnectionFailure("Connection failed"))
        
        with patch('geaicontext.clients.mongo_client.AsyncIOMotorClient', return_value=mock_client):
            with pytest.raises(ConnectionFailure):
                await client.connect()

    @pytest.mark.asyncio
    async def test_disconnect(self, mongo_client):
        """Test disconnection from MongoDB."""
        await mongo_client.disconnect()
        assert mongo_client._connected is False

    @pytest.mark.asyncio
    async def test_health_check_connected(self, mongo_client):
        """Test health check when connected."""
        result = await mongo_client.health_check()
        assert result is True

    @pytest.mark.asyncio
    async def test_health_check_not_connected(self):
        """Test health check when not connected."""
        client = MongoClient()
        result = await client.health_check()
        assert result is False

    @pytest.mark.asyncio
    async def test_health_check_connection_error(self, mongo_client):
        """Test health check when ping fails."""
        mongo_client._client.admin.command = AsyncMock(side_effect=PyMongoError("Ping failed"))
        result = await mongo_client.health_check()
        assert result is False


class TestMongoClientGetContext:
    """Test get_context method."""

    @pytest.mark.asyncio
    async def test_get_context_success(self, mongo_client, sample_document, sample_context):
        """Test successful context retrieval."""
        mongo_client._collection.find_one = AsyncMock(return_value=sample_document)
        
        result = await mongo_client.get_context("test_customer_123")
        
        # Should remove _id field
        assert result == sample_context
        assert "_id" not in result
        mongo_client._collection.find_one.assert_called_once_with({"customer_id": "test_customer_123"})

    @pytest.mark.asyncio
    async def test_get_context_not_found(self, mongo_client):
        """Test when context doesn't exist."""
        mongo_client._collection.find_one = AsyncMock(return_value=None)
        
        result = await mongo_client.get_context("nonexistent_customer")
        
        assert result is None

    @pytest.mark.asyncio
    async def test_get_context_not_connected(self):
        """Test get_context when not connected."""
        client = MongoClient()
        
        with pytest.raises(PyMongoError, match="not connected"):
            await client.get_context("test_customer_123")

    @pytest.mark.asyncio
    async def test_get_context_pymongo_error(self, mongo_client):
        """Test handling of PyMongo errors during get."""
        mongo_client._collection.find_one = AsyncMock(side_effect=PyMongoError("Database error"))
        
        with pytest.raises(PyMongoError):
            await mongo_client.get_context("test_customer_123")

    @pytest.mark.asyncio
    async def test_get_context_removes_id_field(self, mongo_client):
        """Test that _id field is always removed."""
        doc_with_id = {
            "_id": "507f1f77bcf86cd799439011",
            "customer_id": "test_123",
            "data": "value"
        }
        mongo_client._collection.find_one = AsyncMock(return_value=doc_with_id)
        
        result = await mongo_client.get_context("test_123")
        
        assert "_id" not in result
        assert result["customer_id"] == "test_123"
        assert result["data"] == "value"


class TestMongoClientSaveContext:
    """Test save_context method."""

    @pytest.mark.asyncio
    async def test_save_context_insert_new(self, mongo_client, sample_context):
        """Test inserting new context (upsert with new document)."""
        mock_result = AsyncMock()
        mock_result.upserted_id = "507f1f77bcf86cd799439011"
        mock_result.matched_count = 0
        
        mongo_client._collection.replace_one = AsyncMock(return_value=mock_result)
        
        result = await mongo_client.save_context("test_customer_123", sample_context)
        
        assert result is True
        mongo_client._collection.replace_one.assert_called_once()
        
        # Verify upsert parameters
        call_args = mongo_client._collection.replace_one.call_args
        assert call_args[0][0] == {"customer_id": "test_customer_123"}
        assert call_args[1]["upsert"] is True

    @pytest.mark.asyncio
    async def test_save_context_update_existing(self, mongo_client, sample_context):
        """Test updating existing context (upsert with existing document)."""
        mock_result = AsyncMock()
        mock_result.upserted_id = None
        mock_result.matched_count = 1
        
        mongo_client._collection.replace_one = AsyncMock(return_value=mock_result)
        
        result = await mongo_client.save_context("test_customer_123", sample_context)
        
        assert result is True

    @pytest.mark.asyncio
    async def test_save_context_ensures_customer_id(self, mongo_client):
        """Test that customer_id is added to context if missing."""
        context_without_id = {
            "data": "value"
        }
        
        mock_result = AsyncMock()
        mock_result.upserted_id = "507f1f77bcf86cd799439011"
        
        mongo_client._collection.replace_one = AsyncMock(return_value=mock_result)
        
        result = await mongo_client.save_context("test_customer_123", context_without_id)
        
        assert result is True
        
        # Verify customer_id was added
        call_args = mongo_client._collection.replace_one.call_args
        saved_context = call_args[0][1]
        assert saved_context["customer_id"] == "test_customer_123"

    @pytest.mark.asyncio
    async def test_save_context_not_connected(self):
        """Test save_context when not connected."""
        client = MongoClient()
        
        with pytest.raises(PyMongoError, match="not connected"):
            await client.save_context("test_customer_123", {"data": "value"})

    @pytest.mark.asyncio
    async def test_save_context_duplicate_key_error(self, mongo_client, sample_context):
        """Test handling of duplicate key errors."""
        mongo_client._collection.replace_one = AsyncMock(
            side_effect=DuplicateKeyError("Duplicate key")
        )
        
        result = await mongo_client.save_context("test_customer_123", sample_context)
        
        assert result is False

    @pytest.mark.asyncio
    async def test_save_context_pymongo_error(self, mongo_client, sample_context):
        """Test handling of PyMongo errors during save."""
        mongo_client._collection.replace_one = AsyncMock(
            side_effect=PyMongoError("Database error")
        )
        
        with pytest.raises(PyMongoError):
            await mongo_client.save_context("test_customer_123", sample_context)

    @pytest.mark.asyncio
    async def test_save_context_preserves_original(self, mongo_client):
        """Test that original context dict is not modified."""
        original_context = {
            "data": "value"
        }
        
        mock_result = AsyncMock()
        mock_result.upserted_id = "507f1f77bcf86cd799439011"
        
        mongo_client._collection.replace_one = AsyncMock(return_value=mock_result)
        
        await mongo_client.save_context("test_customer_123", original_context)
        
        # Original should not have customer_id added
        assert "customer_id" not in original_context


class TestMongoClientDeleteContext:
    """Test delete_context method."""

    @pytest.mark.asyncio
    async def test_delete_context_success(self, mongo_client):
        """Test successful context deletion."""
        mock_result = AsyncMock()
        mock_result.deleted_count = 1
        
        mongo_client._collection.delete_one = AsyncMock(return_value=mock_result)
        
        result = await mongo_client.delete_context("test_customer_123")
        
        assert result is True
        mongo_client._collection.delete_one.assert_called_once_with({"customer_id": "test_customer_123"})

    @pytest.mark.asyncio
    async def test_delete_context_not_found(self, mongo_client):
        """Test deletion when context doesn't exist."""
        mock_result = AsyncMock()
        mock_result.deleted_count = 0
        
        mongo_client._collection.delete_one = AsyncMock(return_value=mock_result)
        
        result = await mongo_client.delete_context("nonexistent_customer")
        
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_context_not_connected(self):
        """Test delete_context when not connected."""
        client = MongoClient()
        
        with pytest.raises(PyMongoError, match="not connected"):
            await client.delete_context("test_customer_123")

    @pytest.mark.asyncio
    async def test_delete_context_pymongo_error(self, mongo_client):
        """Test handling of PyMongo errors during delete."""
        mongo_client._collection.delete_one = AsyncMock(
            side_effect=PyMongoError("Database error")
        )
        
        with pytest.raises(PyMongoError):
            await mongo_client.delete_context("test_customer_123")


class TestMongoClientCountContexts:
    """Test count_contexts method."""

    @pytest.mark.asyncio
    async def test_count_contexts_success(self, mongo_client):
        """Test successful context counting."""
        mongo_client._collection.count_documents = AsyncMock(return_value=42)
        
        result = await mongo_client.count_contexts()
        
        assert result == 42
        mongo_client._collection.count_documents.assert_called_once_with({})

    @pytest.mark.asyncio
    async def test_count_contexts_empty(self, mongo_client):
        """Test counting when no contexts exist."""
        mongo_client._collection.count_documents = AsyncMock(return_value=0)
        
        result = await mongo_client.count_contexts()
        
        assert result == 0

    @pytest.mark.asyncio
    async def test_count_contexts_not_connected(self):
        """Test count_contexts when not connected."""
        client = MongoClient()
        
        with pytest.raises(PyMongoError, match="not connected"):
            await client.count_contexts()

    @pytest.mark.asyncio
    async def test_count_contexts_pymongo_error(self, mongo_client):
        """Test handling of PyMongo errors during count."""
        mongo_client._collection.count_documents = AsyncMock(
            side_effect=PyMongoError("Database error")
        )
        
        with pytest.raises(PyMongoError):
            await mongo_client.count_contexts()


class TestGlobalMongoClient:
    """Test global client instance."""

    @pytest.mark.asyncio
    async def test_get_mongo_client_singleton(self):
        """Test that get_mongo_client returns singleton instance."""
        client1 = await get_mongo_client()
        client2 = await get_mongo_client()
        assert client1 is client2

    @pytest.mark.asyncio
    async def test_get_mongo_client_not_connected(self):
        """Test that get_mongo_client returns unconnected client."""
        client = await get_mongo_client()
        # Client should exist but not be connected yet
        assert client is not None


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.mark.asyncio
    async def test_save_context_with_unicode(self, mongo_client):
        """Test saving context with Unicode characters."""
        unicode_context = {
            "customer_id": "test_123",
            "name": "José García",
            "message": "¡Hola! 你好"
        }
        
        mock_result = AsyncMock()
        mock_result.upserted_id = "507f1f77bcf86cd799439011"
        
        mongo_client._collection.replace_one = AsyncMock(return_value=mock_result)
        
        result = await mongo_client.save_context("test_123", unicode_context)
        
        assert result is True

    @pytest.mark.asyncio
    async def test_large_context_data(self, mongo_client):
        """Test saving large context data."""
        large_context = {
            "customer_id": "test_123",
            "data": "x" * 1000000  # 1MB of data
        }
        
        mock_result = AsyncMock()
        mock_result.upserted_id = "507f1f77bcf86cd799439011"
        
        mongo_client._collection.replace_one = AsyncMock(return_value=mock_result)
        
        result = await mongo_client.save_context("test_123", large_context)
        
        assert result is True

    @pytest.mark.asyncio
    async def test_empty_context_data(self, mongo_client):
        """Test saving empty context."""
        empty_context = {}
        
        mock_result = AsyncMock()
        mock_result.upserted_id = "507f1f77bcf86cd799439011"
        
        mongo_client._collection.replace_one = AsyncMock(return_value=mock_result)
        
        result = await mongo_client.save_context("test_123", empty_context)
        
        assert result is True
        
        # Verify customer_id was added
        call_args = mongo_client._collection.replace_one.call_args
        saved_context = call_args[0][1]
        assert saved_context["customer_id"] == "test_123"

    @pytest.mark.asyncio
    async def test_deeply_nested_context(self, mongo_client):
        """Test saving deeply nested context data."""
        nested_context = {
            "customer_id": "test_123",
            "level1": {
                "level2": {
                    "level3": {
                        "level4": {
                            "level5": "deep_value"
                        }
                    }
                }
            }
        }
        
        mock_result = AsyncMock()
        mock_result.upserted_id = "507f1f77bcf86cd799439011"
        
        mongo_client._collection.replace_one = AsyncMock(return_value=mock_result)
        
        result = await mongo_client.save_context("test_123", nested_context)
        
        assert result is True

    @pytest.mark.asyncio
    async def test_multiple_operations_sequence(self, mongo_client, sample_context):
        """Test sequence of operations."""
        # Save
        mock_save_result = AsyncMock()
        mock_save_result.upserted_id = "507f1f77bcf86cd799439011"
        mongo_client._collection.replace_one = AsyncMock(return_value=mock_save_result)
        
        save_result = await mongo_client.save_context("test_customer_123", sample_context)
        assert save_result is True
        
        # Get
        doc_with_id = sample_context.copy()
        doc_with_id["_id"] = "507f1f77bcf86cd799439011"
        mongo_client._collection.find_one = AsyncMock(return_value=doc_with_id)
        
        get_result = await mongo_client.get_context("test_customer_123")
        assert get_result == sample_context
        
        # Count
        mongo_client._collection.count_documents = AsyncMock(return_value=1)
        count_result = await mongo_client.count_contexts()
        assert count_result == 1
        
        # Delete
        mock_delete_result = AsyncMock()
        mock_delete_result.deleted_count = 1
        mongo_client._collection.delete_one = AsyncMock(return_value=mock_delete_result)
        
        delete_result = await mongo_client.delete_context("test_customer_123")
        assert delete_result is True
        
        # Get after delete
        mongo_client._collection.find_one = AsyncMock(return_value=None)
        get_after_delete = await mongo_client.get_context("test_customer_123")
        assert get_after_delete is None