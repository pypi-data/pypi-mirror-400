"""Executors for Mielto tools."""

from typing import Any, Dict, Optional

from mielto.client.mielto import Mielto
from mielto.tools.base import MieltoToolsConfig
from mielto.tools.definitions import get_tool_definitions


def create_executors(
    client: Mielto,
    config: Optional[MieltoToolsConfig] = None,
    tool_types: str = "both",
) -> Dict[str, Any]:
    """Create executors for all Mielto tools.

    Args:
        client: Mielto client instance
        config: Optional configuration for default values
        tool_types: Type of tools to include: "memory", "collection", or "both"

    Returns:
        Dictionary mapping tool names to executor functions
    """
    definitions = get_tool_definitions(tool_types)
    executors: Dict[str, Any] = {}

    if tool_types == "memory" or tool_types == "both":

        def search_memories_executor(args: Dict[str, Any]) -> Dict[str, Any]:
            """Execute searchMemories tool."""
            try:
                response = client.memories.search(
                    {
                        "query": args["query"],
                        "user_id": args.get("user_id") or (config.user_id if config else None),
                        "limit": args.get("limit", 10),
                        "retrieval_method": args.get("retrieval_method"),
                    }
                )
                return {
                    "success": True,
                    "memories": [
                        memory.model_dump() if hasattr(memory, "model_dump") else memory for memory in response.memories
                    ],
                    "total_results": response.total_results,
                    "query": response.query,
                    "retrieval_method": response.retrieval_method,
                }
            except Exception as error:
                return {
                    "success": False,
                    "error": str(error),
                }

        executors["searchMemories"] = search_memories_executor

        def add_memory_executor(args: Dict[str, Any]) -> Dict[str, Any]:
            """Execute addMemory tool."""
            try:
                user_id = args.get("user_id") or (config.user_id if config else None)
                if not user_id:
                    return {
                        "success": False,
                        "error": "user_id is required. Provide it in the request or in the config.",
                    }

                response = client.memories.create(
                    {
                        "user_id": user_id,
                        "memory": args["memory"],
                        "memory_type": args.get("memory_type"),
                        "topics": args.get("topics"),
                        "metadata": args.get("metadata"),
                    }
                )
                return {
                    "success": True,
                    "memory": response.model_dump() if hasattr(response, "model_dump") else response,
                }
            except Exception as error:
                return {
                    "success": False,
                    "error": str(error),
                }

        executors["addMemory"] = add_memory_executor

        def list_memories_executor(args: Dict[str, Any]) -> Dict[str, Any]:
            """Execute listMemories tool."""
            try:
                response = client.memories.list(
                    user_id=args.get("user_id") or (config.user_id if config else None),
                    limit=args.get("limit", 50),
                    cursor=args.get("cursor"),
                    sort_by=args.get("sort_by", "updated_at"),
                    sort_order=args.get("sort_order", "desc"),
                )
                return {
                    "success": True,
                    "memories": [
                        memory.model_dump() if hasattr(memory, "model_dump") else memory for memory in response.memories
                    ],
                    "total_count": response.total_count,
                    "has_more": response.has_more,
                    "next_cursor": response.next_cursor,
                }
            except Exception as error:
                return {
                    "success": False,
                    "error": str(error),
                }

        executors["listMemories"] = list_memories_executor

    if tool_types == "collection" or tool_types == "both":

        def search_collection_executor(args: Dict[str, Any]) -> Dict[str, Any]:
            """Execute searchCollection tool."""
            try:
                collection_id = args.get("collection_id") or (config.collection_id if config else None)
                if not collection_id:
                    return {
                        "success": False,
                        "error": "collectionId is required. Provide it in the request or in the config.",
                    }

                response = client.collections.search(
                    {
                        "query": args["query"],
                        "collection_id": collection_id,
                        "search_type": args.get("search_type"),
                        "max_results": args.get("max_results"),
                        "filters": args.get("filters") or {},
                    }
                )
                return {
                    "success": True,
                    "results": [
                        result.model_dump() if hasattr(result, "model_dump") else result for result in response.results
                    ],
                    "total_results": response.total_results,
                    "query": response.query,
                    "search_type": response.search_type,
                }
            except Exception as error:
                return {
                    "success": False,
                    "error": str(error),
                }

        executors["searchCollection"] = search_collection_executor

        def insert_to_collection_executor(args: Dict[str, Any]) -> Dict[str, Any]:
            """Execute insertToCollection tool."""
            try:
                collection_id = args.get("collection_id") or (config.collection_id if config else None)
                if not collection_id:
                    return {
                        "success": False,
                        "error": "collectionId is required. Provide it in the request or in the config.",
                    }

                if not args.get("content") and not args.get("urls"):
                    return {
                        "success": False,
                        "error": "Either content or urls must be provided.",
                    }

                response = client.collections.insert(
                    collection_id=collection_id,
                    content=args.get("content"),
                    urls=args.get("urls"),
                    label=args.get("label"),
                    description=args.get("description"),
                    metadata=args.get("metadata"),
                    ingest=args.get("ingest", True),
                )
                return {
                    "success": True,
                    "response": response.model_dump() if hasattr(response, "model_dump") else response,
                }
            except Exception as error:
                return {
                    "success": False,
                    "error": str(error),
                }

        executors["insertToCollection"] = insert_to_collection_executor

        def list_collections_executor(args: Dict[str, Any]) -> Dict[str, Any]:
            """Execute listCollections tool."""
            try:
                response = client.collections.list(
                    skip=args.get("skip", 0),
                    limit=args.get("limit", 100),
                    status=args.get("status"),
                    visibility=args.get("visibility"),
                    search=args.get("search"),
                    tags=args.get("tags"),
                )
                return {
                    "success": True,
                    "collections": [
                        coll.model_dump() if hasattr(coll, "model_dump") else coll for coll in response.data
                    ],
                    "total": response.total,
                }
            except Exception as error:
                return {
                    "success": False,
                    "error": str(error),
                }

        executors["listCollections"] = list_collections_executor

    # Always include searchAvailableTools
    def search_available_tools_executor(args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute searchAvailableTools tool."""
        try:
            available_tools = [
                {
                    "name": definition.name,
                    "description": definition.description,
                }
                for definition in definitions
                if definition.name != "searchAvailableTools"
            ]

            filtered_tools = available_tools
            if args.get("search_term"):
                search_term_lower = args["search_term"].lower()
                filtered_tools = [
                    tool
                    for tool in available_tools
                    if search_term_lower in tool["name"].lower() or search_term_lower in tool["description"].lower()
                ]

            return {
                "success": True,
                "tools": filtered_tools,
                "total": len(filtered_tools),
                "all_tools": [tool["name"] for tool in available_tools],
            }
        except Exception as error:
            return {
                "success": False,
                "error": str(error),
            }

    executors["searchAvailableTools"] = search_available_tools_executor

    return executors
