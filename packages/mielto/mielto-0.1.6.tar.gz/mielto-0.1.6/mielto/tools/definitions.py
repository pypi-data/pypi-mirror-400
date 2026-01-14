"""Tool definitions for Mielto tools using Pydantic models."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ToolDefinition:
    """Definition of a tool for OpenAI function calling."""

    def __init__(
        self,
        name: str,
        description: str,
        parameters_model: type[BaseModel],
        required: List[str],
    ):
        """Initialize tool definition.

        Args:
            name: Tool name
            description: Tool description
            parameters_model: Pydantic model for parameters
            required: List of required parameter names
        """
        self.name = name
        self.description = description
        self.parameters_model = parameters_model
        self.required = required

    def to_openai_function(self) -> Dict[str, Any]:
        """Convert to OpenAI function definition format.

        Returns:
            OpenAI function definition dictionary
        """
        schema = self.parameters_model.model_json_schema()
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": schema.get("properties", {}),
                "required": self.required,
            },
        }


# Memory Tools Definitions


class SearchMemoriesParams(BaseModel):
    """Parameters for searchMemories tool."""

    query: str = Field(description="Search query to find relevant memories")
    user_id: Optional[str] = Field(
        default=None, description="User ID to search memories for. If not provided, uses the configured userId."
    )
    limit: Optional[int] = Field(default=10, description="Maximum number of results to return")
    retrieval_method: Optional[str] = Field(default=None, description="Retrieval method to use for search")


search_memories_definition = ToolDefinition(
    name="searchMemories",
    description=(
        "Search (recall) memories/details/information about the user or other facts or entities. "
        "Run when explicitly asked or when context about user's past choices would be helpful."
    ),
    parameters_model=SearchMemoriesParams,
    required=["query"],
)


class AddMemoryParams(BaseModel):
    """Parameters for addMemory tool."""

    memory: str = Field(
        description="The text content of the memory to add. This should be a single sentence or a short paragraph."
    )
    user_id: Optional[str] = Field(
        default=None, description="User ID for the memory. If not provided, uses the configured userId."
    )
    memory_type: Optional[str] = Field(default=None, description="Type of memory (e.g., 'fact', 'preference', 'event')")
    topics: Optional[List[str]] = Field(default=None, description="Topics associated with this memory")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata for the memory")


add_memory_definition = ToolDefinition(
    name="addMemory",
    description=(
        "Add (remember) memories/details/information about the user or other facts or entities. "
        "Run when explicitly asked or when the user mentions any information generalizable beyond the context of the current conversation."
    ),
    parameters_model=AddMemoryParams,
    required=["memory"],
)


class ListMemoriesParams(BaseModel):
    """Parameters for listMemories tool."""

    user_id: Optional[str] = Field(
        default=None, description="User ID to list memories for. If not provided, uses the configured userId."
    )
    limit: Optional[int] = Field(default=50, description="Maximum number of memories to return")
    cursor: Optional[str] = Field(default=None, description="Cursor for pagination")
    sort_by: Optional[str] = Field(default="updated_at", description="Field to sort by")
    sort_order: Optional[str] = Field(default="desc", description="Sort order: 'asc' or 'desc'")


list_memories_definition = ToolDefinition(
    name="listMemories",
    description="List memories for a user. Useful for getting an overview of stored memories.",
    parameters_model=ListMemoriesParams,
    required=[],
)


# Collection Tools Definitions


class SearchCollectionParams(BaseModel):
    """Parameters for searchCollection tool."""

    query: str = Field(description="Search query to find relevant content")
    collection_id: Optional[str] = Field(
        default=None,
        description="Collection ID to search in. If not provided, uses the configured collectionId.",
    )
    search_type: Optional[str] = Field(default=None, description="Type of search: hybrid, vector, or keyword")
    max_results: Optional[int] = Field(default=None, description="Maximum number of results to return")
    min_score: Optional[float] = Field(default=None, description="Minimum relevance score threshold")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Additional filters for the search")
    metadata_filters: Optional[Dict[str, Any]] = Field(default=None, description="Metadata filters for the search")


search_collection_definition = ToolDefinition(
    name="searchCollection",
    description="Search within a collection for relevant content. Use this to find information stored in collections.",
    parameters_model=SearchCollectionParams,
    required=["query"],
)


class InsertToCollectionParams(BaseModel):
    """Parameters for insertToCollection tool."""

    collection_id: Optional[str] = Field(
        default=None,
        description="Collection ID to insert into. If not provided, uses the configured collectionId.",
    )
    content: Optional[str] = Field(default=None, description="Text content to insert")
    urls: Optional[List[str]] = Field(default=None, description="URLs to insert and process")
    label: Optional[str] = Field(default=None, description="Label for the content")
    description: Optional[str] = Field(default=None, description="Description of the content")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Metadata for the content")
    ingest: Optional[bool] = Field(default=True, description="Whether to ingest the content for search")


insert_to_collection_definition = ToolDefinition(
    name="insertToCollection",
    description="Insert content into a collection. Can insert text, files, or URLs.",
    parameters_model=InsertToCollectionParams,
    required=[],
)


class ListCollectionsParams(BaseModel):
    """Parameters for listCollections tool."""

    skip: Optional[int] = Field(default=0, description="Number of collections to skip")
    limit: Optional[int] = Field(default=100, description="Maximum number of collections to return")
    status: Optional[str] = Field(default=None, description="Filter by status")
    visibility: Optional[str] = Field(default=None, description="Filter by visibility")
    search: Optional[str] = Field(default=None, description="Search term to filter collections")
    tags: Optional[str] = Field(default=None, description="Filter by tags (comma-separated)")


list_collections_definition = ToolDefinition(
    name="listCollections",
    description="List available collections. Useful for discovering what collections are available.",
    parameters_model=ListCollectionsParams,
    required=[],
)


# Utility Tools Definitions


class SearchAvailableToolsParams(BaseModel):
    """Parameters for searchAvailableTools tool."""

    search_term: Optional[str] = Field(
        default=None, description="Optional search term to filter tools by name or description"
    )


search_available_tools_definition = ToolDefinition(
    name="searchAvailableTools",
    description=(
        "Search for and list available Mielto tools. "
        "Use this to discover what tools are available and their capabilities."
    ),
    parameters_model=SearchAvailableToolsParams,
    required=[],
)


def get_tool_definitions(tool_types: str = "both") -> List[ToolDefinition]:
    """Get all tool definitions by type.

    Args:
        tool_types: Type of tools to include: "memory", "collection", or "both"

    Returns:
        List of tool definitions
    """
    definitions: List[ToolDefinition] = []

    if tool_types == "memory" or tool_types == "both":
        definitions.extend(
            [
                search_memories_definition,
                add_memory_definition,
                list_memories_definition,
            ]
        )

    if tool_types == "collection" or tool_types == "both":
        definitions.extend(
            [
                search_collection_definition,
                insert_to_collection_definition,
                list_collections_definition,
            ]
        )

    # Always include searchAvailableTools
    definitions.append(search_available_tools_definition)

    return definitions
