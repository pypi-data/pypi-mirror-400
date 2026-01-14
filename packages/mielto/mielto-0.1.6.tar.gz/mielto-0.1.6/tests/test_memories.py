"""Tests for Memory resource."""

from unittest.mock import Mock

import pytest

from mielto.client.base import BaseClient
from mielto.resources.memories import Memories
from mielto.types import MemoryCreate, MemorySearchRequest, MemoryUpdate


class TestMemories:
    """Test cases for Memories resource."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client."""
        client = Mock(spec=BaseClient)
        return client

    @pytest.fixture
    def memories(self, mock_client):
        """Create a Memories instance with mock client."""
        return Memories(mock_client)

    def test_create_memory(self, memories, mock_client):
        """Test creating a memory."""
        mock_client.post.return_value = {
            "memory": {
                "memory_id": "mem_123",
                "user_id": "user_123",
                "memory": "Test memory",
                "topics": ["test"],
            }
        }

        memory = memories.create(MemoryCreate(user_id="user_123", memory="Test memory", topics=["test"]))

        assert memory.memory_id == "mem_123"
        assert memory.memory == "Test memory"
        mock_client.post.assert_called_once()

    def test_get_memory(self, memories, mock_client):
        """Test getting a specific memory."""
        mock_client.get.return_value = {
            "memory_id": "mem_123",
            "user_id": "user_123",
            "memory": "Test memory",
            "topics": ["test"],
        }

        memory = memories.get("mem_123", user_id="user_123")

        assert memory.memory_id == "mem_123"
        mock_client.get.assert_called_once()

    def test_update_memory(self, memories, mock_client):
        """Test updating a memory."""
        mock_client.put.return_value = {
            "memory": {
                "memory_id": "mem_123",
                "user_id": "user_123",
                "memory": "Updated memory",
                "topics": ["test", "updated"],
            }
        }

        memory = memories.update("mem_123", MemoryUpdate(memory="Updated memory", topics=["test", "updated"]))

        assert memory.memory == "Updated memory"
        assert "updated" in memory.topics
        mock_client.put.assert_called_once()

    def test_search_memories(self, memories, mock_client):
        """Test searching memories."""
        mock_client.post.return_value = {
            "memories": [
                {
                    "memory_id": "mem_123",
                    "user_id": "user_123",
                    "memory": "Test memory",
                    "topics": ["test"],
                }
            ],
            "total_results": 1,
            "query": "test",
            "retrieval_method": "agentic",
        }

        results = memories.search(MemorySearchRequest(query="test", user_id="user_123", limit=10))

        assert results.total_results == 1
        assert len(results.memories) == 1
        mock_client.post.assert_called_once()

    def test_delete_memory(self, memories, mock_client):
        """Test deleting a memory."""
        mock_client.delete.return_value = {"memory_id": "mem_123", "message": "Memory deleted successfully"}

        result = memories.delete("mem_123", user_id="user_123")

        assert result["message"] == "Memory deleted successfully"
        mock_client.delete.assert_called_once()

    def test_from_messages(self, memories, mock_client):
        """Test creating memories from messages."""
        mock_client.post.return_value = {
            "message": "Memories created successfully from messages",
            "result": {"memories_created": 2, "memory_ids": ["mem_123", "mem_456"]},
        }

        messages = [
            {"role": "user", "content": "Test message"},
            {"role": "assistant", "content": "Response"},
        ]

        result = memories.from_messages(messages=messages, user_id="user_123", agent_id="agent_456")

        assert result.message == "Memories created successfully from messages"
        assert result.result is not None
        # Should be called once to the /memories/from_messages endpoint
        mock_client.post.assert_called_once_with(
            "/memories/from_messages", json_data={"messages": messages, "user_id": "user_123", "agent_id": "agent_456"}
        )
