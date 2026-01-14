"""Main MieltoTools class for managing Mielto tools."""

import json
from typing import Any, Dict, List, Optional

from mielto.client.mielto import Mielto
from mielto.tools.base import MieltoToolsConfig, ToolType, create_mielto_client
from mielto.tools.definitions import ToolDefinition, get_tool_definitions
from mielto.tools.executors import create_executors


class MieltoTools:
    """MieltoTools class for managing Mielto tools for OpenAI function calling."""

    def __init__(
        self,
        config: Optional[MieltoToolsConfig] = None,
        options: Optional[Dict[str, Any]] = None,
        client: Optional[Mielto] = None,
    ):
        """Initialize MieltoTools.

        Args:
            config: Mielto tools configuration
            options: Optional configuration dict with 'tool_types' key
            client: Optional existing Mielto client instance

        Raises:
            ValueError: If neither config nor client is provided
        """
        self.tool_types: ToolType = (options or {}).get("tool_types", "both")

        if client:
            self.client = client
        elif config:
            self.client = create_mielto_client(config)
        else:
            raise ValueError("config or client is required")

        self.definitions: List[ToolDefinition] = get_tool_definitions(self.tool_types)
        self.executors: Dict[str, Any] = create_executors(self.client, config, self.tool_types)

    def get_openai_functions(self) -> List[Dict[str, Any]]:
        """Get OpenAI function definitions.

        Returns:
            List of OpenAI function definitions
        """
        return [definition.to_openai_function() for definition in self.definitions]

    def get_openai_tools(self) -> List[Dict[str, Any]]:
        """Get OpenAI tools format (with type wrapper).

        Returns:
            List of OpenAI tools in the format expected by OpenAI API
        """
        functions = self.get_openai_functions()
        return [{"type": "function", "function": fn} for fn in functions]

    def get_executors(self) -> Dict[str, Any]:
        """Get executors for OpenAI function calling.

        Returns:
            Dictionary mapping function names to executor functions
        """
        return self.executors

    def get_tool_names(self) -> List[str]:
        """Get available tool names.

        Returns:
            List of tool names
        """
        return [definition.name for definition in self.definitions]

    def get_definitions(self) -> List[ToolDefinition]:
        """Get tool definitions.

        Returns:
            List of tool definitions
        """
        return self.definitions

    def execute_tool_calls(self, tool_calls: Optional[List[Any]] = None) -> List[Dict[str, Any]]:
        """Execute tool calls from an OpenAI response.

        Args:
            tool_calls: List of tool calls from OpenAI response. Can be:
                - List of tool call objects (from OpenAI SDK)
                - List of dictionaries with tool call data
                - None (returns empty list)

        Returns:
            List of tool result messages in the format expected by OpenAI API

        Example:
            ```python
            completion = openai.chat.completions.create(...)
            tool_results = tools.execute_tool_calls(
                tool_calls=completion.choices[0].message.tool_calls
            )
            messages.extend(tool_results)
            ```
        """
        if not tool_calls:
            return []

        tool_results = []

        for tool_call in tool_calls:
            # Handle both OpenAI SDK objects and dictionaries
            if hasattr(tool_call, "type"):
                tool_call_type = tool_call.type
                tool_call_id = tool_call.id
                function_name = tool_call.function.name
                function_arguments = tool_call.function.arguments
            elif isinstance(tool_call, dict):
                tool_call_type = tool_call.get("type")
                tool_call_id = tool_call.get("id")
                function_data = tool_call.get("function", {})
                function_name = function_data.get("name") if isinstance(function_data, dict) else None
                function_arguments = function_data.get("arguments") if isinstance(function_data, dict) else None
            else:
                continue

            if tool_call_type != "function":
                continue

            if not function_name or function_arguments is None:
                continue

            # Parse arguments
            try:
                if isinstance(function_arguments, str):
                    args = json.loads(function_arguments)
                else:
                    args = function_arguments
            except (json.JSONDecodeError, TypeError):
                args = {}

            # Execute the tool
            if function_name not in self.executors:
                result = {
                    "success": False,
                    "error": f"Unknown tool: {function_name}",
                }
            else:
                try:
                    result = self.executors[function_name](args)
                except Exception as e:
                    result = {
                        "success": False,
                        "error": str(e),
                    }

            # Format as tool message
            tool_results.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "content": json.dumps(result),
                }
            )

        return tool_results

    def close(self) -> None:
        """Close the underlying Mielto client."""
        self.client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
