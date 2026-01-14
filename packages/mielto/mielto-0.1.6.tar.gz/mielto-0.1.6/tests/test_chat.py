"""Tests for chat completions."""

from unittest.mock import patch

import pytest

from mielto import AsyncMielto, Mielto
from mielto.types.chat import ChatCompletion, ChatMessage


@pytest.fixture
def mock_chat_response():
    """Mock chat completion response."""
    return {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "created": 1677652288,
        "model": "gpt-4o",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": "Hello! How can I help you today?"},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 10, "completion_tokens": 9, "total_tokens": 19},
    }


@pytest.fixture
def mielto_client():
    """Create a Mielto client for testing."""
    return Mielto(api_key="test-api-key", base_url="https://api.test.com/v1")


@pytest.fixture
def async_mielto_client():
    """Create an async Mielto client for testing."""
    return AsyncMielto(api_key="test-api-key", base_url="https://api.test.com/v1")


def test_chat_completions_create(mielto_client, mock_chat_response):
    """Test creating a chat completion."""
    with patch.object(mielto_client._client, "post", return_value=mock_chat_response):
        response = mielto_client.chat.completions.create(
            model="gpt-4o", messages=[{"role": "user", "content": "Hello"}]
        )

        assert isinstance(response, ChatCompletion)
        assert response.id == "chatcmpl-123"
        assert response.model == "gpt-4o"
        assert len(response.choices) == 1
        assert response.choices[0].message.content == "Hello! How can I help you today?"
        assert response.usage.total_tokens == 19


def test_chat_completions_with_parameters(mielto_client, mock_chat_response):
    """Test creating a chat completion with additional parameters."""
    with patch.object(mielto_client._client, "post", return_value=mock_chat_response) as mock_post:
        response = mielto_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Hello"}],
            temperature=0.7,
            max_tokens=100,
            top_p=0.9,
            user_id="user_123",
            conversation_id="conv_456",
        )

        print(response)

        # Verify the request payload
        call_args = mock_post.call_args
        assert call_args[0][0] == "chat/completions"
        payload = call_args[1]["json_data"]

        assert payload["model"] == "gpt-4o"
        assert payload["temperature"] == 0.7
        assert payload["max_tokens"] == 100
        assert payload["top_p"] == 0.9
        assert payload["user_id"] == "user_123"
        assert payload["conversation_id"] == "conv_456"


def test_chat_completions_with_typed_messages(mielto_client, mock_chat_response):
    """Test creating a chat completion with typed ChatMessage objects."""
    with patch.object(mielto_client._client, "post", return_value=mock_chat_response):
        messages = [ChatMessage(role="system", content="You are helpful"), ChatMessage(role="user", content="Hello")]

        response = mielto_client.chat.completions.create(model="gpt-4o", messages=messages)

        assert isinstance(response, ChatCompletion)
        assert response.choices[0].message.content == "Hello! How can I help you today?"


def test_chat_completions_with_tools(mielto_client):
    """Test creating a chat completion with tools/functions."""
    # Mock response with tool_calls
    mock_response_with_tools = {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "created": 1677652288,
        "model": "gpt-4o",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": "call_123",
                            "type": "function",
                            "function": {"name": "get_weather", "arguments": '{"location": "San Francisco"}'},
                        }
                    ],
                },
                "finish_reason": "tool_calls",
            }
        ],
        "usage": {"prompt_tokens": 10, "completion_tokens": 9, "total_tokens": 19},
    }

    with patch.object(mielto_client._client, "post", return_value=mock_response_with_tools) as mock_post:
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get weather for a location",
                    "parameters": {
                        "type": "object",
                        "properties": {"location": {"type": "string"}},
                        "required": ["location"],
                    },
                },
            }
        ]

        response = mielto_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "What's the weather?"}],
            tools=tools,
            tool_choice="auto",
        )

        assert response.choices[0].message.tool_calls is not None
        assert len(response.choices[0].message.tool_calls) == 1
        # tool_calls is a list of dicts
        assert response.choices[0].message.tool_calls[0]["function"]["name"] == "get_weather"

        # Verify tools were included in the request
        payload = mock_post.call_args[1]["json_data"]
        assert "tools" in payload
        assert payload["tools"] == tools
        assert payload["tool_choice"] == "auto"


def test_chat_completions_with_context_injection(mielto_client, mock_chat_response):
    """Test creating a chat completion with Mielto context injection parameters."""
    with patch.object(mielto_client._client, "post", return_value=mock_chat_response) as mock_post:
        response = mielto_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Hello"}],
            user_id="user_123",
            conversation_id="conv_456",
            session_id="sess_789",
            workspace_id="workspace_abc",
            collection_ids=["coll1", "coll2"],
        )

        print(response)

        # Verify Mielto-specific parameters
        payload = mock_post.call_args[1]["json_data"]
        assert payload["user_id"] == "user_123"
        assert payload["conversation_id"] == "conv_456"
        assert payload["session_id"] == "sess_789"
        assert payload["workspace_id"] == "workspace_abc"
        assert payload["collection_ids"] == ["coll1", "coll2"]


@pytest.mark.asyncio
async def test_async_chat_completions_create(async_mielto_client, mock_chat_response):
    """Test creating an async chat completion."""
    with patch.object(async_mielto_client._client, "post", return_value=mock_chat_response) as mock_post:
        # Make the mock async
        async def async_post(*args, **kwargs):
            return mock_chat_response

        mock_post.side_effect = async_post

        response = await async_mielto_client.chat.completions.create(
            model="gpt-4o", messages=[{"role": "user", "content": "Hello"}]
        )

        assert isinstance(response, ChatCompletion)
        assert response.id == "chatcmpl-123"
        assert response.choices[0].message.content == "Hello! How can I help you today?"


def test_chat_resource_exists(mielto_client):
    """Test that chat resource is properly initialized."""
    assert hasattr(mielto_client, "chat")
    assert hasattr(mielto_client.chat, "completions")
    assert hasattr(mielto_client.chat.completions, "create")


def test_async_chat_resource_exists(async_mielto_client):
    """Test that async chat resource is properly initialized."""
    assert hasattr(async_mielto_client, "chat")
    assert hasattr(async_mielto_client.chat, "completions")
    assert hasattr(async_mielto_client.chat.completions, "create")


def test_chat_message_model():
    """Test ChatMessage model validation."""
    message = ChatMessage(role="user", content="Hello")
    assert message.role == "user"
    assert message.content == "Hello"

    # Test with assistant role and tool calls
    message = ChatMessage(
        role="assistant",
        content=None,
        tool_calls=[{"id": "call_123", "type": "function", "function": {"name": "test"}}],
    )
    assert message.role == "assistant"
    assert message.tool_calls is not None


def test_chat_completion_model(mock_chat_response):
    """Test ChatCompletion model validation."""
    completion = ChatCompletion(**mock_chat_response)
    assert completion.id == "chatcmpl-123"
    assert completion.object == "chat.completion"
    assert completion.model == "gpt-4o"
    assert len(completion.choices) == 1
    assert completion.usage.total_tokens == 19
