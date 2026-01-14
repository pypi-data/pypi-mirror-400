"""Memory type definitions."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class MemoryCreate(BaseModel):
    """Schema for creating a new memory."""

    user_id: str = Field(..., description="The user ID who owns the memory")
    memory: str = Field(..., description="The memory content to store")
    memory_type: Optional[str] = Field(default="user", description="Type of memory")
    topics: Optional[List[str]] = Field(None, description="Topics associated with the memory")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class MemoryUpdate(BaseModel):
    """Schema for updating an existing memory."""

    user_id: Optional[str] = Field(None, description="The user ID who owns the memory")
    memory: Optional[str] = Field(None, description="Updated memory content")
    topics: Optional[List[str]] = Field(None, description="Updated topics")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Updated metadata")


class MemoryReplace(BaseModel):
    """Schema for replacing a memory."""

    user_id: Optional[str] = Field(None, description="The user ID who owns the memory")
    memory: str = Field(..., description="The new memory content")
    topics: Optional[List[str]] = Field(None, description="New topics")
    metadata: Optional[Dict[str, Any]] = Field(None, description="New metadata")


class Memory(BaseModel):
    """Schema for memory response."""

    memory_id: str = Field(..., description="Unique identifier for the memory")
    user_id: str = Field(..., description="User ID who owns the memory")
    memory: str = Field(..., description="The memory content")
    topics: Optional[List[str]] = Field(None, description="Topics associated with the memory")
    created_at: Optional[datetime] = Field(None, description="When the memory was created")
    updated_at: Optional[datetime] = Field(None, description="When the memory was last updated")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class MemorySearchRequest(BaseModel):
    """Schema for memory search request."""

    query: str = Field(..., description="Search query for memories")
    user_id: Optional[str] = Field(None, description="User ID")
    limit: Optional[int] = Field(10, ge=1, le=100, description="Maximum number of memories to return")
    retrieval_method: Optional[str] = Field("agentic", description="Retrieval method to use")


class MemorySearchResponse(BaseModel):
    """Schema for memory search response."""

    memories: List[Memory] = Field(..., description="List of matching memories")
    total_results: int = Field(..., description="Total number of memories found")
    query: str = Field(..., description="The search query used")
    retrieval_method: str = Field(..., description="The retrieval method used")


class MemoryListResponse(BaseModel):
    """Schema for listing memories with cursor-based pagination."""

    memories: List[Memory] = Field(..., description="List of memories")
    total_count: int = Field(..., description="Total number of memories returned")
    next_cursor: Optional[str] = Field(None, description="Cursor for fetching the next page")
    has_more: bool = Field(False, description="Whether there are more memories to fetch")


class MemoryFromMessagesRequest(BaseModel):
    """Schema for creating memories from messages."""

    messages: List[Dict[str, Any]] = Field(..., description="List of conversation messages")
    user_id: str = Field(..., description="User ID who owns the memories")
    agent_id: Optional[str] = Field(None, description="Agent ID (optional)")
    team_id: Optional[str] = Field(None, description="Team ID (optional)")


class MemoryFromMessagesResult(BaseModel):
    """Schema for the result object in from_messages response."""

    memories_created: int = Field(..., description="Number of memories created")
    memory_ids: List[str] = Field(..., description="IDs of created memories")


class MemoryFromMessagesResponse(BaseModel):
    """Schema for memories creation from messages response."""

    message: str = Field(..., description="Success message")
    result: Optional[MemoryFromMessagesResult] = Field(None, description="Result details")


class MemoryWithEmbedding(BaseModel):
    """Memory chunk with its vector embedding from the chunks API."""

    id: str = Field(..., description="Chunk ID")
    content_id: Optional[str] = Field(None, description="Memory/content ID")
    collection_id: Optional[str] = Field(None, description="Collection ID")
    workspace_id: Optional[str] = Field(None, description="Workspace ID")
    name: Optional[str] = Field(None, description="Chunk name")
    content: str = Field(..., description="Chunk content")
    embedding: Optional[List[float]] = Field(None, description="Vector embedding")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    created_at: Optional[datetime] = Field(None, description="When the chunk was created")


class MemoryChunksResponse(BaseModel):
    """Response schema for listing memory chunks with embeddings using cursor-based pagination."""

    chunks: List[MemoryWithEmbedding] = Field(..., description="List of memory chunks")
    next_cursor: Optional[str] = Field(None, description="Cursor for next page")
    has_more: bool = Field(default=False, description="Whether there are more memory chunks available")
