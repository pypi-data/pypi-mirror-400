"""Tests for local vector functionality with FAISS."""

import tempfile
from unittest.mock import MagicMock, patch

import pytest

from mielto.internals.vectors.faiss import FAISS
from mielto.types.collection import ChunksResponse


class TestFAISS:
    """Test FAISS vector database implementation."""

    @pytest.fixture
    def temp_path(self):
        """Create a temporary directory for FAISS storage."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def faiss_db(self, temp_path):
        """Create a FAISS instance for testing."""
        db = FAISS(
            collection_name="test_collection",
            path=temp_path,
            distance_strategy="cosine",
            embedding_model_dims=384,
        )
        return db

    def test_create_collection(self, faiss_db):
        """Test creating a FAISS collection."""
        assert faiss_db.collection_name == "test_collection"
        assert faiss_db.index is not None
        assert faiss_db.index.ntotal == 0

    def test_insert_vectors(self, faiss_db):
        """Test inserting vectors into FAISS."""
        vectors = [
            [0.1, 0.2, 0.3] + [0.0] * 381,
            [0.4, 0.5, 0.6] + [0.0] * 381,
            [0.7, 0.8, 0.9] + [0.0] * 381,
        ]
        payloads = [
            {"content": "First document", "metadata": {"source": "test1"}},
            {"content": "Second document", "metadata": {"source": "test2"}},
            {"content": "Third document", "metadata": {"source": "test3"}},
        ]
        ids = ["id1", "id2", "id3"]

        faiss_db.insert(vectors=vectors, payloads=payloads, ids=ids)

        assert faiss_db.index.ntotal == 3
        assert len(faiss_db.docstore) == 3
        assert faiss_db.docstore["id1"]["content"] == "First document"

    def test_search_vectors(self, faiss_db):
        """Test searching for similar vectors."""
        # Insert test data
        vectors = [
            [0.1, 0.2, 0.3] + [0.0] * 381,
            [0.4, 0.5, 0.6] + [0.0] * 381,
            [0.7, 0.8, 0.9] + [0.0] * 381,
        ]
        payloads = [
            {"content": "Machine learning basics", "metadata": {"topic": "ml"}},
            {"content": "Deep learning tutorial", "metadata": {"topic": "dl"}},
            {"content": "Data science intro", "metadata": {"topic": "ds"}},
        ]
        ids = ["id1", "id2", "id3"]

        faiss_db.insert(vectors=vectors, payloads=payloads, ids=ids)

        # Search with a query vector similar to the first vector
        query_vector = [0.11, 0.21, 0.31] + [0.0] * 381
        results = faiss_db.search(query="", vectors=[query_vector], limit=2)

        assert len(results) <= 2
        assert results[0].id in ["id1", "id2", "id3"]
        assert results[0].payload["content"] is not None

    def test_search_with_filters(self, faiss_db):
        """Test searching with metadata filters."""
        vectors = [
            [0.1, 0.2, 0.3] + [0.0] * 381,
            [0.4, 0.5, 0.6] + [0.0] * 381,
            [0.7, 0.8, 0.9] + [0.0] * 381,
        ]
        payloads = [
            {"content": "ML document", "category": "ml", "level": "beginner"},
            {"content": "DL document", "category": "dl", "level": "advanced"},
            {"content": "DS document", "category": "ds", "level": "beginner"},
        ]
        ids = ["id1", "id2", "id3"]

        faiss_db.insert(vectors=vectors, payloads=payloads, ids=ids)

        # Search with filter
        query_vector = [0.5, 0.5, 0.5] + [0.0] * 381
        results = faiss_db.search(query="", vectors=[query_vector], limit=5, filters={"category": "ml"})

        assert len(results) >= 1
        # Check that all results match the filter
        for result in results:
            assert result.payload.get("category") == "ml"

    def test_get_vector(self, faiss_db):
        """Test retrieving a vector by ID."""
        vectors = [[0.1, 0.2, 0.3] + [0.0] * 381]
        payloads = [{"content": "Test document", "metadata": {"key": "value"}}]
        ids = ["test_id"]

        faiss_db.insert(vectors=vectors, payloads=payloads, ids=ids)

        result = faiss_db.get("test_id")
        assert result is not None
        assert result.id == "test_id"
        assert result.payload["content"] == "Test document"

    def test_delete_vector(self, faiss_db):
        """Test deleting a vector by ID."""
        vectors = [[0.1, 0.2, 0.3] + [0.0] * 381]
        payloads = [{"content": "Test document"}]
        ids = ["test_id"]

        faiss_db.insert(vectors=vectors, payloads=payloads, ids=ids)
        faiss_db.delete("test_id")

        result = faiss_db.get("test_id")
        assert result is None

    def test_list_vectors(self, faiss_db):
        """Test listing all vectors."""
        vectors = [
            [0.1, 0.2, 0.3] + [0.0] * 381,
            [0.4, 0.5, 0.6] + [0.0] * 381,
        ]
        payloads = [
            {"content": "First document"},
            {"content": "Second document"},
        ]
        ids = ["id1", "id2"]

        faiss_db.insert(vectors=vectors, payloads=payloads, ids=ids)

        results = faiss_db.list(limit=10)
        assert len(results) == 1  # list returns a list with one element
        assert len(results[0]) == 2  # which contains all the results

    def test_persistence(self, temp_path):
        """Test that FAISS index persists to disk and can be reloaded."""
        # Create and populate a FAISS instance
        db1 = FAISS(
            collection_name="persist_test",
            path=temp_path,
            distance_strategy="cosine",
            embedding_model_dims=384,
        )

        vectors = [[0.1, 0.2, 0.3] + [0.0] * 381]
        payloads = [{"content": "Persisted document"}]
        ids = ["persist_id"]

        db1.insert(vectors=vectors, payloads=payloads, ids=ids)

        # Create a new instance with the same path
        db2 = FAISS(
            collection_name="persist_test",
            path=temp_path,
            distance_strategy="cosine",
            embedding_model_dims=384,
        )

        # Verify data was loaded
        assert db2.index.ntotal == 1
        result = db2.get("persist_id")
        assert result is not None
        assert result.payload["content"] == "Persisted document"


class TestCollectionsLocalVector:
    """Test Collections local vector functionality."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client for testing."""
        client = MagicMock()
        return client

    @pytest.fixture
    def collections_resource(self, mock_client):
        """Create a Collections resource for testing."""
        from mielto.resources.collections import Collections

        return Collections(mock_client)

    def test_get_chunks(self, collections_resource, mock_client):
        """Test getting chunks from a collection."""
        # Mock the API response
        mock_response = {
            "chunks": [
                {
                    "id": "chunk1",
                    "content": "This is the first chunk",
                    "embedding": [0.1] * 384,
                    "metadata": {"page": 1},
                },
                {
                    "id": "chunk2",
                    "content": "This is the second chunk",
                    "embedding": [0.2] * 384,
                    "metadata": {"page": 2},
                },
            ],
            "total": 2,
            "next_cursor": None,
            "has_more": False,
        }
        mock_client.get.return_value = mock_response

        result = collections_resource.get_chunks(collection_id="col_123", limit=100, include_embedding=True)

        assert isinstance(result, ChunksResponse)
        assert len(result.chunks) == 2
        assert result.chunks[0].id == "chunk1"
        assert result.chunks[0].content == "This is the first chunk"
        assert len(result.chunks[0].embedding) == 384
        assert result.has_more is False
        assert result.next_cursor is None

        # Verify the API was called correctly with new endpoint and headers
        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert "/chunks" in call_args[0]
        # Check that headers include X-Collection-Id
        assert call_args[1]["headers"]["X-Collection-Id"] == "col_123"

    @patch("mielto.internals.vectors.faiss.FAISS")
    def test_load_to_local(self, mock_faiss_class, collections_resource, mock_client):
        """Test loading chunks to local FAISS."""
        # Mock collection response
        mock_collection = {
            "id": "col_123",
            "name": "Test Collection",
            "embedding": {"dimension": 384},
            "status": "active",
            "visibility": "private",
            "workspace_id": "ws_123",
        }

        # Mock chunks response with cursor-based pagination
        mock_chunks = {
            "chunks": [
                {
                    "id": "chunk1",
                    "content": "First chunk",
                    "embedding": [0.1] * 384,
                    "metadata": {"source": "doc1"},
                },
                {
                    "id": "chunk2",
                    "content": "Second chunk",
                    "embedding": [0.2] * 384,
                    "metadata": {"source": "doc2"},
                },
            ],
            "total": 2,
            "next_cursor": None,
            "has_more": False,
        }

        mock_client.get.side_effect = [mock_collection, mock_chunks]

        # Mock FAISS instance
        mock_faiss = MagicMock()
        mock_faiss.index = None  # No existing index
        mock_faiss.is_fresh.return_value = False  # Not fresh, needs sync
        mock_faiss_class.return_value = mock_faiss

        result = collections_resource.load(collection_id="col_123", show_progress=False)
        assert result is not None

        # Verify FAISS was created
        mock_faiss_class.assert_called_once()
        assert mock_faiss_class.call_args[1]["collection_name"] == "col_123"
        assert mock_faiss_class.call_args[1]["embedding_model_dims"] == 384

        # Verify vectors were inserted
        mock_faiss.insert.assert_called()
        insert_call = mock_faiss.insert.call_args
        assert len(insert_call[1]["vectors"]) == 2
        assert len(insert_call[1]["ids"]) == 2

        # Verify mark_synced was called
        mock_faiss.mark_synced.assert_called_once_with(total_chunks=2)

    def test_local_query(self, collections_resource):
        """Test local query with FAISS."""
        # Create a mock FAISS instance
        mock_faiss = MagicMock()

        # Mock search results
        from mielto.internals.vectors.faiss import OutputData

        mock_results = [
            OutputData(
                id="chunk1",
                score=0.95,
                payload={"content": "Machine learning", "metadata": {"topic": "ml"}},
            ),
            OutputData(
                id="chunk2",
                score=0.85,
                payload={"content": "Deep learning", "metadata": {"topic": "dl"}},
            ),
        ]
        mock_faiss.search.return_value = mock_results

        query_embedding = [0.5] * 384
        results = collections_resource.query(vector_db=mock_faiss, query_embedding=query_embedding, limit=5)

        assert len(results) == 2
        assert results[0]["id"] == "chunk1"
        assert results[0]["score"] == 0.95
        assert results[0]["content"] == "Machine learning"
        assert results[1]["content"] == "Deep learning"

        # Verify search was called correctly
        mock_faiss.search.assert_called_once()
        call_args = mock_faiss.search.call_args
        assert call_args[1]["limit"] == 5


class TestFAISSConfig:
    """Test FAISS configuration management and drift detection."""

    @pytest.fixture
    def temp_path(self):
        """Create a temporary directory for FAISS storage."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def mock_embedder(self):
        """Create a mock embedder for testing."""

        class MockEmbedder:
            def __init__(self, model_name="mock-model-v1", dims=384):
                self.model_name = model_name
                self._dimensions = dims

            def get_embedding(self, text: str):
                return [0.1] * self._dimensions

            @property
            def dimensions(self):
                return self._dimensions

        return MockEmbedder

    def test_config_creation(self, temp_path, mock_embedder):
        """Test that config is created with FAISS index."""
        embedder = mock_embedder(model_name="test-model-v1", dims=384)

        faiss_db = FAISS(
            collection_name="test_collection",
            path=temp_path,
            distance_strategy="cosine",
            embedding_model_dims=embedder.dimensions,
            collection_id="col_test123",
            embedder=embedder,
        )

        # Check config was created
        config = faiss_db.get_config()
        assert config is not None
        assert config.collection_name == "test_collection"
        assert config.collection_id == "col_test123"
        assert config.embedder_type == "MockEmbedder"
        assert config.embedder_model == "test-model-v1"
        assert config.embedding_dimension == 384
        assert config.distance_strategy == "cosine"
        assert config.re_embedded is True
        assert config.created_at is not None
        assert config.updated_at is not None

    def test_config_persistence(self, temp_path, mock_embedder):
        """Test that config persists across loads."""
        embedder = mock_embedder(model_name="persist-model", dims=384)

        # Create and save
        faiss_db1 = FAISS(
            collection_name="persist_test",
            path=temp_path,
            distance_strategy="cosine",
            embedding_model_dims=embedder.dimensions,
            collection_id="col_persist",
            embedder=embedder,
        )

        # Add some vectors
        vectors = [[0.1] * 384 for _ in range(5)]
        faiss_db1.insert(vectors)

        original_created_at = faiss_db1.config.created_at

        # Load again without embedder
        faiss_db2 = FAISS(
            collection_name="persist_test",
            path=temp_path,
            distance_strategy="cosine",
            embedding_model_dims=384,
        )

        # Check config was loaded
        config2 = faiss_db2.get_config()
        assert config2 is not None
        assert config2.created_at == original_created_at
        assert config2.embedder_type == "MockEmbedder"
        assert config2.embedder_model == "persist-model"

    def test_config_file_exists(self, temp_path, mock_embedder):
        """Test that config file is created on disk."""
        import json
        import os

        embedder = mock_embedder(model_name="file-test", dims=384)

        faiss_db = FAISS(
            collection_name="file_test",
            path=temp_path,
            distance_strategy="cosine",
            embedding_model_dims=embedder.dimensions,
            embedder=embedder,
        )
        assert faiss_db is not None

        # Check config file exists
        config_path = os.path.join(temp_path, "file_test.config.json")
        assert os.path.exists(config_path)

        # Check config file content
        with open(config_path) as f:
            config_data = json.load(f)
            assert config_data["collection_name"] == "file_test"
            assert config_data["embedder_model"] == "file-test"
            assert config_data["embedding_dimension"] == 384

    def test_drift_detection_dimension_change(self, temp_path, mock_embedder):
        """Test drift detection when dimensions change."""
        embedder1 = mock_embedder(model_name="model-v1", dims=384)

        # Create with first embedder
        faiss_db1 = FAISS(
            collection_name="drift_test",
            path=temp_path,
            distance_strategy="cosine",
            embedding_model_dims=embedder1.dimensions,
            embedder=embedder1,
        )
        faiss_db1.insert([[0.1] * 384])

        # Try different embedder with different dimensions
        embedder2 = mock_embedder(model_name="model-v1", dims=768)

        faiss_db2 = FAISS(
            collection_name="drift_test",
            path=temp_path,
            distance_strategy="cosine",
            embedding_model_dims=embedder2.dimensions,
            embedder=embedder2,
        )

        drift = faiss_db2.detect_drift(embedder2)

        assert drift.has_drift is True
        assert drift.severity == "high"
        assert len(drift.changes) > 0

        # Check dimension change was detected
        dimension_changes = [c for c in drift.changes if c["field"] == "embedder_dimensions"]
        assert len(dimension_changes) > 0
        assert dimension_changes[0]["old_value"] == 384
        assert dimension_changes[0]["new_value"] == 768

    def test_drift_detection_model_change(self, temp_path, mock_embedder):
        """Test drift detection when model changes."""
        embedder1 = mock_embedder(model_name="model-v1", dims=384)

        faiss_db1 = FAISS(
            collection_name="model_drift_test",
            path=temp_path,
            distance_strategy="cosine",
            embedding_model_dims=embedder1.dimensions,
            embedder=embedder1,
        )
        faiss_db1.insert([[0.1] * 384])

        # Try different model
        embedder2 = mock_embedder(model_name="model-v2", dims=384)

        faiss_db2 = FAISS(
            collection_name="model_drift_test",
            path=temp_path,
            distance_strategy="cosine",
            embedding_model_dims=embedder2.dimensions,
            embedder=embedder2,
        )

        drift = faiss_db2.detect_drift(embedder2)

        assert drift.has_drift is True
        assert drift.severity == "high"

        # Check model change was detected
        model_changes = [c for c in drift.changes if c["field"] == "embedder_model"]
        assert len(model_changes) > 0
        assert model_changes[0]["old_value"] == "model-v1"
        assert model_changes[0]["new_value"] == "model-v2"

    def test_drift_detection_distance_change(self, temp_path, mock_embedder):
        """Test drift detection when distance strategy changes."""
        embedder = mock_embedder(model_name="model-v1", dims=384)

        # Create with cosine
        faiss_db1 = FAISS(
            collection_name="distance_drift_test",
            path=temp_path,
            distance_strategy="cosine",
            embedding_model_dims=embedder.dimensions,
            embedder=embedder,
        )
        faiss_db1.insert([[0.1] * 384])

        # Reload with euclidean
        faiss_db2 = FAISS(
            collection_name="distance_drift_test",
            path=temp_path,
            distance_strategy="euclidean",
            embedding_model_dims=embedder.dimensions,
            embedder=embedder,
        )

        drift = faiss_db2.detect_drift(embedder)

        assert drift.has_drift is True
        assert drift.severity == "medium"

        # Check distance change was detected
        distance_changes = [c for c in drift.changes if c["field"] == "distance_strategy"]
        assert len(distance_changes) > 0
        assert distance_changes[0]["old_value"] == "cosine"
        assert distance_changes[0]["new_value"] == "euclidean"

    def test_no_drift(self, temp_path, mock_embedder):
        """Test that no drift is detected with same config."""
        embedder1 = mock_embedder(model_name="model-v1", dims=384)

        faiss_db1 = FAISS(
            collection_name="no_drift_test",
            path=temp_path,
            distance_strategy="cosine",
            embedding_model_dims=embedder1.dimensions,
            embedder=embedder1,
        )
        faiss_db1.insert([[0.1] * 384])

        # Reload with same embedder
        embedder2 = mock_embedder(model_name="model-v1", dims=384)

        faiss_db2 = FAISS(
            collection_name="no_drift_test",
            path=temp_path,
            distance_strategy="cosine",
            embedding_model_dims=embedder2.dimensions,
            embedder=embedder2,
        )

        drift = faiss_db2.detect_drift(embedder2)

        assert drift.has_drift is False
        assert drift.severity == "none"
        assert len(drift.changes) == 0

    def test_info_includes_config(self, temp_path, mock_embedder):
        """Test that info includes config data."""
        embedder = mock_embedder(model_name="info-model", dims=384)

        faiss_db = FAISS(
            collection_name="info_test",
            path=temp_path,
            distance_strategy="cosine",
            embedding_model_dims=embedder.dimensions,
            collection_id="col_info123",
            embedder=embedder,
        )
        faiss_db.insert([[0.1] * 384 for _ in range(10)])

        info = faiss_db.info()

        assert "config" in info
        assert info["config"]["collection_id"] == "col_info123"
        assert info["config"]["embedder_type"] == "MockEmbedder"
        assert info["config"]["embedder_model"] == "info-model"
        assert info["config"]["re_embedded"] is True
        assert info["count"] == 10

    def test_delete_removes_config(self, temp_path, mock_embedder):
        """Test that deleting index also removes config file."""
        import os

        embedder = mock_embedder(model_name="delete-test", dims=384)

        faiss_db = FAISS(
            collection_name="delete_test",
            path=temp_path,
            distance_strategy="cosine",
            embedding_model_dims=embedder.dimensions,
            embedder=embedder,
        )
        faiss_db.insert([[0.1] * 384])

        config_path = os.path.join(temp_path, "delete_test.config.json")
        assert os.path.exists(config_path)

        # Delete index
        faiss_db.delete_index()

        # Config file should be deleted
        assert not os.path.exists(config_path)

    def test_config_without_embedder(self, temp_path):
        """Test config creation without embedder (API embeddings)."""
        faiss_db = FAISS(
            collection_name="no_embedder_test",
            path=temp_path,
            distance_strategy="cosine",
            embedding_model_dims=1536,
            collection_id="col_api",
        )

        config = faiss_db.get_config()
        assert config is not None
        assert config.embedder_type is None
        assert config.embedder_model is None
        assert config.re_embedded is False
        assert config.embedding_dimension == 1536


class TestFAISSSync:
    """Test FAISS sync freshness and caching."""

    @pytest.fixture
    def temp_path(self):
        """Create a temporary directory for FAISS storage."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def mock_embedder(self):
        """Create a mock embedder for testing."""

        class MockEmbedder:
            def __init__(self, model_name="mock-model-v1", dims=384):
                self.model_name = model_name
                self._dimensions = dims

            def get_embedding(self, text: str):
                return [0.1] * self._dimensions

            @property
            def dimensions(self):
                return self._dimensions

        return MockEmbedder

    def test_needs_sync_never_synced(self, temp_path, mock_embedder):
        """Test that needs_sync returns True for never-synced index."""
        embedder = mock_embedder()
        faiss_db = FAISS(
            collection_name="never_synced",
            path=temp_path,
            distance_strategy="cosine",
            embedding_model_dims=embedder.dimensions,
            embedder=embedder,
        )

        # Never synced - should need sync
        assert faiss_db.needs_sync() is True
        assert faiss_db.is_fresh() is False

    def test_needs_sync_just_synced(self, temp_path, mock_embedder):
        """Test that needs_sync returns False for freshly synced index."""
        embedder = mock_embedder()
        faiss_db = FAISS(
            collection_name="just_synced",
            path=temp_path,
            distance_strategy="cosine",
            embedding_model_dims=embedder.dimensions,
            embedder=embedder,
        )

        # Add some vectors
        vectors = [[0.1] * 384 for _ in range(5)]
        faiss_db.insert(vectors)

        # Mark as synced
        faiss_db.mark_synced(total_chunks=5)

        # Should not need sync
        assert faiss_db.needs_sync(sync_threshold_hours=24) is False
        assert faiss_db.is_fresh(sync_threshold_hours=24) is True

    def test_needs_sync_threshold(self, temp_path, mock_embedder):
        """Test custom sync threshold."""
        from datetime import datetime, timedelta

        embedder = mock_embedder()
        faiss_db = FAISS(
            collection_name="threshold_test",
            path=temp_path,
            distance_strategy="cosine",
            embedding_model_dims=embedder.dimensions,
            embedder=embedder,
        )

        # Add vectors and mark as synced
        vectors = [[0.1] * 384]
        faiss_db.insert(vectors)
        faiss_db.mark_synced(total_chunks=1)

        # Manually set last_synced_at to 2 days ago
        two_days_ago = datetime.utcnow() - timedelta(days=2)
        faiss_db.config.last_synced_at = two_days_ago.isoformat()
        faiss_db._save_config()

        # Should need sync with 24 hour threshold
        assert faiss_db.needs_sync(sync_threshold_hours=24) is True
        assert faiss_db.is_fresh(sync_threshold_hours=24) is False

        # Should NOT need sync with 72 hour threshold
        assert faiss_db.needs_sync(sync_threshold_hours=72) is False
        assert faiss_db.is_fresh(sync_threshold_hours=72) is True

    def test_mark_synced_updates_config(self, temp_path, mock_embedder):
        """Test that mark_synced updates config properly."""
        embedder = mock_embedder()
        faiss_db = FAISS(
            collection_name="mark_synced_test",
            path=temp_path,
            distance_strategy="cosine",
            embedding_model_dims=embedder.dimensions,
            embedder=embedder,
        )

        # Initial state
        assert faiss_db.config.last_synced_at is None
        assert faiss_db.config.total_chunks == 0

        # Mark as synced
        faiss_db.mark_synced(total_chunks=100)

        # Check updates
        assert faiss_db.config.last_synced_at is not None
        assert faiss_db.config.total_chunks == 100

    def test_mark_synced_persists(self, temp_path, mock_embedder):
        """Test that mark_synced persists across loads."""
        embedder = mock_embedder()

        # Create and sync
        faiss_db1 = FAISS(
            collection_name="persist_sync_test",
            path=temp_path,
            distance_strategy="cosine",
            embedding_model_dims=embedder.dimensions,
            embedder=embedder,
        )
        vectors = [[0.1] * 384 for _ in range(10)]
        faiss_db1.insert(vectors)
        faiss_db1.mark_synced(total_chunks=10)

        last_synced = faiss_db1.config.last_synced_at

        # Reload
        faiss_db2 = FAISS(
            collection_name="persist_sync_test",
            path=temp_path,
            distance_strategy="cosine",
            embedding_model_dims=embedder.dimensions,
        )

        # Check persistence
        assert faiss_db2.config.last_synced_at == last_synced
        assert faiss_db2.config.total_chunks == 10
        assert faiss_db2.is_fresh()

    def test_info_includes_sync_data(self, temp_path, mock_embedder):
        """Test that info includes sync metadata."""
        embedder = mock_embedder()
        faiss_db = FAISS(
            collection_name="info_sync_test",
            path=temp_path,
            distance_strategy="cosine",
            embedding_model_dims=embedder.dimensions,
            collection_id="col_sync123",
            embedder=embedder,
        )

        vectors = [[0.1] * 384 for _ in range(20)]
        faiss_db.insert(vectors)
        faiss_db.mark_synced(total_chunks=20)

        info = faiss_db.info()

        # Check config includes sync data
        assert "config" in info
        # Use .get() with a check to handle both presence and None values
        config = info.get("config", {})
        assert config is not None, "Config should not be None"
        last_synced = config.get("last_synced_at")
        assert last_synced is not None, f"last_synced_at should not be None. Config: {config}"
        assert info["count"] == 20


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
