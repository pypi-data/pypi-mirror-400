"""OpenAI provider for Mielto tools."""

from typing import Any, Dict, List

from mielto.tools.mielto_tools import MieltoTools


def get_openai_functions(client: MieltoTools) -> List[Dict[str, Any]]:
    """Get OpenAI function definitions for Mielto tools.

    Args:
        client: MieltoTools instance

    Returns:
        List of OpenAI function definitions
    """
    return client.get_openai_functions()


def get_executors(client: MieltoTools) -> Dict[str, Any]:
    """Get function executors for OpenAI function calling.

    Args:
        client: MieltoTools instance

    Returns:
        Dictionary mapping function names to executor functions
    """
    return client.get_executors()


def get_openai_tools(client: MieltoTools) -> List[Dict[str, Any]]:
    """Get OpenAI tools format (with type wrapper).

    Args:
        client: MieltoTools instance

    Returns:
        List of OpenAI tools in the format expected by OpenAI API
    """
    return client.get_openai_tools()
