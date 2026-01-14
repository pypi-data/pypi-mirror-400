"""Memory resource for interacting with the Mielto Memory API."""

from typing import Any, Dict, List, Optional, Union

from tqdm import tqdm

from mielto.client.base import AsyncBaseClient, BaseClient
from mielto.internals.vectors.base import VectorDB
from mielto.internals.vectors.enum import VectorStore
from mielto.types.memory import (
    Memory,
    MemoryChunksResponse,
    MemoryCreate,
    MemoryFromMessagesRequest,
    MemoryFromMessagesResponse,
    MemoryListResponse,
    MemoryReplace,
    MemorySearchRequest,
    MemorySearchResponse,
    MemoryUpdate,
)


class Memories:
    """Synchronous Memory resource."""

    def __init__(self, client: BaseClient):
        """Initialize the Memory resource.

        Args:
            client: Base HTTP client instance
        """
        self._client = client

    def create(self, memory_data: Union[MemoryCreate, dict]) -> Memory:
        """Create a new memory.

        Args:
            memory_data: Memory data to create

        Returns:
            Created memory

        Example:
            ```python
            memory = client.memories.create(
                MemoryCreate(
                    user_id="user_123",
                    memory="User prefers dark mode",
                    topics=["preferences", "ui"]
                )
            )
            ```
        """
        if isinstance(memory_data, MemoryCreate):
            payload = memory_data.model_dump(exclude_none=True)
        else:
            payload = memory_data

        response = self._client.post("/memories", json_data=payload)
        return Memory(**response["memory"])

    def get(self, memory_id: str, user_id: Optional[str] = None) -> Memory:
        """Get a specific memory by ID.

        Args:
            memory_id: Memory ID
            user_id: Optional user ID filter

        Returns:
            Memory object

        Example:
            ```python
            memory = client.memories.get("mem_123")
            ```
        """
        params = {}
        if user_id:
            params["user_id"] = user_id

        response = self._client.get(f"/memories/{memory_id}", params=params)
        return Memory(**response)

    def list(
        self,
        user_id: Optional[str] = None,
        cursor: Optional[str] = None,
        limit: int = 50,
        sort_by: str = "updated_at",
        sort_order: str = "desc",
    ) -> MemoryListResponse:
        """List memories with pagination.

        Args:
            user_id: Optional user ID to filter memories
            cursor: Cursor for pagination
            limit: Number of memories to return (1-100)
            sort_by: Field to sort by
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            MemoryListResponse with memories and pagination info

        Example:
            ```python
            result = client.memories.list(user_id="user_123", limit=20)
            for memory in result.memories:
                print(memory.memory)

            # Get next page
            if result.has_more:
                next_page = client.memories.list(
                    user_id="user_123",
                    cursor=result.next_cursor
                )
            ```
        """
        params = {
            "limit": limit,
            "sort_by": sort_by,
            "sort_order": sort_order,
        }
        if user_id:
            params["user_id"] = user_id
        if cursor:
            params["cursor"] = cursor

        response = self._client.get("/memories", params=params)
        return MemoryListResponse(**response)

    def search(self, search_request: Union[MemorySearchRequest, dict]) -> MemorySearchResponse:
        """Search memories.

        Args:
            search_request: Search parameters

        Returns:
            MemorySearchResponse with matching memories

        Example:
            ```python
            results = client.memories.search(
                MemorySearchRequest(
                    query="dark mode preferences",
                    user_id="user_123",
                    limit=10
                )
            )
            for memory in results.memories:
                print(f"{memory.memory} (score: {memory.score})")
            ```
        """
        if isinstance(search_request, MemorySearchRequest):
            payload = search_request.model_dump(exclude_none=True)
        else:
            payload = search_request

        response = self._client.post("/memories/search", json_data=payload)
        return MemorySearchResponse(**response)

    def update(self, memory_id: str, memory_data: Union[MemoryUpdate, dict]) -> Memory:
        """Update an existing memory.

        Args:
            memory_id: Memory ID
            memory_data: Updated memory data

        Returns:
            Updated memory

        Example:
            ```python
            updated = client.memories.update(
                "mem_123",
                MemoryUpdate(
                    memory="User prefers light mode now",
                    topics=["preferences", "ui", "updated"]
                )
            )
            ```
        """
        if isinstance(memory_data, MemoryUpdate):
            payload = memory_data.model_dump(exclude_none=True)
        else:
            payload = memory_data

        response = self._client.put(f"/memories/{memory_id}", json_data=payload)
        return Memory(**response["memory"])

    def replace(self, memory_id: str, memory_data: Union[MemoryReplace, dict]) -> dict:
        """Replace an existing memory completely.

        Args:
            memory_id: Memory ID
            memory_data: New memory data

        Returns:
            Dict with old and new memory

        Example:
            ```python
            result = client.memories.replace(
                "mem_123",
                MemoryReplace(
                    memory="Completely new memory content",
                    topics=["new"]
                )
            )
            ```
        """
        if isinstance(memory_data, MemoryReplace):
            payload = memory_data.model_dump(exclude_none=True)
        else:
            payload = memory_data

        return self._client.post(f"/memories/{memory_id}/replace", json_data=payload)

    def delete(self, memory_id: str, user_id: Optional[str] = None) -> dict:
        """Delete a memory.

        Args:
            memory_id: Memory ID
            user_id: Optional user ID

        Returns:
            Deletion confirmation

        Example:
            ```python
            result = client.memories.delete("mem_123")
            print(result["message"])
            ```
        """
        params = {}
        if user_id:
            params["user_id"] = user_id

        endpoint = f"/memories/{memory_id}"
        if params:
            from urllib.parse import urlencode

            endpoint += f"?{urlencode(params)}"

        return self._client.delete(endpoint)

    def from_messages(
        self,
        messages: List[dict],
        user_id: str,
        agent_id: Optional[str] = None,
        team_id: Optional[str] = None,
    ) -> MemoryFromMessagesResponse:
        """Create memories from a list of conversation messages.

        This endpoint analyzes a conversation and extracts meaningful memories
        that can be stored and retrieved later for context in future interactions.

        Args:
            messages: List of message objects with 'role' and 'content' keys
            user_id: User ID to associate with the memories
            agent_id: Optional agent ID
            team_id: Optional team ID

        Returns:
            MemoryFromMessagesResponse with result and success message

        Example:
            ```python
            messages = [
                {"role": "user", "content": "I prefer dark mode"},
                {"role": "assistant", "content": "I'll remember that"},
                {"role": "user", "content": "I work in tech"}
            ]
            response = client.memories.from_messages(
                messages=messages,
                user_id="user_123",
                agent_id="agent_456"
            )
            print(response.message)
            ```
        """
        request_data = MemoryFromMessagesRequest(
            messages=messages,
            user_id=user_id,
            agent_id=agent_id,
            team_id=team_id,
        )

        payload = request_data.model_dump(exclude_none=True)
        response = self._client.post("/memories/from_messages", json_data=payload)

        # Handle response - API may return memories in 'result' field
        if "result" in response and isinstance(response["result"], list):
            response["memories"] = response.pop("result")

        return MemoryFromMessagesResponse(**response)

    def get_chunks(
        self,
        user_id: Optional[str] = None,
        limit: int = 100,
        cursor: Optional[str] = None,
        include_embedding: bool = False,
    ) -> MemoryChunksResponse:
        """Get memory chunks with their embeddings.

        This method uses cursor-based pagination for efficient traversal.

        Args:
            user_id: Filter by user ID (required)
            limit: Maximum number of chunks to return (default: 100, max: 100)
            cursor: Pagination cursor from previous response (use next_cursor)
            include_embedding: Whether to include vector embeddings

        Returns:
            MemoryChunksResponse with memory chunks data, next_cursor, and has_more

        Example:
            ```python
            # Get first page of memory chunks
            response = client.memories.get_chunks(
                user_id="user_123",
                limit=100,
                include_embedding=True
            )
            print(f"Retrieved {len(response.memories)} memories")

            # Get next page using cursor
            if response.has_more:
                next_response = client.memories.get_chunks(
                    user_id="user_123",
                    cursor=response.next_cursor,
                    limit=100
                )

            # Iterate through all memory chunks
            cursor = None
            while True:
                response = client.memories.get_chunks(
                    user_id="user_123",
                    limit=100,
                    cursor=cursor,
                    include_embedding=True
                )
                # Process response.chunks
                if not response.has_more:
                    break
                cursor = response.next_cursor
            ```
        """
        params = {
            "limit": limit,
            "include_embedding": include_embedding,
        }
        if user_id:
            params["user_id"] = user_id
        if cursor:
            params["cursor"] = cursor

        response = self._client.get("/memories/chunks", params=params)
        return MemoryChunksResponse(**response)

    def load(
        self,
        user_id: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        vector_store: VectorStore = VectorStore.FAISS,
        path: Optional[str] = None,
        distance_strategy: str = "cosine",
        batch_size: int = 1000,
        show_progress: bool = True,
        embedder: Optional[Any] = None,
        re_embed: bool = False,
    ):
        """Load memories into a local vector database.

        Fetches memories (optionally filtered) and stores them in a local
        vector database for offline search.

        Args:
            user_id: Filter by user ID (optional)
            filters: Optional filters (e.g., {"topics": ["work"]})
            vector_store: Vector database to use - currently only "faiss" is supported
            path: Path to store local database (default: /tmp/{vector_store}/memories_{user_id})
            distance_strategy: Distance metric - "cosine", "euclidean", or "inner_product"
            batch_size: Number of memories to fetch per batch
            show_progress: Whether to show progress bar
            embedder: Optional embedder to re-embed content locally. Must implement get_embedding(text: str) -> List[float]
            re_embed: If True and embedder is provided, re-embed all content using the local embedder instead of API embeddings

        Returns:
            Local vector database instance (FAISS)

        Example:
            ```python
            # Load all memories for a user (using API embeddings)
            vector_db = client.memories.load(
                user_id="user_123",
                path="./my_memories",
                distance_strategy="cosine"
            )

            # Load with re-embedding using local embedder
            embedder = MyEmbedder()
            vector_db = client.memories.load(
                user_id="user_123",
                path="./my_memories",
                embedder=embedder,
                re_embed=True  # Re-embed with local model
            )
            ```
        """
        if vector_store.value != "faiss":
            raise ValueError(f"Unsupported vector store: {vector_store.value}. Currently only 'faiss' is supported.")

        # Validate embedder if re_embed is True
        if re_embed and not embedder:
            raise ValueError("embedder must be provided when re_embed=True")

        if embedder:
            from mielto.internals.embedder import is_embedder

            if not is_embedder(embedder):
                raise ValueError(
                    "embedder must implement get_embedding(text: str) -> List[float] method and dimensions property"
                )

        # Lazy import to avoid requiring faiss if not using local vectors
        from mielto.internals.vectors.faiss import FAISS

        # Use embedder dimensions if re-embedding, otherwise use default API dimensions
        if re_embed and embedder:
            embedding_dims = embedder.dimensions
        else:
            embedding_dims = 1536  # Default to OpenAI dimensions

        # Initialize FAISS
        suffix = f"_{user_id}" if user_id else ""
        if path is None:
            path = f"/tmp/{vector_store.value}/memories{suffix}"

        faiss_db = FAISS(
            collection_name=f"memories{suffix}",
            path=path,
            distance_strategy=distance_strategy,
            embedding_model_dims=embedding_dims,
        )

        # Fetch all memories in batches using cursor-based pagination
        cursor = None
        total_loaded = 0

        # Create progress bar if requested
        pbar = None
        if show_progress:
            pbar = tqdm(desc="Loading memories", unit="memory")

        while True:
            # Fetch batch of memory chunks with embeddings
            chunks_response = self.get_chunks(
                user_id=user_id,
                limit=min(batch_size, 100),  # API max limit is 100
                cursor=cursor,
                include_embedding=True,
            )

            if not chunks_response.chunks:
                break

            # Prepare data for FAISS
            vectors = []
            payloads = []
            ids = []

            for memory in chunks_response.chunks:
                # Get content and id from the chunk
                content = memory.content
                chunk_id = memory.id

                # Skip if no content or id
                if not content or not chunk_id:
                    continue

                # Extract user_id from metadata if available
                user_id = memory.metadata.get("user_id", "") if memory.metadata else ""

                # Re-embed using local embedder if requested
                if re_embed and embedder:
                    try:
                        embedding = embedder.get_embedding(content)
                        vectors.append(embedding)
                        payloads.append(
                            {
                                "content": content,
                                "metadata": {
                                    "user_id": user_id,
                                    "content_id": memory.content_id or "",
                                    **(memory.metadata or {}),
                                },
                            }
                        )
                        ids.append(chunk_id)
                    except Exception as e:
                        # Log error but continue processing
                        if show_progress:
                            tqdm.write(f"Warning: Failed to embed chunk {chunk_id}: {e}")
                        continue
                # Use API embeddings
                elif memory.embedding:
                    vectors.append(memory.embedding)
                    payloads.append(
                        {
                            "content": content,
                            "metadata": {
                                "user_id": user_id,
                                "content_id": memory.content_id or "",
                                **(memory.metadata or {}),
                            },
                        }
                    )
                    ids.append(chunk_id)

            # Insert into FAISS
            if vectors:
                faiss_db.insert(vectors=vectors, payloads=payloads, ids=ids)
                total_loaded += len(vectors)

            if pbar is not None:
                pbar.update(len(chunks_response.chunks))

            # Check if there are more chunks
            if not chunks_response.has_more:
                break

            cursor = chunks_response.next_cursor

        if pbar is not None:
            pbar.close()

        return faiss_db

    def query(
        self,
        vector_db: VectorDB,
        query_text: Optional[str] = None,
        query_embedding: Optional[List[float]] = None,
        embedder: Optional[Any] = None,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Query a local vector database (offline search).

        Use this method to search in locally loaded memories without making API calls.
        For remote API searches, use the `search()` method instead.

        Args:
            vector_db: Vector database instance (from `load()`)
            query_text: Query text (requires embedder to be provided)
            query_embedding: Pre-computed query vector embedding
            embedder: Embedder to use for generating embedding from query_text
            limit: Maximum number of results to return
            filters: Optional metadata filters to apply

        Returns:
            List of search results with id, score, content, and metadata

        Example:
            ```python
            # Load memories locally
            vector_db = client.memories.load(user_id="user_123")

            # Option 1: Query with text and embedder
            results = client.memories.query(
                vector_db=vector_db,
                query_text="What are my work preferences?",
                embedder=my_embedder,
                limit=5
            )

            # Option 2: Query with pre-computed embedding
            query_embedding = my_embedder.get_embedding("What are my work preferences?")
            results = client.memories.query(
                vector_db=vector_db,
                query_embedding=query_embedding,
                limit=5,
                filters={"topics": ["work"]}
            )

            for result in results:
                print(f"{result['score']:.4f}: {result['content']}")
            ```
        """
        if not vector_db:
            raise ValueError("vector_db is required. Load memories first using load()")

        # Generate embedding from text if provided
        if query_text is not None:
            if not embedder:
                raise ValueError("embedder is required when using query_text")
            from mielto.internals.embedder import is_embedder

            if not is_embedder(embedder):
                raise ValueError(
                    "embedder must implement get_embedding(text: str) -> List[float] method and dimensions property"
                )
            query_embedding = embedder.get_embedding(query_text)

        # Validate query_embedding is provided
        if not query_embedding:
            raise ValueError("Either query_text with embedder or query_embedding must be provided")

        # Search using the local vector database
        search_results = vector_db.search(query="", vectors=[query_embedding], limit=limit, filters=filters)

        # Format results
        results = []
        for result in search_results:
            results.append(
                {
                    "id": result.id,
                    "score": result.score,
                    "content": result.payload.get("content", ""),
                    "metadata": result.payload.get("metadata", {}),
                }
            )
        return results


class AsyncMemories:
    """Asynchronous Memory resource."""

    def __init__(self, client: AsyncBaseClient):
        """Initialize the async Memory resource.

        Args:
            client: Async base HTTP client instance
        """
        self._client = client

    async def create(self, memory_data: Union[MemoryCreate, dict]) -> Memory:
        """Create a new memory asynchronously."""
        if isinstance(memory_data, MemoryCreate):
            payload = memory_data.model_dump(exclude_none=True)
        else:
            payload = memory_data

        response = await self._client.post("/memories", json_data=payload)
        return Memory(**response["memory"])

    async def get(self, memory_id: str, user_id: Optional[str] = None) -> Memory:
        """Get a specific memory by ID asynchronously."""
        params = {}
        if user_id:
            params["user_id"] = user_id

        response = await self._client.get(f"/memories/{memory_id}", params=params)
        return Memory(**response)

    async def list(
        self,
        user_id: Optional[str] = None,
        cursor: Optional[str] = None,
        limit: int = 50,
        sort_by: str = "updated_at",
        sort_order: str = "desc",
    ) -> MemoryListResponse:
        """List memories with pagination asynchronously."""
        params = {
            "limit": limit,
            "sort_by": sort_by,
            "sort_order": sort_order,
        }
        if user_id:
            params["user_id"] = user_id
        if cursor:
            params["cursor"] = cursor

        response = await self._client.get("/memories", params=params)
        return MemoryListResponse(**response)

    async def search(self, search_request: Union[MemorySearchRequest, dict]) -> MemorySearchResponse:
        """Search memories asynchronously."""
        if isinstance(search_request, MemorySearchRequest):
            payload = search_request.model_dump(exclude_none=True)
        else:
            payload = search_request

        response = await self._client.post("/memories/search", json_data=payload)
        return MemorySearchResponse(**response)

    async def update(self, memory_id: str, memory_data: Union[MemoryUpdate, dict]) -> Memory:
        """Update an existing memory asynchronously."""
        if isinstance(memory_data, MemoryUpdate):
            payload = memory_data.model_dump(exclude_none=True)
        else:
            payload = memory_data

        response = await self._client.put(f"/memories/{memory_id}", json_data=payload)
        return Memory(**response["memory"])

    async def replace(self, memory_id: str, memory_data: Union[MemoryReplace, dict]) -> dict:
        """Replace an existing memory completely asynchronously."""
        if isinstance(memory_data, MemoryReplace):
            payload = memory_data.model_dump(exclude_none=True)
        else:
            payload = memory_data

        return await self._client.post(f"/memories/{memory_id}/replace", json_data=payload)

    async def delete(self, memory_id: str, user_id: Optional[str] = None) -> dict:
        """Delete a memory asynchronously."""
        params = {}
        if user_id:
            params["user_id"] = user_id

        endpoint = f"/memories/{memory_id}"
        if params:
            from urllib.parse import urlencode

            endpoint += f"?{urlencode(params)}"

        return await self._client.delete(endpoint)

    async def from_messages(
        self,
        messages: List[dict],
        user_id: str,
        agent_id: Optional[str] = None,
        team_id: Optional[str] = None,
    ) -> MemoryFromMessagesResponse:
        """Create memories from a list of conversation messages asynchronously.

        This endpoint analyzes a conversation and extracts meaningful memories
        that can be stored and retrieved later for context in future interactions.

        Args:
            messages: List of message objects with 'role' and 'content' keys
            user_id: User ID to associate with the memories
            agent_id: Optional agent ID
            team_id: Optional team ID

        Returns:
            MemoryFromMessagesResponse with result and success message

        Example:
            ```python
            messages = [
                {"role": "user", "content": "I prefer dark mode"},
                {"role": "assistant", "content": "I'll remember that"},
                {"role": "user", "content": "I work in tech"}
            ]
            response = await client.memories.from_messages(
                messages=messages,
                user_id="user_123",
                agent_id="agent_456"
            )
            print(response.message)
            ```
        """
        request_data = MemoryFromMessagesRequest(
            messages=messages,
            user_id=user_id,
            agent_id=agent_id,
            team_id=team_id,
        )

        payload = request_data.model_dump(exclude_none=True)
        response = await self._client.post("/memories/from_messages", json_data=payload)

        # Handle response - API may return memories in 'result' field
        if "result" in response and isinstance(response["result"], list):
            response["memories"] = response.pop("result")

        return MemoryFromMessagesResponse(**response)

    async def get_chunks(
        self,
        user_id: Optional[str] = None,
        limit: int = 100,
        cursor: Optional[str] = None,
        include_embedding: bool = False,
    ) -> MemoryChunksResponse:
        """Get memory chunks with their embeddings asynchronously.

        This method uses cursor-based pagination for efficient traversal.

        Args:
            user_id: Filter by user ID (required)
            limit: Maximum number of chunks to return (default: 100, max: 100)
            cursor: Pagination cursor from previous response (use next_cursor)
            include_embedding: Whether to include vector embeddings

        Returns:
            MemoryChunksResponse with memory chunks data, next_cursor, and has_more

        Example:
            ```python
            # Get first page of memory chunks
            response = await client.memories.get_chunks(
                user_id="user_123",
                limit=100,
                include_embedding=True
            )
            print(f"Retrieved {len(response.chunks)} memory chunks")

            # Get next page using cursor
            if response.has_more:
                next_response = await client.memories.get_chunks(
                    user_id="user_123",
                    cursor=response.next_cursor,
                    limit=100
                )

            # Iterate through all memory chunks
            cursor = None
            while True:
                response = await client.memories.get_chunks(
                    user_id="user_123",
                    limit=100,
                    cursor=cursor,
                    include_embedding=True
                )
                # Process response.chunks
                if not response.has_more:
                    break
                cursor = response.next_cursor
            ```
        """
        params = {
            "limit": limit,
            "include_embedding": include_embedding,
        }
        if user_id:
            params["user_id"] = user_id
        if cursor:
            params["cursor"] = cursor

        response = await self._client.get("/memories/chunks", params=params)
        return MemoryChunksResponse(**response)

    async def load(
        self,
        user_id: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        vector_store: VectorStore = VectorStore.FAISS,
        path: Optional[str] = None,
        distance_strategy: str = "cosine",
        batch_size: int = 1000,
        show_progress: bool = True,
        embedder: Optional[Any] = None,
        re_embed: bool = False,
    ):
        """Load memories into a local vector database asynchronously.

        Fetches memories (optionally filtered) and stores them in a local
        vector database for offline search.

        Args:
            user_id: Filter by user ID (optional)
            filters: Optional filters (e.g., {"topics": ["work"]})
            vector_store: Vector database to use - currently only "faiss" is supported
            path: Path to store local database (default: /tmp/{vector_store}/memories_{user_id})
            distance_strategy: Distance metric - "cosine", "euclidean", or "inner_product"
            batch_size: Number of memories to fetch per batch
            show_progress: Whether to show progress bar
            embedder: Optional embedder to re-embed content locally. Must implement get_embedding(text: str) -> List[float]
            re_embed: If True and embedder is provided, re-embed all content using the local embedder instead of API embeddings

        Returns:
            Local vector database instance (FAISS)

        Example:
            ```python
            # Load all memories for a user (using API embeddings)
            vector_db = await client.memories.load(
                user_id="user_123",
                path="./my_memories",
                distance_strategy="cosine"
            )

            # Load with re-embedding using local embedder
            embedder = MyEmbedder()
            vector_db = await client.memories.load(
                user_id="user_123",
                path="./my_memories",
                embedder=embedder,
                re_embed=True  # Re-embed with local model
            )
            ```
        """
        if vector_store.value != "faiss":
            raise ValueError(f"Unsupported vector store: {vector_store.value}. Currently only 'faiss' is supported.")

        # Validate embedder if re_embed is True
        if re_embed and not embedder:
            raise ValueError("embedder must be provided when re_embed=True")

        if embedder:
            from mielto.internals.embedder import is_embedder

            if not is_embedder(embedder):
                raise ValueError(
                    "embedder must implement get_embedding(text: str) -> List[float] method and dimensions property"
                )

        # Lazy import to avoid requiring faiss if not using local vectors
        from mielto.internals.vectors.faiss import FAISS

        # Use embedder dimensions if re-embedding, otherwise use default API dimensions
        if re_embed and embedder:
            embedding_dims = embedder.dimensions
        else:
            embedding_dims = 1536  # Default to OpenAI dimensions

        # Initialize FAISS
        suffix = f"_{user_id}" if user_id else ""
        if path is None:
            path = f"/tmp/{vector_store.value}/memories{suffix}"

        faiss_db = FAISS(
            collection_name=f"memories{suffix}",
            path=path,
            distance_strategy=distance_strategy,
            embedding_model_dims=embedding_dims,
        )

        # Fetch all memories in batches using cursor-based pagination
        cursor = None
        total_loaded = 0

        # Create progress bar if requested
        pbar = None
        if show_progress:
            pbar = tqdm(desc="Loading memories", unit="memory")

        while True:
            # Fetch batch of memory chunks with embeddings
            chunks_response = await self.get_chunks(
                user_id=user_id,
                limit=min(batch_size, 100),  # API max limit is 100
                cursor=cursor,
                include_embedding=True,
            )

            if not chunks_response.chunks:
                break

            # Prepare data for FAISS
            vectors = []
            payloads = []
            ids = []

            for memory in chunks_response.chunks:
                # Get content and id from the chunk
                content = memory.content
                chunk_id = memory.id

                # Skip if no content or id
                if not content or not chunk_id:
                    continue

                # Extract user_id from metadata if available
                user_id = memory.metadata.get("user_id", "") if memory.metadata else ""

                # Re-embed using local embedder if requested
                if re_embed and embedder:
                    try:
                        embedding = embedder.get_embedding(content)
                        vectors.append(embedding)
                        payloads.append(
                            {
                                "content": content,
                                "metadata": {
                                    "user_id": user_id,
                                    "content_id": memory.content_id or "",
                                    **(memory.metadata or {}),
                                },
                            }
                        )
                        ids.append(chunk_id)
                    except Exception as e:
                        # Log error but continue processing
                        if show_progress:
                            tqdm.write(f"Warning: Failed to embed chunk {chunk_id}: {e}")
                        continue
                # Use API embeddings
                elif memory.embedding:
                    vectors.append(memory.embedding)
                    payloads.append(
                        {
                            "content": content,
                            "metadata": {
                                "user_id": user_id,
                                "content_id": memory.content_id or "",
                                **(memory.metadata or {}),
                            },
                        }
                    )
                    ids.append(chunk_id)

            # Insert into FAISS
            if vectors:
                faiss_db.insert(vectors=vectors, payloads=payloads, ids=ids)
                total_loaded += len(vectors)

            if pbar is not None:
                pbar.update(len(chunks_response.chunks))

            # Check if there are more chunks
            if not chunks_response.has_more:
                break

            cursor = chunks_response.next_cursor

        if pbar is not None:
            pbar.close()

        return faiss_db

    def query(
        self,
        vector_db: VectorDB,
        query_text: Optional[str] = None,
        query_embedding: Optional[List[float]] = None,
        embedder: Optional[Any] = None,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Query a local vector database (offline search).

        Note: This method is synchronous even in the async client since vector operations are CPU-bound.
        Use this method to search in locally loaded memories without making API calls.
        For remote API searches, use the `search()` method instead.

        Args:
            vector_db: Vector database instance (from `load()`)
            query_text: Query text (requires embedder to be provided)
            query_embedding: Pre-computed query vector embedding
            embedder: Embedder to use for generating embedding from query_text
            limit: Maximum number of results to return
            filters: Optional metadata filters to apply

        Returns:
            List of search results with id, score, content, and metadata

        Example:
            ```python
            # Load memories locally
            vector_db = await client.memories.load(user_id="user_123")

            # Option 1: Query with text and embedder
            results = client.memories.query(
                vector_db=vector_db,
                query_text="What are my work preferences?",
                embedder=my_embedder,
                limit=5
            )

            # Option 2: Query with pre-computed embedding
            query_embedding = my_embedder.get_embedding("What are my work preferences?")
            results = client.memories.query(
                vector_db=vector_db,
                query_embedding=query_embedding,
                limit=5,
                filters={"topics": ["work"]}
            )

            for result in results:
                print(f"{result['score']:.4f}: {result['content']}")
            ```
        """
        if not vector_db:
            raise ValueError("vector_db is required. Load memories first using load()")

        # Generate embedding from text if provided
        if query_text is not None:
            if not embedder:
                raise ValueError("embedder is required when using query_text")
            from mielto.internals.embedder import is_embedder

            if not is_embedder(embedder):
                raise ValueError(
                    "embedder must implement get_embedding(text: str) -> List[float] method and dimensions property"
                )
            query_embedding = embedder.get_embedding(query_text)

        # Validate query_embedding is provided
        if not query_embedding:
            raise ValueError("Either query_text with embedder or query_embedding must be provided")

        # Search using the local vector database (synchronous operation)
        search_results = vector_db.search(query="", vectors=[query_embedding], limit=limit, filters=filters)

        # Format results
        results = []
        for result in search_results:
            results.append(
                {
                    "id": result.id,
                    "score": result.score,
                    "content": result.payload.get("content", ""),
                    "metadata": result.payload.get("metadata", {}),
                }
            )
        return results
