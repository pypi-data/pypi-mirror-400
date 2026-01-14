"""Base configuration and utilities for Mielto tools."""

from typing import Optional

from mielto.client.mielto import Mielto


class MieltoToolsConfig:
    """Configuration for Mielto tools."""

    def __init__(
        self,
        api_key: str,
        user_id: Optional[str] = None,
        collection_id: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
    ):
        """Initialize Mielto tools configuration.

        Args:
            api_key: Mielto API key
            user_id: User ID for memory operations
            collection_id: Collection ID for collection operations
            base_url: Base URL for the Mielto API
            timeout: Timeout for API requests in seconds
            max_retries: Maximum number of retries
        """
        self.api_key = api_key
        self.user_id = user_id
        self.collection_id = collection_id
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries


ToolType = str  # "memory" | "collection" | "both"


def create_mielto_client(config: MieltoToolsConfig) -> Mielto:
    """Create a Mielto client instance from configuration.

    Args:
        config: Mielto tools configuration

    Returns:
        Mielto client instance
    """
    client_kwargs = {
        "api_key": config.api_key,
    }
    if config.base_url:
        client_kwargs["base_url"] = config.base_url
    if config.timeout:
        client_kwargs["timeout"] = config.timeout
    if config.max_retries:
        client_kwargs["max_retries"] = config.max_retries

    return Mielto(**client_kwargs)
