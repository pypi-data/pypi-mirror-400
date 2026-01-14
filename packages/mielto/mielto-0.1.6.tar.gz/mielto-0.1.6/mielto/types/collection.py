"""Collection type definitions."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class CollectionStoreType(str, Enum):
    """Collection store types."""

    PGVECTOR = "pgvector"
    PINECONE = "pinecone"
    QDRANT = "qdrant"
    LANGCHAIN_PGVECTOR = "langchain_pgvector"


class CollectionStatus(str, Enum):
    """Collection statuses."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    DELETING = "deleting"
    ARCHIVED = "archived"


class SearchType(str, Enum):
    """Search types."""

    HYBRID = "hybrid"
    VECTOR = "vector"
    KEYWORD = "keyword"


class CollectionCreate(BaseModel):
    """Schema for creating a new collection."""

    name: str = Field(..., min_length=1, max_length=100, description="Collection name")
    description: Optional[str] = Field(None, max_length=255, description="Collection description")
    store_type: Optional[CollectionStoreType] = Field(
        CollectionStoreType.PGVECTOR, description="Storage type for the collection"
    )
    visibility: str = Field(default="private", description="Collection visibility (private/public)")
    tags: Optional[List[str]] = Field(None, description="Collection tags for organization")
    parent_id: Optional[str] = Field(None, description="Reference to parent collection")
    meta_data: Dict[str, Any] = Field(default_factory=dict, description="Collection metadata")
    settings: Dict[str, Any] = Field(default_factory=dict, description="Collection configuration settings")
    embedding: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Embedding configuration")


class CollectionUpdate(BaseModel):
    """Schema for updating a collection."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    visibility: Optional[str] = None
    tags: Optional[List[str]] = None
    parent_id: Optional[str] = None
    meta_data: Optional[Dict[str, Any]] = None
    settings: Optional[Dict[str, Any]] = None
    embedding: Optional[Dict[str, Any]] = None


class Collection(BaseModel):
    """Schema for collection response."""

    id: str = Field(..., description="Collection ID")
    name: str = Field(..., description="Collection name")
    description: Optional[str] = Field(None, description="Collection description")
    store_type: Optional[str] = Field(None, description="Storage type")
    visibility: str = Field(..., description="Collection visibility")
    status: str = Field(..., description="Collection status")
    tags: Optional[List[str]] = Field(None, description="Collection tags")
    parent_id: Optional[str] = Field(None, description="Parent collection ID")
    stats: Dict[str, Any] = Field(default_factory=dict, description="Collection statistics")
    meta_data: Dict[str, Any] = Field(default_factory=dict, description="Collection metadata")
    settings: Dict[str, Any] = Field(default_factory=dict, description="Collection settings")
    embedding: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Embedding configuration")
    workspace_id: str = Field(..., description="Workspace ID")
    created_by: Optional[str] = Field(None, description="Creator user ID")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")


class SearchResult(BaseModel):
    """Individual search result."""

    content: str = Field(..., description="The content text")
    score: float = Field(..., description="Relevance score")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    content_id: Optional[str] = Field(None, description="ID of the content")
    source: Optional[str] = Field(None, description="Source of the content")


class SearchRequest(BaseModel):
    """Request schema for knowledge search."""

    query: str = Field(..., description="Search query string")
    collection_id: str = Field(..., description="ID of the collection to search in")
    search_type: SearchType = Field(default=SearchType.HYBRID, description="Type of search to perform")
    max_results: int = Field(default=10, ge=1, le=100, description="Maximum number of results to return")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Additional filters to apply")


class SearchResponse(BaseModel):
    """Response schema for knowledge search."""

    results: List[SearchResult] = Field(..., description="List of search results")
    total_results: int = Field(..., description="Total number of results found")
    query: str = Field(..., description="Original search query")
    search_type: SearchType = Field(..., description="Type of search performed")
    collection_id: str = Field(..., description="Collection that was searched")
    execution_time_ms: Optional[float] = Field(None, description="Search execution time in milliseconds")


class Chunk(BaseModel):
    """Chunk/Document with embedding."""

    id: str = Field(..., description="Chunk ID")
    content: str = Field(..., description="The content text")
    embedding: Optional[List[float]] = Field(None, description="Vector embedding")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ChunksResponse(BaseModel):
    """Response schema for listing chunks with cursor-based pagination."""

    chunks: List[Chunk] = Field(..., description="List of chunks")
    total: Optional[int] = Field(None, description="Total number of chunks (deprecated, use has_more)")
    next_cursor: Optional[str] = Field(None, description="Cursor for next page")
    has_more: bool = Field(default=False, description="Whether there are more chunks available")
