from enum import Enum


class VectorStore(str, Enum):
    """Vector database types."""

    FAISS = "faiss"
    MOSS = "moss"
