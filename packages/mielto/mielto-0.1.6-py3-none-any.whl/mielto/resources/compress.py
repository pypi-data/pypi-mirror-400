"""Compress resource for text compression via Mielto API."""

from typing import Any, Dict, List, Optional, Union

from mielto.client.base import AsyncBaseClient, BaseClient
from mielto.types.compress import CompressRequest, CompressResponse


class Compress:
    """Synchronous Compress resource."""

    def __init__(self, client: BaseClient):
        """Initialize the Compress resource.

        Args:
            client: Base HTTP client instance
        """
        self._client = client

    def compress(
        self,
        content: Union[str, List[Dict[str, Any]]],
        strategy: str = "ai_compress",
        include_metadata: bool = False,
        webhook_url: Optional[str] = None,
    ) -> CompressResponse:
        """Compress text content using AI.

        Args:
            content: Content to compress (string or list of message objects)
            strategy: Compression strategy to use
            include_metadata: Whether to include metadata in compression
            webhook_url: Optional webhook URL for async results

        Returns:
            CompressResponse with compressed content

        Examples:
            ```python
            # Compress simple text
            result = client.compress.compress(
                content="This is a very long text that needs to be compressed..."
            )
            print(result.content)
            print(f"Reduced from {result.original_length} to {result.compressed_length}")

            # Compress message history
            messages = [
                {"role": "user", "message": "Hello, how are you?", "created_at": "2024-01-01"},
                {"role": "assistant", "message": "I'm doing well!", "created_at": "2024-01-01"},
            ]
            result = client.compress.compress(
                content=messages,
                include_metadata=True
            )

            # Async compression with webhook
            result = client.compress.compress(
                content="Long text...",
                webhook_url="https://example.com/webhook"
            )
            print(result.message)  # "Compression response will be sent to webhook"
            ```
        """
        compress_req = CompressRequest(
            content=content,
            strategy=strategy,
            include_metadata=include_metadata,
            webhook_url=webhook_url,
        )

        payload = compress_req.model_dump(exclude_none=True)
        print(payload)
        response = self._client.post("/compress", json_data=payload)
        return CompressResponse(**response)


class AsyncCompress:
    """Asynchronous Compress resource."""

    def __init__(self, client: AsyncBaseClient):
        """Initialize the async Compress resource.

        Args:
            client: Async base HTTP client instance
        """
        self._client = client

    async def compress(
        self,
        content: Union[str, List[Dict[str, Any]]],
        strategy: str = "ai_compress",
        include_metadata: bool = False,
        webhook_url: Optional[str] = None,
    ) -> CompressResponse:
        """Compress text content using AI asynchronously.

        Args:
            content: Content to compress (string or list of message objects)
            strategy: Compression strategy to use
            include_metadata: Whether to include metadata in compression
            webhook_url: Optional webhook URL for async results

        Returns:
            CompressResponse with compressed content

        Example:
            ```python
            result = await client.compress.compress(
                content="This is a very long text that needs to be compressed..."
            )
            print(result.content)
            ```
        """
        compress_req = CompressRequest(
            content=content,
            strategy=strategy,
            include_metadata=include_metadata,
            webhook_url=webhook_url,
        )

        payload = compress_req.model_dump(exclude_none=True)
        response = await self._client.post("/compress", json_data=payload)
        return CompressResponse(**response)
