"""Type definitions for Mielto API."""

from mielto.types.chat import (
    ChatCompletion,
    ChatCompletionChoice,
    ChatCompletionChunk,
    ChatCompletionChunkChoice,
    ChatCompletionRequest,
    ChatCompletionUsage,
    ChatDelta,
    ChatMessage,
    FunctionDefinition,
    ToolDefinition,
)
from mielto.types.collection import (
    Chunk,
    ChunksResponse,
    Collection,
    CollectionCreate,
    CollectionUpdate,
    SearchRequest,
    SearchResponse,
    SearchResult,
)
from mielto.types.compress import CompressRequest, CompressResponse
from mielto.types.memory import (
    Memory,
    MemoryChunksResponse,
    MemoryCreate,
    MemoryListResponse,
    MemoryReplace,
    MemorySearchRequest,
    MemorySearchResponse,
    MemoryUpdate,
    MemoryWithEmbedding,
)
from mielto.types.upload import FileUpload, UploadRequest, UploadResponse

__all__ = [
    # Chat types
    "ChatMessage",
    "ChatDelta",
    "ChatCompletion",
    "ChatCompletionChunk",
    "ChatCompletionChoice",
    "ChatCompletionChunkChoice",
    "ChatCompletionRequest",
    "ChatCompletionUsage",
    "FunctionDefinition",
    "ToolDefinition",
    # Memory types
    "Memory",
    "MemoryCreate",
    "MemoryUpdate",
    "MemoryReplace",
    "MemorySearchRequest",
    "MemorySearchResponse",
    "MemoryListResponse",
    "MemoryWithEmbedding",
    "MemoryChunksResponse",
    # Collection types
    "Collection",
    "CollectionCreate",
    "CollectionUpdate",
    "SearchRequest",
    "SearchResponse",
    "SearchResult",
    "Chunk",
    "ChunksResponse",
    # Compress types
    "CompressRequest",
    "CompressResponse",
    # Upload types
    "UploadRequest",
    "UploadResponse",
    "FileUpload",
]
