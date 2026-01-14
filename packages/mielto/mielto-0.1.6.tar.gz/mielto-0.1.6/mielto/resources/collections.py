"""Collection resource for interacting with the Mielto Collections API."""

import base64
import logging
import mimetypes
from pathlib import Path
from typing import Any, BinaryIO, Dict, List, Optional, Union

from tqdm import tqdm

from mielto.client.base import AsyncBaseClient, BaseClient
from mielto.internals.vectors.base import VectorDB
from mielto.internals.vectors.enum import VectorStore
from mielto.types.collection import (
    ChunksResponse,
    Collection,
    CollectionCreate,
    CollectionUpdate,
    SearchRequest,
    SearchResponse,
)
from mielto.types.upload import FileUpload, UploadRequest, UploadResponse

logger = logging.getLogger(__name__)


class Collections:
    """Synchronous Collections resource."""

    def __init__(self, client: BaseClient):
        """Initialize the Collections resource.

        Args:
            client: Base HTTP client instance
        """
        self._client = client

    def create(self, collection_data: Union[CollectionCreate, dict]) -> Collection:
        """Create a new collection.

        Args:
            collection_data: Collection data to create

        Returns:
            Created collection

        Example:
            ```python
            collection = client.collections.create(
                CollectionCreate(
                    name="My Documents",
                    description="Personal document collection",
                    store_type="pgvector",
                    tags=["personal", "documents"]
                )
            )
            ```
        """
        if isinstance(collection_data, CollectionCreate):
            payload = collection_data.model_dump(exclude_none=True)
        else:
            payload = collection_data

        response = self._client.post("/collections", json_data=payload)
        return Collection(**response)

    def get(self, collection_id: str) -> Collection:
        """Get a specific collection by ID.

        Args:
            collection_id: Collection ID

        Returns:
            Collection object

        Example:
            ```python
            collection = client.collections.get("col_123")
            print(collection.name)
            ```
        """
        response = self._client.get(f"/collections/{collection_id}")
        return Collection(**response)

    def list(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        visibility: Optional[str] = None,
        search: Optional[str] = None,
        tags: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List collections with filtering and pagination.

        Args:
            skip: Number of collections to skip
            limit: Number of collections to return (1-1000)
            status: Filter by collection status
            visibility: Filter by visibility ('public' or 'private')
            search: Search term for name or description
            tags: Comma-separated list of tags to filter by

        Returns:
            Dict with collections data and total count

        Example:
            ```python
            result = client.collections.list(
                limit=20,
                status="active",
                tags="personal,work"
            )
            for collection in result["data"]:
                print(collection.name)
            ```
        """
        params = {
            "skip": skip,
            "limit": limit,
        }
        if status:
            params["status"] = status
        if visibility:
            params["visibility"] = visibility
        if search:
            params["search"] = search
        if tags:
            params["tags"] = tags

        return self._client.get("/collections", params=params)

    def update(self, collection_id: str, collection_data: Union[CollectionUpdate, dict]) -> Collection:
        """Update an existing collection.

        Args:
            collection_id: Collection ID
            collection_data: Updated collection data

        Returns:
            Updated collection

        Example:
            ```python
            updated = client.collections.update(
                "col_123",
                CollectionUpdate(
                    name="Updated Name",
                    tags=["updated", "documents"]
                )
            )
            ```
        """
        if isinstance(collection_data, CollectionUpdate):
            payload = collection_data.model_dump(exclude_none=True)
        else:
            payload = collection_data

        response = self._client.put(f"/collections/{collection_id}", json_data=payload)
        return Collection(**response)

    def delete(self, collection_id: str) -> dict:
        """Delete a collection (async operation).

        This initiates an asynchronous deletion process.

        Args:
            collection_id: Collection ID

        Returns:
            Deletion status with job_id

        Example:
            ```python
            result = client.collections.delete("col_123")
            print(f"Deletion job: {result['job_id']}")
            ```
        """
        return self._client.delete(f"/collections/{collection_id}")

    def search(self, search_request: Union[SearchRequest, dict]) -> SearchResponse:
        """Search within a collection.

        Args:
            search_request: Search parameters

        Returns:
            SearchResponse with results

        Example:
            ```python
            results = client.collections.search(
                SearchRequest(
                    query="artificial intelligence",
                    collection_id="col_123",
                    search_type="hybrid",
                    max_results=10
                )
            )
            for result in results.results:
                print(f"{result.content[:100]}... (score: {result.score})")
            ```
        """
        if isinstance(search_request, SearchRequest):
            payload = search_request.model_dump(exclude_none=True)
        else:
            payload = search_request

        response = self._client.post("/collections/search", json_data=payload)
        return SearchResponse(**response)

    def insert(
        self,
        collection_id: str,
        content: Optional[str] = None,
        file_path: Optional[Union[str, Path]] = None,
        file_obj: Optional[BinaryIO] = None,
        file_base64: Optional[str] = None,
        urls: Optional[List[str]] = None,
        label: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        mimetype: Optional[str] = None,
        ingest: bool = True,
        reader: Optional[Union[str, Dict[str, str]]] = None,
    ) -> UploadResponse:
        """Insert content into a collection.

        This method supports multiple input types:
        - Raw text content
        - File path (with automatic mimetype detection)
        - File object (opened file)
        - Base64 encoded file content
        - URLs

        Args:
            collection_id: Collection ID
            content: Raw text content to insert
            file_path: Path to file to upload
            file_obj: File object to upload
            file_base64: Base64 encoded file content (alternative to file_path/file_obj)
            urls: List of URLs to download and insert
            label: Custom label for the content
            description: Description of the content
            metadata: Additional metadata
            mimetype: MIME type of the file (auto-detected if not provided)
            ingest: Whether to ingest content into vector database
            reader: Reader configuration for file processing

        Returns:
            UploadResponse with upload results

        Examples:
            ```python
            # Insert raw text
            result = client.collections.insert(
                collection_id="col_123",
                content="This is my text content",
                label="Quick Note"
            )

            # Insert from file path (mimetype auto-detected)
            result = client.collections.insert(
                collection_id="col_123",
                file_path="document.pdf",
                reader="native"
            )

            # Insert from file object
            with open("document.pdf", "rb") as f:
                result = client.collections.insert(
                    collection_id="col_123",
                    file_obj=f,
                    label="document.pdf",
                    mimetype="application/pdf"
                )

            # Insert from base64
            result = client.collections.insert(
                collection_id="col_123",
                file_base64="base64_encoded_content...",
                label="document.pdf",
                mimetype="application/pdf"
            )

            # Insert from URLs
            result = client.collections.insert(
                collection_id="col_123",
                urls=["https://example.com/doc.pdf"],
                reader="native"
            )
            ```
        """
        # Prepare the request data
        files_list = []

        # Handle file path
        if file_path:
            file_path = Path(file_path)
            with open(file_path, "rb") as f:
                file_content = f.read()
                encoded = base64.b64encode(file_content).decode("utf-8")

                # Auto-detect mimetype if not provided
                detected_mimetype = mimetype
                if not detected_mimetype:
                    detected_mimetype, _ = mimetypes.guess_type(str(file_path))

                files_list.append(
                    FileUpload(
                        file=encoded,
                        label=label or file_path.name,
                        mimetype=detected_mimetype,
                    )
                )

        # Handle file object
        elif file_obj:
            file_content = file_obj.read()
            encoded = base64.b64encode(file_content).decode("utf-8")

            # Try to detect mimetype from file object name
            detected_mimetype = mimetype
            if not detected_mimetype and hasattr(file_obj, "name"):
                detected_mimetype, _ = mimetypes.guess_type(file_obj.name)

            files_list.append(
                FileUpload(
                    file=encoded,
                    label=label or getattr(file_obj, "name", "file"),
                    mimetype=detected_mimetype,
                )
            )

        # Handle base64 directly
        elif file_base64:
            files_list.append(
                FileUpload(
                    file=file_base64,
                    label=label or "file",
                    mimetype=mimetype,
                )
            )

        # Prepare upload request
        upload_req = UploadRequest(
            collection_id=collection_id,
            content_type="text" if content else "url" if urls else "file",
            files=files_list if files_list else None,
            content=content,
            urls=urls,
            label=label,
            description=description,
            metadata=metadata,
            ingest=ingest,
            reader=reader,
        )

        payload = upload_req.model_dump(exclude_none=True)
        response = self._client.post("/upload", json_data=payload)
        return UploadResponse(**response)

    def insert_directory(
        self,
        collection_id: str,
        directory_path: Union[str, Path],
        recursive: bool = True,
        file_extensions: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        ingest: bool = True,
        reader: Optional[Union[str, Dict[str, str]]] = None,
        batch_size: int = 10,
        show_progress: bool = True,
    ) -> List[UploadResponse]:
        """Insert all files from a directory into a collection.

        Args:
            collection_id: Collection ID
            directory_path: Path to directory containing files
            recursive: Whether to recursively traverse subdirectories
            file_extensions: List of file extensions to include (e.g., ['.pdf', '.txt'])
            exclude_patterns: List of filename patterns to exclude (e.g., ['*.tmp', '.DS_Store'])
            metadata: Additional metadata to attach to all files
            ingest: Whether to ingest content into vector database
            reader: Reader configuration for file processing
            batch_size: Number of files to upload per batch
            show_progress: Whether to show progress bar (default: True)

        Returns:
            List of UploadResponse objects, one per batch

        Examples:
            ```python
            # Upload all files from a directory
            results = client.collections.insert_directory(
                collection_id="col_123",
                directory_path="./documents"
            )

            # Upload only PDFs, non-recursively
            results = client.collections.insert_directory(
                collection_id="col_123",
                directory_path="./documents",
                recursive=False,
                file_extensions=['.pdf']
            )

            # Upload with exclusions
            results = client.collections.insert_directory(
                collection_id="col_123",
                directory_path="./documents",
                exclude_patterns=['*.tmp', '.DS_Store', '__pycache__']
            )
            ```
        """
        directory = Path(directory_path)
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        if not directory.is_dir():
            raise NotADirectoryError(f"Not a directory: {directory_path}")

        # Collect all files
        files_to_upload = self._collect_files(
            directory=directory,
            recursive=recursive,
            file_extensions=file_extensions,
            exclude_patterns=exclude_patterns,
        )

        if not files_to_upload:
            return []

        # Upload in batches with progress bar
        responses = []
        total_batches = (len(files_to_upload) + batch_size - 1) // batch_size

        # Create progress bars
        batch_pbar = tqdm(
            total=total_batches,
            desc="Uploading batches",
            unit="batch",
            disable=not show_progress,
        )
        file_pbar = tqdm(
            total=len(files_to_upload),
            desc="Processing files",
            unit="file",
            disable=not show_progress,
        )

        try:
            for i in range(0, len(files_to_upload), batch_size):
                batch = files_to_upload[i : i + batch_size]

                # Prepare files for this batch
                files_list = []
                for file_path in batch:
                    with open(file_path, "rb") as f:
                        file_content = f.read()
                        encoded = base64.b64encode(file_content).decode("utf-8")

                        # Auto-detect mimetype
                        detected_mimetype, _ = mimetypes.guess_type(str(file_path))

                        # Get relative path for label
                        try:
                            relative_path = file_path.relative_to(directory)
                            label = str(relative_path)
                        except ValueError:
                            label = file_path.name

                        files_list.append(
                            FileUpload(
                                file=encoded,
                                label=label,
                                mimetype=detected_mimetype,
                            )
                        )

                    file_pbar.update(1)

                # Upload batch
                upload_req = UploadRequest(
                    collection_id=collection_id,
                    content_type="file",
                    files=files_list,
                    metadata=metadata,
                    ingest=ingest,
                    reader=reader,
                )

                payload = upload_req.model_dump(exclude_none=True)
                response_data = self._client.post("/upload", json_data=payload)
                responses.append(UploadResponse(**response_data))

                batch_pbar.update(1)

        finally:
            batch_pbar.close()
            file_pbar.close()

        return responses

    def _collect_files(
        self,
        directory: Path,
        recursive: bool,
        file_extensions: Optional[List[str]],
        exclude_patterns: Optional[List[str]],
    ) -> List[Path]:
        """Collect files from directory based on filters.

        Args:
            directory: Directory to scan
            recursive: Whether to scan recursively
            file_extensions: File extensions to include
            exclude_patterns: Patterns to exclude

        Returns:
            List of file paths
        """
        files = []

        # Get all files
        if recursive:
            pattern = "**/*"
        else:
            pattern = "*"

        for item in directory.glob(pattern):
            if not item.is_file():
                continue

            # Check if file should be excluded
            if exclude_patterns:
                excluded = False
                for pattern in exclude_patterns:
                    if item.match(pattern) or item.name == pattern:
                        excluded = True
                        break
                if excluded:
                    continue

            # Check file extension
            if file_extensions:
                if item.suffix.lower() not in [ext.lower() for ext in file_extensions]:
                    continue

            files.append(item)

        return files

    def get_chunks(
        self,
        collection_id: str,
        limit: int = 50,
        cursor: Optional[str] = None,
        include_embedding: bool = False,
        content_id: Optional[str] = None,
    ) -> ChunksResponse:
        """Get chunks from a collection with their embeddings.

        This method uses cursor-based pagination for efficient traversal.

        Args:
            collection_id: Collection ID
            limit: Maximum number of chunks to return (default: 50, max: 500)
            cursor: Pagination cursor from previous response (use next_cursor)
            include_embedding: Whether to include vector embeddings
            content_id: Optional filter by content ID

        Returns:
            ChunksResponse with chunks data, next_cursor, and has_more

        Example:
            ```python
            # Get first page of chunks
            response = client.collections.get_chunks(
                collection_id="col_123",
                limit=100,
                include_embedding=True
            )
            print(f"Retrieved {len(response.chunks)} chunks")

            # Get next page using cursor
            if response.has_more:
                next_response = client.collections.get_chunks(
                    collection_id="col_123",
                    cursor=response.next_cursor,
                    limit=100
                )

            # Iterate through all chunks
            cursor = None
            while True:
                response = client.collections.get_chunks(
                    collection_id="col_123",
                    limit=100,
                    cursor=cursor
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
        if cursor:
            params["cursor"] = cursor
        if content_id:
            params["content_id"] = content_id

        headers = {"X-Collection-Id": collection_id}
        response = self._client.get("/chunks", params=params, headers=headers)
        return ChunksResponse(**response)

    def load(
        self,
        collection_id: str,
        filters: Optional[Dict[str, Any]] = None,
        vector_store: VectorStore = VectorStore.FAISS,
        path: Optional[str] = None,
        distance_strategy: str = "cosine",
        batch_size: int = 1000,
        show_progress: bool = True,
        embedder: Optional[Any] = None,
        re_embed: bool = False,
        force_sync: bool = False,
        sync_threshold_hours: int = 24,
    ):
        """Load chunks from a collection into a local vector database.

        Fetches chunks (optionally filtered) from the remote collection and stores them
        in a local vector database for offline search. Automatically caches and reuses
        existing indexes to avoid unnecessary API calls.

        Args:
            collection_id: Collection ID to load from
            filters: Optional filters to apply when fetching chunks (e.g., {"metadata.category": "ml"})
            vector_store: Vector database to use - currently only "faiss" is supported
            path: Path to store local database (default: /tmp/{vector_store}/{collection_id})
            distance_strategy: Distance metric - "cosine", "euclidean", or "inner_product"
            batch_size: Number of chunks to fetch per batch
            show_progress: Whether to show progress bar
            embedder: Optional embedder to re-embed content locally. Must implement get_embedding(text: str) -> List[float]
            re_embed: If True and embedder is provided, re-embed all content using the local embedder instead of API embeddings
            force_sync: If True, always re-fetch chunks even if local index is fresh (default: False)
            sync_threshold_hours: Hours after which local index is considered stale and needs refresh (default: 24)

        Returns:
            Local vector database instance (FAISS)

        Example:
            ```python
            # Load all chunks from a collection (using API embeddings)
            vector_db = client.collections.load(
                collection_id="col_123",
                path="./my_local_db",
                distance_strategy="cosine"
            )

            # Load with re-embedding using local embedder
            from fastembed import TextEmbedding

            class MyEmbedder:
                def __init__(self):
                    self.model = TextEmbedding("BAAI/bge-small-en-v1.5")
                    self._dimensions = 384

                def get_embedding(self, text: str):
                    return list(list(self.model.embed(text))[0])

                @property
                def dimensions(self):
                    return self._dimensions

            embedder = MyEmbedder()
            vector_db = client.collections.load(
                collection_id="col_123",
                path="./my_local_db",
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

        # Get collection info to determine embedding dimensions
        collection = self.get(collection_id)
        embedding_config = collection.embedding or {}

        # Use embedder dimensions if re-embedding, otherwise use API dimensions
        if re_embed and embedder:
            embedding_dims = embedder.dimensions
        else:
            embedding_dims = embedding_config.get("dimension", 1536)  # Default to OpenAI dimensions

        # Initialize FAISS
        if path is None:
            path = f"/tmp/{vector_store.value}/{collection_id}"

        faiss_db = FAISS(
            collection_name=collection_id,
            path=path,
            distance_strategy=distance_strategy,
            embedding_model_dims=embedding_dims,
            collection_id=collection_id,
            embedder=embedder if re_embed else None,
        )

        # Check if index is fresh and can be reused
        if not force_sync and faiss_db.index and faiss_db.is_fresh(sync_threshold_hours):
            logger.info(
                f"Local index is fresh (last synced: {faiss_db.config.last_synced_at}). "
                f"Skipping fetch. Use force_sync=True to re-fetch."
            )
            if show_progress:
                print(
                    f"✅ Using cached index ({faiss_db.config.total_chunks} chunks, last synced: {faiss_db.config.last_synced_at})"
                )
            return faiss_db

        # If index is stale, reset and re-fetch
        if faiss_db.index and not force_sync:
            logger.info(
                f"Index exists but is stale (last synced: {faiss_db.config.last_synced_at if faiss_db.config else 'unknown'}). "
                f"Re-fetching chunks..."
            )
            if show_progress:
                print("🔄 Index is stale, updating from remote...")
            # Reset the index to start fresh
            faiss_db.delete_index()
            faiss_db.create(collection_id)
        elif force_sync and faiss_db.index:
            logger.info("Force sync requested. Re-fetching all chunks...")
            if show_progress:
                print("🔄 Force sync - updating from remote...")
            faiss_db.delete_index()
            faiss_db.create(collection_id)

        # Fetch all chunks in batches using cursor-based pagination
        cursor = None
        total_loaded = 0

        # Create progress bar if requested
        pbar = None
        if show_progress:
            pbar = tqdm(desc="Loading chunks", unit="chunk")

        while True:
            # Fetch batch of chunks with embeddings
            chunks_response = self.get_chunks(
                collection_id=collection_id,
                limit=batch_size,
                cursor=cursor,
                include_embedding=True,
            )

            if not chunks_response.chunks:
                break

            # Prepare data for FAISS
            vectors = []
            payloads = []
            ids = []

            for chunk in chunks_response.chunks:
                # Re-embed using local embedder if requested
                if re_embed and embedder:
                    try:
                        embedding = embedder.get_embedding(chunk.content)
                        vectors.append(embedding)
                        payloads.append(
                            {
                                "content": chunk.content,
                                "metadata": chunk.metadata,
                            }
                        )
                        ids.append(chunk.id)
                    except Exception as e:
                        # Log error but continue processing
                        if show_progress:
                            tqdm.write(f"Warning: Failed to embed chunk {chunk.id}: {e}")
                        continue
                # Use API embeddings
                elif chunk.embedding:
                    vectors.append(chunk.embedding)
                    payloads.append(
                        {
                            "content": chunk.content,
                            "metadata": chunk.metadata,
                        }
                    )
                    ids.append(chunk.id)

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

        # Mark index as synced with current timestamp
        faiss_db.mark_synced(total_chunks=total_loaded)

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

        Use this method to search in a locally loaded collection without making API calls.
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
            # Load collection locally
            vector_db = client.collections.load(collection_id="col_123")

            # Option 1: Query with text and embedder
            results = client.collections.query(
                vector_db=vector_db,
                query_text="What is machine learning?",
                embedder=my_embedder,
                limit=10
            )

            # Option 2: Query with pre-computed embedding
            query_embedding = my_embedder.get_embedding("What is machine learning?")
            results = client.collections.query(
                vector_db=vector_db,
                query_embedding=query_embedding,
                limit=10,
                filters={"category": "ml"}
            )

            for result in results:
                print(f"{result['score']:.4f}: {result['content'][:100]}")
            ```
        """
        if not vector_db:
            raise ValueError("vector_db is required. Load a collection first using load()")

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


class AsyncCollections:
    """Asynchronous Collections resource."""

    def __init__(self, client: AsyncBaseClient):
        """Initialize the async Collections resource.

        Args:
            client: Async base HTTP client instance
        """
        self._client = client

    async def create(self, collection_data: Union[CollectionCreate, dict]) -> Collection:
        """Create a new collection asynchronously."""
        if isinstance(collection_data, CollectionCreate):
            payload = collection_data.model_dump(exclude_none=True)
        else:
            payload = collection_data

        response = await self._client.post("/collections", json_data=payload)
        return Collection(**response)

    async def get(self, collection_id: str) -> Collection:
        """Get a specific collection by ID asynchronously."""
        response = await self._client.get(f"/collections/{collection_id}")
        return Collection(**response)

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        visibility: Optional[str] = None,
        search: Optional[str] = None,
        tags: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List collections with filtering and pagination asynchronously."""
        params = {
            "skip": skip,
            "limit": limit,
        }
        if status:
            params["status"] = status
        if visibility:
            params["visibility"] = visibility
        if search:
            params["search"] = search
        if tags:
            params["tags"] = tags

        return await self._client.get("/collections", params=params)

    async def update(self, collection_id: str, collection_data: Union[CollectionUpdate, dict]) -> Collection:
        """Update an existing collection asynchronously."""
        if isinstance(collection_data, CollectionUpdate):
            payload = collection_data.model_dump(exclude_none=True)
        else:
            payload = collection_data

        response = await self._client.put(f"/collections/{collection_id}", json_data=payload)
        return Collection(**response)

    async def delete(self, collection_id: str) -> dict:
        """Delete a collection asynchronously."""
        return await self._client.delete(f"/collections/{collection_id}")

    async def search(self, search_request: Union[SearchRequest, dict]) -> SearchResponse:
        """Search within a collection asynchronously."""
        if isinstance(search_request, SearchRequest):
            payload = search_request.model_dump(exclude_none=True)
        else:
            payload = search_request

        response = await self._client.post("/collections/search", json_data=payload)
        return SearchResponse(**response)

    async def insert(
        self,
        collection_id: str,
        content: Optional[str] = None,
        file_path: Optional[Union[str, Path]] = None,
        file_obj: Optional[BinaryIO] = None,
        file_base64: Optional[str] = None,
        urls: Optional[List[str]] = None,
        label: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        mimetype: Optional[str] = None,
        ingest: bool = True,
        reader: Optional[Union[str, Dict[str, str]]] = None,
    ) -> UploadResponse:
        """Insert content into a collection asynchronously."""
        files_list = []

        if file_path:
            file_path = Path(file_path)
            with open(file_path, "rb") as f:
                file_content = f.read()
                encoded = base64.b64encode(file_content).decode("utf-8")

                # Auto-detect mimetype if not provided
                detected_mimetype = mimetype
                if not detected_mimetype:
                    detected_mimetype, _ = mimetypes.guess_type(str(file_path))

                files_list.append(
                    FileUpload(
                        file=encoded,
                        label=label or file_path.name,
                        mimetype=detected_mimetype,
                    )
                )

        elif file_obj:
            file_content = file_obj.read()
            encoded = base64.b64encode(file_content).decode("utf-8")

            # Try to detect mimetype from file object name
            detected_mimetype = mimetype
            if not detected_mimetype and hasattr(file_obj, "name"):
                detected_mimetype, _ = mimetypes.guess_type(file_obj.name)

            files_list.append(
                FileUpload(
                    file=encoded,
                    label=label or getattr(file_obj, "name", "file"),
                    mimetype=detected_mimetype,
                )
            )

        elif file_base64:
            files_list.append(
                FileUpload(
                    file=file_base64,
                    label=label or "file",
                    mimetype=mimetype,
                )
            )

        upload_req = UploadRequest(
            collection_id=collection_id,
            content_type="text" if content else "url" if urls else "file",
            files=files_list if files_list else None,
            content=content,
            urls=urls,
            label=label,
            description=description,
            metadata=metadata,
            ingest=ingest,
            reader=reader,
        )

        payload = upload_req.model_dump(exclude_none=True)
        response = await self._client.post("/upload", json_data=payload)
        return UploadResponse(**response)

    async def insert_directory(
        self,
        collection_id: str,
        directory_path: Union[str, Path],
        recursive: bool = True,
        file_extensions: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        ingest: bool = True,
        reader: Optional[Union[str, Dict[str, str]]] = None,
        batch_size: int = 10,
        show_progress: bool = True,
    ) -> List[UploadResponse]:
        """Insert all files from a directory into a collection asynchronously.

        Args:
            collection_id: Collection ID
            directory_path: Path to directory containing files
            recursive: Whether to recursively traverse subdirectories
            file_extensions: List of file extensions to include (e.g., ['.pdf', '.txt'])
            exclude_patterns: List of filename patterns to exclude (e.g., ['*.tmp', '.DS_Store'])
            metadata: Additional metadata to attach to all files
            ingest: Whether to ingest content into vector database
            reader: Reader configuration for file processing
            batch_size: Number of files to upload per batch
            show_progress: Whether to show progress bar (default: True)

        Returns:
            List of UploadResponse objects, one per batch

        Example:
            ```python
            # Upload all files from a directory
            results = await client.collections.insert_directory(
                collection_id="col_123",
                directory_path="./documents",
                file_extensions=['.pdf', '.docx']
            )
            ```
        """
        directory = Path(directory_path)
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        if not directory.is_dir():
            raise NotADirectoryError(f"Not a directory: {directory_path}")

        # Collect all files
        files_to_upload = self._collect_files(
            directory=directory,
            recursive=recursive,
            file_extensions=file_extensions,
            exclude_patterns=exclude_patterns,
        )

        if not files_to_upload:
            return []

        # Upload in batches with progress bar
        responses = []
        total_batches = (len(files_to_upload) + batch_size - 1) // batch_size

        # Create progress bars
        batch_pbar = tqdm(
            total=total_batches,
            desc="Uploading batches",
            unit="batch",
            disable=not show_progress,
        )
        file_pbar = tqdm(
            total=len(files_to_upload),
            desc="Processing files",
            unit="file",
            disable=not show_progress,
        )

        try:
            for i in range(0, len(files_to_upload), batch_size):
                batch = files_to_upload[i : i + batch_size]

                # Prepare files for this batch
                files_list = []
                for file_path in batch:
                    with open(file_path, "rb") as f:
                        file_content = f.read()
                        encoded = base64.b64encode(file_content).decode("utf-8")

                        # Auto-detect mimetype
                        detected_mimetype, _ = mimetypes.guess_type(str(file_path))

                        # Get relative path for label
                        try:
                            relative_path = file_path.relative_to(directory)
                            label = str(relative_path)
                        except ValueError:
                            label = file_path.name

                        files_list.append(
                            FileUpload(
                                file=encoded,
                                label=label,
                                mimetype=detected_mimetype,
                            )
                        )

                    file_pbar.update(1)

                # Upload batch
                upload_req = UploadRequest(
                    collection_id=collection_id,
                    content_type="file",
                    files=files_list,
                    metadata=metadata,
                    ingest=ingest,
                    reader=reader,
                )

                payload = upload_req.model_dump(exclude_none=True)
                response_data = await self._client.post("/upload", json_data=payload)
                responses.append(UploadResponse(**response_data))

                batch_pbar.update(1)

        finally:
            batch_pbar.close()
            file_pbar.close()

        return responses

    def _collect_files(
        self,
        directory: Path,
        recursive: bool,
        file_extensions: Optional[List[str]],
        exclude_patterns: Optional[List[str]],
    ) -> List[Path]:
        """Collect files from directory based on filters.

        Args:
            directory: Directory to scan
            recursive: Whether to scan recursively
            file_extensions: File extensions to include
            exclude_patterns: Patterns to exclude

        Returns:
            List of file paths
        """
        files = []

        # Get all files
        if recursive:
            pattern = "**/*"
        else:
            pattern = "*"

        for item in directory.glob(pattern):
            if not item.is_file():
                continue

            # Check if file should be excluded
            if exclude_patterns:
                excluded = False
                for pattern in exclude_patterns:
                    if item.match(pattern) or item.name == pattern:
                        excluded = True
                        break
                if excluded:
                    continue

            # Check file extension
            if file_extensions:
                if item.suffix.lower() not in [ext.lower() for ext in file_extensions]:
                    continue

            files.append(item)

        return files

    async def get_chunks(
        self,
        collection_id: str,
        limit: int = 50,
        cursor: Optional[str] = None,
        include_embedding: bool = False,
        content_id: Optional[str] = None,
    ) -> ChunksResponse:
        """Get chunks from a collection with their embeddings asynchronously.

        This method uses cursor-based pagination for efficient traversal.

        Args:
            collection_id: Collection ID
            limit: Maximum number of chunks to return (default: 50, max: 500)
            cursor: Pagination cursor from previous response (use next_cursor)
            include_embedding: Whether to include vector embeddings
            content_id: Optional filter by content ID

        Returns:
            ChunksResponse with chunks data, next_cursor, and has_more

        Example:
            ```python
            # Get first page of chunks
            response = await client.collections.get_chunks(
                collection_id="col_123",
                limit=100,
                include_embedding=True
            )
            print(f"Retrieved {len(response.chunks)} chunks")

            # Get next page using cursor
            if response.has_more:
                next_response = await client.collections.get_chunks(
                    collection_id="col_123",
                    cursor=response.next_cursor,
                    limit=100
                )

            # Iterate through all chunks
            cursor = None
            while True:
                response = await client.collections.get_chunks(
                    collection_id="col_123",
                    limit=100,
                    cursor=cursor
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
        if cursor:
            params["cursor"] = cursor
        if content_id:
            params["content_id"] = content_id

        headers = {"X-Collection-Id": collection_id}
        response = await self._client.get("/chunks", params=params, headers=headers)
        return ChunksResponse(**response)

    async def load(
        self,
        collection_id: str,
        filters: Optional[Dict[str, Any]] = None,
        vector_store: VectorStore = VectorStore.FAISS,
        path: Optional[str] = None,
        distance_strategy: str = "cosine",
        batch_size: int = 1000,
        show_progress: bool = True,
        embedder: Optional[Any] = None,
        re_embed: bool = False,
        force_sync: bool = False,
        sync_threshold_hours: int = 24,
    ):
        """Load chunks from a collection into a local vector database asynchronously.

        Fetches chunks (optionally filtered) from the remote collection and stores them
        in a local vector database for offline search. Automatically caches and reuses
        existing indexes to avoid unnecessary API calls.

        Args:
            collection_id: Collection ID to load from
            filters: Optional filters to apply when fetching chunks (e.g., {"metadata.category": "ml"})
            vector_store: Vector database to use - currently only "faiss" is supported
            path: Path to store local database (default: /tmp/{vector_store}/{collection_id})
            distance_strategy: Distance metric - "cosine", "euclidean", or "inner_product"
            batch_size: Number of chunks to fetch per batch
            show_progress: Whether to show progress bar
            embedder: Optional embedder to re-embed content locally. Must implement get_embedding(text: str) -> List[float]
            re_embed: If True and embedder is provided, re-embed all content using the local embedder instead of API embeddings
            force_sync: If True, always re-fetch chunks even if local index is fresh (default: False)
            sync_threshold_hours: Hours after which local index is considered stale and needs refresh (default: 24)

        Returns:
            Local vector database instance (FAISS)

        Example:
            ```python
            # Load all chunks from a collection (using API embeddings)
            vector_db = await client.collections.load(
                collection_id="col_123",
                path="./my_local_db",
                distance_strategy="cosine"
            )

            # Load with re-embedding using local embedder
            from fastembed import TextEmbedding

            class MyEmbedder:
                def __init__(self):
                    self.model = TextEmbedding("BAAI/bge-small-en-v1.5")
                    self._dimensions = 384

                def get_embedding(self, text: str):
                    return list(list(self.model.embed(text))[0])

                @property
                def dimensions(self):
                    return self._dimensions

            embedder = MyEmbedder()
            vector_db = await client.collections.load(
                collection_id="col_123",
                path="./my_local_db",
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

        # Get collection info to determine embedding dimensions
        collection = await self.get(collection_id)
        embedding_config = collection.embedding or {}

        # Use embedder dimensions if re-embedding, otherwise use API dimensions
        if re_embed and embedder:
            embedding_dims = embedder.dimensions
        else:
            embedding_dims = embedding_config.get("dimension", 1536)  # Default to OpenAI dimensions

        # Initialize FAISS
        if path is None:
            path = f"/tmp/{vector_store.value}/{collection_id}"

        faiss_db = FAISS(
            collection_name=collection_id,
            path=path,
            distance_strategy=distance_strategy,
            embedding_model_dims=embedding_dims,
            collection_id=collection_id,
            embedder=embedder if re_embed else None,
        )

        # Check if index is fresh and can be reused
        if not force_sync and faiss_db.index and faiss_db.is_fresh(sync_threshold_hours):
            logger.info(
                f"Local index is fresh (last synced: {faiss_db.config.last_synced_at}). "
                f"Skipping fetch. Use force_sync=True to re-fetch."
            )
            if show_progress:
                print(
                    f"✅ Using cached index ({faiss_db.config.total_chunks} chunks, last synced: {faiss_db.config.last_synced_at})"
                )
            return faiss_db

        # If index is stale, reset and re-fetch
        if faiss_db.index and not force_sync:
            logger.info(
                f"Index exists but is stale (last synced: {faiss_db.config.last_synced_at if faiss_db.config else 'unknown'}). "
                f"Re-fetching chunks..."
            )
            if show_progress:
                print("🔄 Index is stale, updating from remote...")
            # Reset the index to start fresh
            faiss_db.delete_index()
            faiss_db.create(collection_id)
        elif force_sync and faiss_db.index:
            logger.info("Force sync requested. Re-fetching all chunks...")
            if show_progress:
                print("🔄 Force sync - updating from remote...")
            faiss_db.delete_index()
            faiss_db.create(collection_id)

        # Fetch all chunks in batches using cursor-based pagination
        cursor = None
        total_loaded = 0

        # Create progress bar if requested
        pbar = None
        if show_progress:
            pbar = tqdm(desc="Loading chunks", unit="chunk")

        while True:
            # Fetch batch of chunks with embeddings
            chunks_response = await self.get_chunks(
                collection_id=collection_id,
                limit=batch_size,
                cursor=cursor,
                include_embedding=True,
            )

            if not chunks_response.chunks:
                break

            # Prepare data for FAISS
            vectors = []
            payloads = []
            ids = []

            for chunk in chunks_response.chunks:
                # Re-embed using local embedder if requested
                if re_embed and embedder:
                    try:
                        embedding = embedder.get_embedding(chunk.content)
                        vectors.append(embedding)
                        payloads.append(
                            {
                                "content": chunk.content,
                                "metadata": chunk.metadata,
                            }
                        )
                        ids.append(chunk.id)
                    except Exception as e:
                        # Log error but continue processing
                        if show_progress:
                            tqdm.write(f"Warning: Failed to embed chunk {chunk.id}: {e}")
                        continue
                # Use API embeddings
                elif chunk.embedding:
                    vectors.append(chunk.embedding)
                    payloads.append(
                        {
                            "content": chunk.content,
                            "metadata": chunk.metadata,
                        }
                    )
                    ids.append(chunk.id)

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

        # Mark index as synced with current timestamp
        faiss_db.mark_synced(total_chunks=total_loaded)

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
        Use this method to search in a locally loaded collection without making API calls.
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
            # Load collection locally
            vector_db = await client.collections.load(collection_id="col_123")

            # Option 1: Query with text and embedder
            results = client.collections.query(
                vector_db=vector_db,
                query_text="What is machine learning?",
                embedder=my_embedder,
                limit=10
            )

            # Option 2: Query with pre-computed embedding
            query_embedding = my_embedder.get_embedding("What is machine learning?")
            results = client.collections.query(
                vector_db=vector_db,
                query_embedding=query_embedding,
                limit=10,
                filters={"category": "ml"}
            )

            for result in results:
                print(f"{result['score']:.4f}: {result['content'][:100]}")
            ```
        """
        if not vector_db:
            raise ValueError("vector_db is required. Load a collection first using load()")

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
