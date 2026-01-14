"""Tests for Mielto client."""

from unittest.mock import patch

from mielto import Mielto
from mielto.types import Memory, MemoryCreate
from mielto.types.upload import UploadResponse


class TestMieltoClient:
    """Test cases for Mielto client."""

    def test_client_initialization(self):
        """Test client initialization."""
        client = Mielto(api_key="test-key")
        assert client._client.api_key == "test-key"
        assert client.memories is not None
        assert client.collections is not None
        assert client.compress is not None
        client.close()

    def test_client_context_manager(self):
        """Test client as context manager."""
        with Mielto(api_key="test-key") as client:
            assert client._client.api_key == "test-key"

    @patch("mielto.client.base.BaseClient.post")
    def test_create_memory(self, mock_post):
        """Test creating a memory."""
        # Mock API response
        mock_post.return_value = {
            "memory": {
                "memory_id": "mem_123",
                "user_id": "user_123",
                "memory": "Test memory",
                "topics": ["test"],
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            }
        }

        with Mielto(api_key="test-key") as client:
            memory = client.memories.create(MemoryCreate(user_id="user_123", memory="Test memory", topics=["test"]))

            assert isinstance(memory, Memory)
            assert memory.memory_id == "mem_123"
            assert memory.memory == "Test memory"
            assert memory.user_id == "user_123"

    @patch("mielto.client.base.BaseClient.get")
    def test_list_memories(self, mock_get):
        """Test listing memories."""
        # Mock API response
        mock_get.return_value = {
            "memories": [
                {
                    "memory_id": "mem_123",
                    "user_id": "user_123",
                    "memory": "Test memory 1",
                    "topics": ["test"],
                }
            ],
            "total_count": 1,
            "next_cursor": None,
            "has_more": False,
        }

        with Mielto(api_key="test-key") as client:
            result = client.memories.list(user_id="user_123")

            assert result.total_count == 1
            assert len(result.memories) == 1
            assert result.memories[0].memory_id == "mem_123"
            assert not result.has_more

    @patch("mielto.client.base.BaseClient.post")
    def test_upload_success(self, mock_post):
        """Test successful upload response."""
        # Mock API response
        mock_post.return_value = {
            "status": "success",
            "contents": [
                {
                    "id": "con_123",
                    "name": "test.pdf",
                    "description": "Test document",
                    "content": None,
                    "content_type": "document",
                    "type": "application/pdf",
                    "size": 1024,
                    "metadata": {},
                }
            ],
        }

        with Mielto(api_key="test-key") as client:
            result = client.collections.insert(collection_id="col_123", content="Test content")

            assert isinstance(result, UploadResponse)
            assert result.status == "success"
            assert result.is_success()
            assert not result.has_failures()
            assert result.total_uploads == 1
            assert result.successful_uploads == 1
            assert result.failed_uploads == 0
            assert len(result.successful) == 1
            assert len(result.errors) == 0

    @patch("mielto.client.base.BaseClient.post")
    def test_upload_partial_success(self, mock_post):
        """Test partial success upload response."""
        # Mock API response
        mock_post.return_value = {
            "status": "partial_success",
            "contents": [
                {
                    "id": "con_123",
                    "name": "success.pdf",
                    "description": None,
                    "content": None,
                    "content_type": "document",
                    "type": "application/pdf",
                    "size": 1024,
                    "metadata": {},
                },
                {
                    "id": None,
                    "name": "failed.pdf",
                    "description": None,
                    "content": None,
                    "content_type": "file",
                    "type": "application/pdf",
                    "size": 0,
                    "metadata": {},
                    "error": "Failed to read file: Invalid PDF format",
                },
            ],
        }

        with Mielto(api_key="test-key") as client:
            result = client.collections.insert(collection_id="col_123", content="Test content")

            assert isinstance(result, UploadResponse)
            assert result.status == "partial_success"
            assert not result.is_success()
            assert result.has_failures()
            assert result.total_uploads == 2
            assert result.successful_uploads == 1
            assert result.failed_uploads == 1
            assert len(result.successful) == 1
            assert len(result.errors) == 1
            assert result.errors[0].name == "failed.pdf"
            assert "Invalid PDF format" in result.errors[0].error

    @patch("mielto.client.base.BaseClient.post")
    def test_upload_all_failed(self, mock_post):
        """Test all failed upload response."""
        # Mock API response
        mock_post.return_value = {
            "status": "failed",
            "contents": [
                {
                    "id": None,
                    "name": "failed.pdf",
                    "description": None,
                    "content": None,
                    "content_type": "file",
                    "type": "application/pdf",
                    "size": 0,
                    "metadata": {},
                    "error": "File not found",
                }
            ],
        }

        with Mielto(api_key="test-key") as client:
            result = client.collections.insert(collection_id="col_123", content="Test content")

            assert isinstance(result, UploadResponse)
            assert result.status == "failed"
            assert not result.is_success()
            assert result.has_failures()
            assert result.total_uploads == 1
            assert result.successful_uploads == 0
            assert result.failed_uploads == 1
            assert len(result.successful) == 0
            assert len(result.errors) == 1
