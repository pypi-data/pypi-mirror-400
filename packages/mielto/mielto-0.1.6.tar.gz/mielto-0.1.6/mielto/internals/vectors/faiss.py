import json
import logging
import os
import pickle
import uuid
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel

try:
    import numpy as np
except ImportError:
    raise ImportError("numpy not installed, use `pip install numpy`")

try:
    # Suppress SWIG deprecation warnings from FAISS
    warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*SwigPy.*")
    warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*swigvarlink.*")

    logging.getLogger("faiss").setLevel(logging.WARNING)
    logging.getLogger("faiss.loader").setLevel(logging.WARNING)

    import faiss
except ImportError:
    raise ImportError(
        "Could not import faiss python package. "
        "Please install it with `pip install faiss-gpu` (for CUDA supported GPU) "
        "or `pip install faiss-cpu` (depending on Python version)."
    )

from mielto.internals.vectors.base import VectorDB

logger = logging.getLogger(__name__)


class FAISSConfig(BaseModel):
    """Configuration for a FAISS collection."""

    collection_name: str
    collection_id: Optional[str] = None
    embedding_dimension: int
    distance_strategy: str
    normalize_L2: bool  # noqa: N815
    embedder_type: Optional[str] = None  # e.g., "FastEmbedEmbedder", "OpenAI", "Custom"
    embedder_model: Optional[str] = None  # e.g., "BAAI/bge-small-en-v1.5", "text-embedding-ada-002"
    re_embedded: bool = False  # Whether content was re-embedded locally
    created_at: str  # ISO format timestamp
    updated_at: str  # ISO format timestamp
    last_synced_at: Optional[str] = None  # Last sync with remote API
    total_chunks: Optional[int] = None  # Number of chunks synced
    version: str = "1.0.0"  # Config version for future compatibility


class ConfigDrift(BaseModel):
    """Represents detected drift in configuration."""

    has_drift: bool
    changes: List[Dict[str, Any]]
    severity: str  # "none", "low", "medium", "high"


class OutputData(BaseModel):
    id: Optional[str]  # chunk id
    score: Optional[float]  # distance
    payload: Optional[Dict]  # metadata


class FAISS(VectorDB):
    def __init__(
        self,
        collection_name: str,
        path: Optional[str] = None,
        distance_strategy: str = "euclidean",
        normalize_L2: bool = False,  # noqa: N803
        embedding_model_dims: int = 1536,
        collection_id: Optional[str] = None,
        embedder: Optional[Any] = None,
    ):
        """
        Initialize the FAISS vector store.

        Args:
            collection_name (str): Name of the collection.
            path (str, optional): Path for local FAISS database. Defaults to None.
            distance_strategy (str, optional): Distance strategy to use. Options: 'euclidean', 'inner_product', 'cosine'.
                Defaults to "euclidean".
            normalize_L2 (bool, optional): Whether to normalize L2 vectors. Only applicable for euclidean distance.
                Defaults to False.
            embedding_model_dims (int, optional): Dimension of embeddings. Defaults to 1536.
            collection_id (str, optional): Remote collection ID if loaded from API.
            embedder (Any, optional): Embedder instance used for local embedding.
        """
        self.collection_name = collection_name
        self.collection_id = collection_id
        self.path = path or f"/.mielto/vectors/faiss/{collection_name}"
        self.distance_strategy = distance_strategy
        self.normalize_L2 = normalize_L2
        self.embedding_model_dims = embedding_model_dims
        self.embedder = embedder

        # Initialize storage structures
        self.index = None
        self.docstore = {}
        self.index_to_id = {}
        self.config: Optional[FAISSConfig] = None

        # Create directory if it doesn't exist
        if self.path:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)

            # Try to load existing index if available
            index_path = f"{self.path}/{collection_name}.faiss"
            docstore_path = f"{self.path}/{collection_name}.pkl"

            if os.path.exists(index_path) and os.path.exists(docstore_path):
                self._load(index_path, docstore_path)
                # Check for config drift if embedder is provided
                if embedder and self.config:
                    drift = self.detect_drift(embedder)
                    if drift.has_drift:
                        self._log_drift_warning(drift)
            else:
                self.create(collection_name)

    def _load(self, index_path: str, docstore_path: str):
        """
        Load FAISS index, docstore, and config from disk.

        Args:
            index_path (str): Path to FAISS index file.
            docstore_path (str): Path to docstore pickle file.
        """
        try:
            self.index = faiss.read_index(index_path)
            with open(docstore_path, "rb") as f:
                self.docstore, self.index_to_id = pickle.load(f)

            # Derive config path from index path
            config_path = index_path.replace(".faiss", ".config.json")

            # Load config if it exists
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    config_data = json.load(f)
                    self.config = FAISSConfig(**config_data)
                logger.info(
                    f"Loaded FAISS index from {index_path} with {self.index.ntotal} vectors "
                    f"(created: {self.config.created_at})"
                )
            else:
                logger.warning(f"Config file not found at {config_path}. Creating new config.")
                self._create_config()
                self._save_config()
                logger.info(f"Loaded FAISS index from {index_path} with {self.index.ntotal} vectors")
        except Exception as e:
            logger.warning(f"Failed to load FAISS index: {e}")
            self.docstore = {}
            self.index_to_id = {}
            self.config = None

    def _save(self):
        """Save FAISS index, docstore, and config to disk."""
        if not self.path or not self.index:
            return

        try:
            os.makedirs(self.path, exist_ok=True)
            index_path = f"{self.path}/{self.collection_name}.faiss"
            docstore_path = f"{self.path}/{self.collection_name}.pkl"

            faiss.write_index(self.index, index_path)
            with open(docstore_path, "wb") as f:
                pickle.dump((self.docstore, self.index_to_id), f)

            # Update and save config
            if self.config:
                self.config.updated_at = datetime.utcnow().isoformat()
            self._save_config()
        except Exception as e:
            logger.warning(f"Failed to save FAISS index: {e}")

    def _create_config(self):
        """Create a new config based on current settings."""
        # Extract embedder information if available
        embedder_type = None
        embedder_model = None
        re_embedded = False

        if self.embedder:
            re_embedded = True
            embedder_type = type(self.embedder).__name__
            # Try to extract model name if available
            if hasattr(self.embedder, "model_name"):
                embedder_model = self.embedder.model_name
            elif hasattr(self.embedder, "model"):
                if hasattr(self.embedder.model, "model_name"):
                    embedder_model = self.embedder.model.model_name
                elif hasattr(self.embedder.model, "_name_or_path"):
                    embedder_model = self.embedder.model._name_or_path

        now = datetime.utcnow().isoformat()
        self.config = FAISSConfig(
            collection_name=self.collection_name,
            collection_id=self.collection_id,
            embedding_dimension=self.embedding_model_dims,
            distance_strategy=self.distance_strategy,
            normalize_L2=self.normalize_L2,
            embedder_type=embedder_type,
            embedder_model=embedder_model,
            re_embedded=re_embedded,
            created_at=now,
            updated_at=now,
            last_synced_at=None,
            total_chunks=0,
        )

    def _save_config(self):
        """Save config to disk."""
        if not self.path or not self.config:
            return

        try:
            config_path = f"{self.path}/{self.collection_name}.config.json"
            with open(config_path, "w") as f:
                json.dump(self.config.model_dump(), f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save config: {e}")

    def _get_embedder_info(self, embedder: Any) -> Tuple[Optional[str], Optional[str]]:
        """Extract embedder type and model name from embedder instance.

        Args:
            embedder: Embedder instance

        Returns:
            Tuple of (embedder_type, embedder_model)
        """
        embedder_type = type(embedder).__name__
        embedder_model = None

        # Try to extract model name
        if hasattr(embedder, "model_name"):
            embedder_model = embedder.model_name
        elif hasattr(embedder, "model"):
            if hasattr(embedder.model, "model_name"):
                embedder_model = embedder.model.model_name
            elif hasattr(embedder.model, "_name_or_path"):
                embedder_model = embedder.model._name_or_path

        return embedder_type, embedder_model

    def detect_drift(self, embedder: Optional[Any] = None) -> ConfigDrift:
        """Detect configuration drift between current settings and saved config.

        Args:
            embedder: Optional embedder to check against saved config

        Returns:
            ConfigDrift object with drift information
        """
        if not self.config:
            return ConfigDrift(
                has_drift=False,
                changes=[],
                severity="none",
            )

        changes = []
        severity = "none"

        # Check dimension drift (HIGH severity - data incompatibility)
        if self.embedding_model_dims != self.config.embedding_dimension:
            changes.append(
                {
                    "field": "embedding_dimension",
                    "old_value": self.config.embedding_dimension,
                    "new_value": self.embedding_model_dims,
                    "severity": "high",
                    "impact": "Vectors are incompatible due to dimension mismatch",
                }
            )
            severity = "high"

        # Check distance strategy drift (MEDIUM severity - affects results)
        if self.distance_strategy != self.config.distance_strategy:
            changes.append(
                {
                    "field": "distance_strategy",
                    "old_value": self.config.distance_strategy,
                    "new_value": self.distance_strategy,
                    "severity": "medium",
                    "impact": "Search results will use different similarity metric",
                }
            )
            if severity != "high":
                severity = "medium"

        # Check normalization drift (LOW-MEDIUM severity)
        if self.normalize_L2 != self.config.normalize_L2:
            changes.append(
                {
                    "field": "normalize_L2",
                    "old_value": self.config.normalize_L2,
                    "new_value": self.normalize_L2,
                    "severity": "medium",
                    "impact": "Vector normalization setting has changed",
                }
            )
            if severity not in ["high", "medium"]:
                severity = "medium"

        # Check embedder drift (HIGH severity if model changed)
        if embedder:
            embedder_type, embedder_model = self._get_embedder_info(embedder)

            if embedder_type != self.config.embedder_type:
                changes.append(
                    {
                        "field": "embedder_type",
                        "old_value": self.config.embedder_type,
                        "new_value": embedder_type,
                        "severity": "high",
                        "impact": "Different embedder type will produce incompatible vectors",
                    }
                )
                severity = "high"

            if embedder_model and embedder_model != self.config.embedder_model:
                changes.append(
                    {
                        "field": "embedder_model",
                        "old_value": self.config.embedder_model,
                        "new_value": embedder_model,
                        "severity": "high",
                        "impact": "Different embedder model will produce incompatible vectors",
                    }
                )
                severity = "high"

            # Check dimensions from embedder
            if hasattr(embedder, "dimensions"):
                if embedder.dimensions != self.config.embedding_dimension:
                    changes.append(
                        {
                            "field": "embedder_dimensions",
                            "old_value": self.config.embedding_dimension,
                            "new_value": embedder.dimensions,
                            "severity": "high",
                            "impact": "Embedder produces different dimension vectors",
                        }
                    )
                    severity = "high"

        return ConfigDrift(
            has_drift=len(changes) > 0,
            changes=changes,
            severity=severity,
        )

    def _log_drift_warning(self, drift: ConfigDrift):
        """Log drift warnings to help users identify configuration issues.

        Args:
            drift: ConfigDrift object with detected changes
        """
        if not drift.has_drift:
            return

        logger.warning("=" * 80)
        logger.warning(f"Configuration drift detected! Severity: {drift.severity.upper()}")
        logger.warning(f"Collection: {self.collection_name}")
        logger.warning("-" * 80)

        for change in drift.changes:
            logger.warning(f"Field: {change['field']}")
            logger.warning(f"  Old value: {change['old_value']}")
            logger.warning(f"  New value: {change['new_value']}")
            logger.warning(f"  Impact: {change['impact']}")
            logger.warning("-" * 80)

        if drift.severity == "high":
            logger.warning(
                "HIGH SEVERITY: The index may not work correctly with current settings. "
                "Consider recreating the index or reverting to original configuration."
            )
        elif drift.severity == "medium":
            logger.warning(
                "MEDIUM SEVERITY: Search results may differ from original configuration. Review changes carefully."
            )

        logger.warning("=" * 80)

    def get_config(self) -> Optional[FAISSConfig]:
        """Get the current configuration.

        Returns:
            FAISSConfig object or None if not loaded
        """
        return self.config

    def needs_sync(self, sync_threshold_hours: int = 24) -> bool:
        """Check if index needs to be synced with remote.

        Args:
            sync_threshold_hours: Number of hours after which sync is needed

        Returns:
            True if sync is needed, False if index is recent enough
        """
        if not self.config or not self.config.last_synced_at:
            return True  # No config or never synced - needs sync

        from datetime import timedelta

        last_synced = datetime.fromisoformat(self.config.last_synced_at)
        threshold = datetime.utcnow() - timedelta(hours=sync_threshold_hours)

        return last_synced < threshold  # True if last sync was before threshold

    def is_fresh(self, sync_threshold_hours: int = 24) -> bool:
        """Check if index is fresh (recently synced).

        Args:
            sync_threshold_hours: Number of hours to consider index fresh

        Returns:
            True if index is fresh and doesn't need syncing
        """
        return not self.needs_sync(sync_threshold_hours)

    def mark_synced(self, total_chunks: int):
        """Mark the index as synced with remote.

        Args:
            total_chunks: Total number of chunks synced
        """
        if self.config:
            self.config.last_synced_at = datetime.utcnow().isoformat()
            self.config.total_chunks = total_chunks
            self.config.updated_at = datetime.utcnow().isoformat()
            self._save_config()
            logger.info(f"Marked index as synced: {total_chunks} chunks at {self.config.last_synced_at}")

    def _parse_output(self, scores, ids, limit=None) -> List[OutputData]:
        """
        Parse the output data.

        Args:
            scores: Similarity scores from FAISS.
            ids: Indices from FAISS.
            limit: Maximum number of results to return.

        Returns:
            List[OutputData]: Parsed output data.
        """
        if limit is None:
            limit = len(ids)

        results = []
        for i in range(min(len(ids), limit)):
            if ids[i] == -1:  # FAISS returns -1 for empty results
                continue

            index_id = int(ids[i])
            vector_id = self.index_to_id.get(index_id)
            if vector_id is None:
                continue

            payload = self.docstore.get(vector_id)
            if payload is None:
                continue

            payload_copy = payload.copy()

            score = float(scores[i])
            entry = OutputData(
                id=vector_id,
                score=score,
                payload=payload_copy,
            )
            results.append(entry)

        return results

    def create(self, name: str, distance: str = None):
        """
        Create a new vector index.

        Args:
            name (str): Name of the collection.
            distance (str, optional): Distance metric to use. Overrides the distance_strategy
                passed during initialization. Defaults to None.

        Returns:
            self: The FAISS instance.
        """
        distance_strategy = distance or self.distance_strategy
        self.distance_strategy = distance_strategy

        # Create index based on distance strategy
        if distance_strategy.lower() == "inner_product" or distance_strategy.lower() == "cosine":
            self.index = faiss.IndexFlatIP(self.embedding_model_dims)
        else:
            self.index = faiss.IndexFlatL2(self.embedding_model_dims)

        self.collection_name = name

        # Create config
        self._create_config()

        self._save()

        return self

    def insert(
        self,
        vectors: List[list],
        payloads: Optional[List[Dict]] = None,
        ids: Optional[List[str]] = None,
    ):
        """
        Insert vectors into a collection.

        Args:
            vectors (List[list]): List of vectors to insert.
            payloads (Optional[List[Dict]], optional): List of payloads corresponding to vectors. Defaults to None.
            ids (Optional[List[str]], optional): List of IDs corresponding to vectors. Defaults to None.
        """
        if self.index is None:
            raise ValueError("Collection not initialized. Call create first.")

        if ids is None:
            ids = [str(uuid.uuid4()) for _ in range(len(vectors))]

        if payloads is None:
            payloads = [{} for _ in range(len(vectors))]

        if len(vectors) != len(ids) or len(vectors) != len(payloads):
            raise ValueError("Vectors, payloads, and IDs must have the same length")

        vectors_np = np.array(vectors, dtype=np.float32)

        if self.normalize_L2 and self.distance_strategy.lower() == "euclidean":
            faiss.normalize_L2(vectors_np)

        self.index.add(vectors_np)

        starting_idx = len(self.index_to_id)
        for i, (vector_id, payload) in enumerate(zip(ids, payloads)):
            self.docstore[vector_id] = payload.copy()
            self.index_to_id[starting_idx + i] = vector_id

        self._save()

        logger.info(f"Inserted {len(vectors)} vectors into collection {self.collection_name}")

    def search(
        self, query: str, vectors: List[list], limit: int = 5, filters: Optional[Dict] = None
    ) -> List[OutputData]:
        """
        Search for similar vectors.

        Args:
            query (str): Query (not used, kept for API compatibility).
            vectors (List[list]): List of vectors to search.
            limit (int, optional): Number of results to return. Defaults to 5.
            filters (Optional[Dict], optional): Filters to apply to the search. Defaults to None.

        Returns:
            List[OutputData]: Search results.
        """
        if self.index is None:
            raise ValueError("Collection not initialized. Call create first.")

        query_vectors = np.array(vectors, dtype=np.float32)

        if len(query_vectors.shape) == 1:
            query_vectors = query_vectors.reshape(1, -1)

        if self.normalize_L2 and self.distance_strategy.lower() == "euclidean":
            faiss.normalize_L2(query_vectors)

        fetch_k = limit * 2 if filters else limit
        scores, indices = self.index.search(query_vectors, fetch_k)

        results = self._parse_output(scores[0], indices[0], limit)

        if filters:
            filtered_results = []
            for result in results:
                if self._apply_filters(result.payload, filters):
                    filtered_results.append(result)
                    if len(filtered_results) >= limit:
                        break
            results = filtered_results[:limit]

        return results

    def _apply_filters(self, payload: Dict, filters: Dict) -> bool:
        """
        Apply filters to a payload.

        Args:
            payload (Dict): Payload to filter.
            filters (Dict): Filters to apply.

        Returns:
            bool: True if payload passes filters, False otherwise.
        """
        if not filters or not payload:
            return True

        for key, value in filters.items():
            if key not in payload:
                return False

            if isinstance(value, list):
                if payload[key] not in value:
                    return False
            elif payload[key] != value:
                return False

        return True

    def delete(self, vector_id: str):
        """
        Delete a vector by ID.

        Args:
            vector_id (str): ID of the vector to delete.
        """
        if self.index is None:
            raise ValueError("Collection not initialized. Call create first.")

        index_to_delete = None
        for idx, vid in self.index_to_id.items():
            if vid == vector_id:
                index_to_delete = idx
                break

        if index_to_delete is not None:
            self.docstore.pop(vector_id, None)
            self.index_to_id.pop(index_to_delete, None)

            self._save()

            logger.info(f"Deleted vector {vector_id} from collection {self.collection_name}")
        else:
            logger.warning(f"Vector {vector_id} not found in collection {self.collection_name}")

    def update(
        self,
        vector_id: str,
        vector: Optional[List[float]] = None,
        payload: Optional[Dict] = None,
    ):
        """
        Update a vector and its payload.

        Args:
            vector_id (str): ID of the vector to update.
            vector (Optional[List[float]], optional): Updated vector. Defaults to None.
            payload (Optional[Dict], optional): Updated payload. Defaults to None.
        """
        if self.index is None:
            raise ValueError("Collection not initialized. Call create first.")

        if vector_id not in self.docstore:
            raise ValueError(f"Vector {vector_id} not found")

        current_payload = self.docstore[vector_id].copy()

        if payload is not None:
            self.docstore[vector_id] = payload.copy()
            current_payload = self.docstore[vector_id].copy()

        if vector is not None:
            self.delete(vector_id)
            self.insert([vector], [current_payload], [vector_id])
        else:
            self._save()

        logger.info(f"Updated vector {vector_id} in collection {self.collection_name}")

    def get(self, vector_id: str) -> OutputData:
        """
        Retrieve a vector by ID.

        Args:
            vector_id (str): ID of the vector to retrieve.

        Returns:
            OutputData: Retrieved vector.
        """
        if self.index is None:
            raise ValueError("Collection not initialized. Call create first.")

        if vector_id not in self.docstore:
            return None

        payload = self.docstore[vector_id].copy()

        return OutputData(
            id=vector_id,
            score=None,
            payload=payload,
        )

    def list_indexes(self) -> List[str]:
        """
        List all vector indexes.

        Returns:
            List[str]: List of vector index names.
        """
        if not self.path:
            return [self.collection_name] if self.index else []

        try:
            collections = []
            path = Path(self.path).parent
            for file in path.glob("*.faiss"):
                collections.append(file.stem)
            return collections
        except Exception as e:
            logger.warning(f"Failed to list collections: {e}")
            return [self.collection_name] if self.index else []

    def delete_index(self):
        """
        Delete a vector index and its config.
        """
        if self.path:
            try:
                index_path = f"{self.path}/{self.collection_name}.faiss"
                docstore_path = f"{self.path}/{self.collection_name}.pkl"
                config_path = f"{self.path}/{self.collection_name}.config.json"

                if os.path.exists(index_path):
                    os.remove(index_path)
                if os.path.exists(docstore_path):
                    os.remove(docstore_path)
                if os.path.exists(config_path):
                    os.remove(config_path)

                logger.info(f"Deleted collection {self.collection_name}")
            except Exception as e:
                logger.warning(f"Failed to delete collection: {e}")

        self.index = None
        self.docstore = {}
        self.index_to_id = {}
        self.config = None

    def info(self) -> Dict:
        """
        Get information about a vector index including config.

        Returns:
            Dict: Vector index information including configuration details.
        """
        if self.index is None:
            return {"name": self.collection_name, "count": 0}

        info_dict = {
            "name": self.collection_name,
            "count": self.index.ntotal,
            "dimension": self.index.d,
            "distance": self.distance_strategy,
        }

        # Add config information if available
        if self.config:
            info_dict["config"] = {
                "collection_id": self.config.collection_id,
                "embedder_type": self.config.embedder_type,
                "embedder_model": self.config.embedder_model,
                "re_embedded": self.config.re_embedded,
                "created_at": self.config.created_at,
                "updated_at": self.config.updated_at,
                "last_synced_at": self.config.last_synced_at,
                "total_chunks": self.config.total_chunks,
                "normalize_L2": self.config.normalize_L2,
            }

        return info_dict

    def list(self, filters: Optional[Dict] = None, limit: int = 100) -> List[OutputData]:
        """
        List all vectors in a collection.

        Args:
            filters (Optional[Dict], optional): Filters to apply to the list. Defaults to None.
            limit (int, optional): Number of vectors to return. Defaults to 100.

        Returns:
            List[OutputData]: List of vectors.
        """
        if self.index is None:
            return []

        results = []
        count = 0

        for vector_id, payload in self.docstore.items():
            if filters and not self._apply_filters(payload, filters):
                continue

            payload_copy = payload.copy()

            results.append(
                OutputData(
                    id=vector_id,
                    score=None,
                    payload=payload_copy,
                )
            )

            count += 1
            if count >= limit:
                break

        return [results]

    def reset(self):
        """Reset the index by deleting and recreating it."""
        logger.warning(f"Resetting index {self.collection_name}...")
        self.delete_index()
        self.create(self.collection_name)
