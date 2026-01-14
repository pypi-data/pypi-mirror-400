"""Synchronous Mielto API client."""

from mielto.client.base import BaseClient
from mielto.resources.chat import Chat
from mielto.resources.collections import Collections
from mielto.resources.compress import Compress
from mielto.resources.memories import Memories


class Mielto:
    """Synchronous client for interacting with the Mielto API.

    This is the main entry point for using the Mielto Python SDK in a synchronous context.

    Example:
        ```python
        from mielto import Mielto

        # Initialize the client
        client = Mielto(api_key="your-api-key")

        # Use memories
        memory = client.memories.create(
            MemoryCreate(
                user_id="user_123",
                memory="User prefers dark mode"
            )
        )

        # Use collections
        collection = client.collections.create(
            CollectionCreate(name="My Docs")
        )

        # Search in collection
        results = client.collections.search(
            SearchRequest(
                query="AI research",
                collection_id=collection.id
            )
        )

        # Compress text
        compressed = client.compress.compress(
            content="Long text to compress..."
        )

        # Close the client when done
        client.close()
        ```

    Or use as a context manager:
        ```python
        with Mielto(api_key="your-api-key") as client:
            memory = client.memories.create(...)
        ```
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.mielto.com/api/v1",
        timeout: float = 30.0,
        max_retries: int = 2,
    ):
        """Initialize the Mielto client.

        Args:
            api_key: Your Mielto API key
            base_url: Base URL for the Mielto API (defaults to production)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
        """
        self._client = BaseClient(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
        )

        # Initialize resources
        self.memories = Memories(self._client)
        self.collections = Collections(self._client)
        self.compress = Compress(self._client)
        self.chat = Chat(self._client)

    def close(self) -> None:
        """Close the HTTP client and clean up resources."""
        self._client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
