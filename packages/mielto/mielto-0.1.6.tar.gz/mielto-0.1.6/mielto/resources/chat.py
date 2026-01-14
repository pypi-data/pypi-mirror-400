"""Chat completion resources for Mielto API."""

import json
from typing import Any, AsyncIterator, Dict, Iterator, List, Optional, Union

from mielto.client.base import AsyncBaseClient, BaseClient
from mielto.types.chat import (
    ChatCompletion,
    ChatCompletionChunk,
    ChatMessage,
)


class Completions:
    """Sync chat completions resource."""

    def __init__(self, client: BaseClient):
        """Initialize the completions resource.

        Args:
            client: The base HTTP client
        """
        self._client = client

    def create(
        self,
        model: str,
        messages: List[Union[ChatMessage, Dict[str, Any]]],
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        n: Optional[int] = None,
        stream: bool = False,
        stop: Optional[Union[str, List[str]]] = None,
        max_tokens: Optional[int] = None,
        presence_penalty: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        logit_bias: Optional[Dict[str, float]] = None,
        user: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        response_format: Optional[Dict[str, Any]] = None,
        seed: Optional[int] = None,
        logprobs: Optional[bool] = None,
        top_logprobs: Optional[int] = None,
        # Mielto-specific parameters
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        session_id: Optional[str] = None,
        collection_ids: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Union[ChatCompletion, Iterator[ChatCompletionChunk]]:
        """Create a chat completion.

        Args:
            model: ID of the model to use
            messages: List of messages in the conversation
            temperature: Sampling temperature (0-2)
            top_p: Nucleus sampling parameter
            n: Number of completions to generate
            stream: Whether to stream the response
            stop: Sequences where the API will stop generating
            max_tokens: Maximum number of tokens to generate
            presence_penalty: Presence penalty (-2.0 to 2.0)
            frequency_penalty: Frequency penalty (-2.0 to 2.0)
            logit_bias: Modify likelihood of specified tokens
            user: Unique identifier for the end-user
            tools: List of tools the model can call
            tool_choice: Controls which tool is called
            response_format: Format of the response (e.g., {"type": "json_object"})
            seed: Random seed for deterministic sampling
            logprobs: Whether to return log probabilities
            top_logprobs: Number of most likely tokens to return
            user_id: Mielto user identifier
            conversation_id: Mielto conversation identifier
            session_id: Mielto session identifier
            collection_ids: List of collection IDs for knowledge retrieval

        Returns:
            ChatCompletion or Iterator of ChatCompletionChunk if streaming
        """
        # Build request payload
        payload: Dict[str, Any] = {
            "model": model,
            "messages": [msg if isinstance(msg, dict) else msg.model_dump() for msg in messages],
        }

        # Add optional parameters
        if temperature is not None:
            payload["temperature"] = temperature
        if top_p is not None:
            payload["top_p"] = top_p
        if n is not None:
            payload["n"] = n
        if stream:
            payload["stream"] = stream
        if stop is not None:
            payload["stop"] = stop
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if presence_penalty is not None:
            payload["presence_penalty"] = presence_penalty
        if frequency_penalty is not None:
            payload["frequency_penalty"] = frequency_penalty
        if logit_bias is not None:
            payload["logit_bias"] = logit_bias
        if user is not None:
            payload["user"] = user
        if tools is not None:
            payload["tools"] = tools
        if tool_choice is not None:
            payload["tool_choice"] = tool_choice
        if response_format is not None:
            payload["response_format"] = response_format
        if seed is not None:
            payload["seed"] = seed
        if logprobs is not None:
            payload["logprobs"] = logprobs
        if top_logprobs is not None:
            payload["top_logprobs"] = top_logprobs

        # Add Mielto-specific parameters
        if user_id is not None:
            payload["user_id"] = user_id
        if conversation_id is not None:
            payload["conversation_id"] = conversation_id
        if session_id is not None:
            payload["session_id"] = session_id
        if collection_ids is not None:
            payload["collection_ids"] = collection_ids

        # Add any additional kwargs
        payload.update(kwargs)

        if stream:
            return self._create_stream(payload)
        else:
            response = self._client.post("chat/completions", json_data=payload)
            return ChatCompletion(**response)

    def _create_stream(self, payload: Dict[str, Any]) -> Iterator[ChatCompletionChunk]:
        """Create a streaming chat completion.

        Args:
            payload: Request payload

        Yields:
            ChatCompletionChunk objects
        """
        import httpx

        url = self._client._build_url("chat/completions")

        with httpx.stream(
            "POST",
            url,
            json=payload,
            headers=self._client._get_headers(),
            timeout=self._client.timeout,
        ) as response:
            if not response.is_success:
                print(response)
                self._client._handle_response_error(response)

            for line in response.iter_lines():
                if line.startswith("data: "):
                    data = line[6:]  # Remove "data: " prefix
                    if data == "[DONE]":
                        break
                    try:
                        chunk_data = json.loads(data)
                        yield ChatCompletionChunk(**chunk_data)
                    except json.JSONDecodeError:
                        continue


class AsyncCompletions:
    """Async chat completions resource."""

    def __init__(self, client: AsyncBaseClient):
        """Initialize the async completions resource.

        Args:
            client: The async base HTTP client
        """
        self._client = client

    async def create(
        self,
        model: str,
        messages: List[Union[ChatMessage, Dict[str, Any]]],
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        n: Optional[int] = None,
        stream: bool = False,
        stop: Optional[Union[str, List[str]]] = None,
        max_tokens: Optional[int] = None,
        presence_penalty: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        logit_bias: Optional[Dict[str, float]] = None,
        user: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        response_format: Optional[Dict[str, Any]] = None,
        seed: Optional[int] = None,
        logprobs: Optional[bool] = None,
        top_logprobs: Optional[int] = None,
        # Mielto-specific parameters
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        session_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        collection_ids: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Union[ChatCompletion, AsyncIterator[ChatCompletionChunk]]:
        """Create a chat completion asynchronously.

        Args:
            model: ID of the model to use
            messages: List of messages in the conversation
            temperature: Sampling temperature (0-2)
            top_p: Nucleus sampling parameter
            n: Number of completions to generate
            stream: Whether to stream the response
            stop: Sequences where the API will stop generating
            max_tokens: Maximum number of tokens to generate
            presence_penalty: Presence penalty (-2.0 to 2.0)
            frequency_penalty: Frequency penalty (-2.0 to 2.0)
            logit_bias: Modify likelihood of specified tokens
            user: Unique identifier for the end-user
            tools: List of tools the model can call
            tool_choice: Controls which tool is called
            response_format: Format of the response (e.g., {"type": "json_object"})
            seed: Random seed for deterministic sampling
            logprobs: Whether to return log probabilities
            top_logprobs: Number of most likely tokens to return
            user_id: Mielto user identifier
            conversation_id: Mielto conversation identifier
            session_id: Mielto session identifier
            workspace_id: Mielto workspace identifier
            collection_ids: List of collection IDs for knowledge retrieval

        Returns:
            ChatCompletion or AsyncIterator of ChatCompletionChunk if streaming
        """
        # Build request payload
        payload: Dict[str, Any] = {
            "model": model,
            "messages": [msg if isinstance(msg, dict) else msg.model_dump() for msg in messages],
        }

        # Add optional parameters
        if temperature is not None:
            payload["temperature"] = temperature
        if top_p is not None:
            payload["top_p"] = top_p
        if n is not None:
            payload["n"] = n
        if stream:
            payload["stream"] = stream
        if stop is not None:
            payload["stop"] = stop
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if presence_penalty is not None:
            payload["presence_penalty"] = presence_penalty
        if frequency_penalty is not None:
            payload["frequency_penalty"] = frequency_penalty
        if logit_bias is not None:
            payload["logit_bias"] = logit_bias
        if user is not None:
            payload["user"] = user
        if tools is not None:
            payload["tools"] = tools
        if tool_choice is not None:
            payload["tool_choice"] = tool_choice
        if response_format is not None:
            payload["response_format"] = response_format
        if seed is not None:
            payload["seed"] = seed
        if logprobs is not None:
            payload["logprobs"] = logprobs
        if top_logprobs is not None:
            payload["top_logprobs"] = top_logprobs

        # Add Mielto-specific parameters
        if user_id is not None:
            payload["user_id"] = user_id
        if conversation_id is not None:
            payload["conversation_id"] = conversation_id
        if session_id is not None:
            payload["session_id"] = session_id
        if workspace_id is not None:
            payload["workspace_id"] = workspace_id
        if collection_ids is not None:
            payload["collection_ids"] = collection_ids

        # Add any additional kwargs
        payload.update(kwargs)

        if stream:
            return self._create_stream(payload)
        else:
            response = await self._client.post("chat/completions", json_data=payload)
            return ChatCompletion(**response)

    async def _create_stream(self, payload: Dict[str, Any]) -> AsyncIterator[ChatCompletionChunk]:
        """Create a streaming chat completion asynchronously.

        Args:
            payload: Request payload

        Yields:
            ChatCompletionChunk objects
        """
        import httpx

        url = self._client._build_url("chat/completions")

        async with httpx.AsyncClient(timeout=self._client.timeout) as client:
            async with client.stream(
                "POST",
                url,
                json=payload,
                headers=self._client._get_headers(),
            ) as response:
                if not response.is_success:
                    self._client._handle_response_error(response)

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]  # Remove "data: " prefix
                        if data == "[DONE]":
                            break
                        try:
                            chunk_data = json.loads(data)
                            yield ChatCompletionChunk(**chunk_data)
                        except json.JSONDecodeError:
                            continue


class Chat:
    """Sync chat resource."""

    def __init__(self, client: BaseClient):
        """Initialize the chat resource.

        Args:
            client: The base HTTP client
        """
        self.completions = Completions(client)


class AsyncChat:
    """Async chat resource."""

    def __init__(self, client: AsyncBaseClient):
        """Initialize the async chat resource.

        Args:
            client: The async base HTTP client
        """
        self.completions = AsyncCompletions(client)
