"""FastEmbed embedder implementation.

This is an optional convenience implementation. Users can use this directly
or create their own embedder implementations.

Install: pip install fastembed
"""

from typing import List

try:
    from fastembed import TextEmbedding
except ImportError:
    raise ImportError("fastembed is not installed. Install it with: pip install fastembed")


class FastEmbedEmbedder:
    """Embedder using FastEmbed (lightweight, CPU-optimized).

    FastEmbed provides fast, lightweight embeddings optimized for CPU inference.
    Ideal for local/offline use cases.

    Args:
        model_name: Name of the FastEmbed model to use
                   Default: "BAAI/bge-small-en-v1.5" (384 dimensions)
                   See https://qdrant.github.io/fastembed/ for available models

    Example:
        ```python
        from mielto import Mielto
        from mielto.internals.embedder import FastEmbedEmbedder

        client = Mielto(api_key="your-api-key")
        embedder = FastEmbedEmbedder()

        # Load with re-embedding
        local_db = client.collections.load(
            collection_id="col_123",
            embedder=embedder,
            re_embed=True
        )

        # Query with text
        results = client.collections.query(
            vector_db=local_db,
            query_text="What is machine learning?",
            embedder=embedder,
            limit=10
        )
        ```
    """

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        self.model_name = model_name
        self.model = TextEmbedding(model_name=model_name)

        # Set dimensions based on model
        # Most common FastEmbed models use 384 dimensions
        self._dimensions = self._get_model_dimensions(model_name)

    def _get_model_dimensions(self, model_name: str) -> int:
        """Get embedding dimensions for the model."""
        # Map common models to their dimensions
        model_dims = {
            "BAAI/bge-small-en-v1.5": 384,
            "BAAI/bge-base-en-v1.5": 768,
            "sentence-transformers/all-MiniLM-L6-v2": 384,
        }
        return model_dims.get(model_name, 384)  # Default to 384

    def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for a text string.

        Args:
            text: Text to embed

        Returns:
            List of floats representing the embedding vector
        """
        embeddings = self.model.embed(text)
        embedding_list = list(embeddings)[0]

        # Convert numpy array to list if needed
        if hasattr(embedding_list, "tolist"):
            return embedding_list.tolist()
        return list(embedding_list)

    @property
    def dimensions(self) -> int:
        """Return the dimensionality of embeddings produced.

        Returns:
            Integer representing embedding dimensions (e.g., 384, 768)
        """
        return self._dimensions
