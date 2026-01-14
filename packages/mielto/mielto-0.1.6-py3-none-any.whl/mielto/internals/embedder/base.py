"""Embedder protocol for local vector operations.

This module defines a simple protocol that users can implement to provide
custom embedding functionality for local vector operations.

Users can implement this protocol with any embedding library:
- FastEmbed
- Sentence Transformers
- OpenAI
- Cohere
- Custom implementations
"""

from typing import List, Protocol, runtime_checkable


@runtime_checkable
class Embedder(Protocol):
    """Protocol for embedding functions.

    Any object that implements this protocol can be used as an embedder
    for local vector operations (loading and querying).

    Example:
        ```python
        from fastembed import TextEmbedding

        class MyEmbedder:
            def __init__(self):
                self.model = TextEmbedding("BAAI/bge-small-en-v1.5")
                self._dimensions = 384

            def get_embedding(self, text: str) -> List[float]:
                embeddings = self.model.embed(text)
                return list(list(embeddings)[0])

            @property
            def dimensions(self) -> int:
                return self._dimensions

        # Use with mielto
        embedder = MyEmbedder()
        local_db = client.collections.load(
            collection_id="col_123",
            embedder=embedder,
            re_embed=True
        )
        ```
    """

    def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for a text string.

        Args:
            text: Text to embed

        Returns:
            List of floats representing the embedding vector
        """
        ...

    @property
    def dimensions(self) -> int:
        """Return the dimensionality of embeddings produced.

        Returns:
            Integer representing embedding dimensions (e.g., 384, 1536)
        """
        ...


def is_embedder(obj) -> bool:
    """Check if an object implements the Embedder protocol.

    Args:
        obj: Object to check

    Returns:
        True if object implements Embedder protocol
    """
    return hasattr(obj, "get_embedding") and callable(obj.get_embedding) and hasattr(obj, "dimensions")
