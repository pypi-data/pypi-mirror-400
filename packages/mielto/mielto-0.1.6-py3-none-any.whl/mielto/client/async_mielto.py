"""Asynchronous Mielto API client."""

from mielto.client.base import AsyncBaseClient
from mielto.resources.chat import AsyncChat
from mielto.resources.collections import AsyncCollections
from mielto.resources.compress import AsyncCompress
from mielto.resources.memories import AsyncMemories


class AsyncMielto:
    """Asynchronous client for interacting with the Mielto API.

    This is the main entry point for using the Mielto Python SDK in an asynchronous context.

    Example:
        ```python
        import asyncio
        from mielto import AsyncMielto

        async def main():
            # Initialize the client
            client = AsyncMielto(api_key="your-api-key")

            # Use memories
            memory = await client.memories.create(
                MemoryCreate(
                    user_id="user_123",
                    memory="User prefers dark mode"
                )
            )

            # Use collections
            collection = await client.collections.create(
                CollectionCreate(name="My Docs")
            )

            # Search in collection
            results = await client.collections.search(
                SearchRequest(
                    query="AI research",
                    collection_id=collection.id
                )
            )

            # Compress text
            compressed = await client.compress.compress(
                content="Long text to compress..."
            )

            # Close the client when done
            await client.close()

        asyncio.run(main())
        ```

    Or use as an async context manager:
        ```python
        async with AsyncMielto(api_key="your-api-key") as client:
            memory = await client.memories.create(...)
        ```
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.mielto.com/api/v1",
        timeout: float = 30.0,
        max_retries: int = 2,
    ):
        """Initialize the async Mielto client.

        Args:
            api_key: Your Mielto API key
            base_url: Base URL for the Mielto API (defaults to production)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
        """
        self._client = AsyncBaseClient(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
        )

        # Initialize resources
        self.memories = AsyncMemories(self._client)
        self.collections = AsyncCollections(self._client)
        self.compress = AsyncCompress(self._client)
        self.chat = AsyncChat(self._client)

    async def close(self) -> None:
        """Close the HTTP client and clean up resources."""
        await self._client.close()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
