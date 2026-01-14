"""Vector database implementations."""

from mielto.internals.vectors.base import VectorDB
from mielto.internals.vectors.enum import VectorStore

__all__ = ["VectorDB", "VectorStore"]

# Optional FAISS import - only available if faiss-cpu/faiss-gpu is installed
try:
    from mielto.internals.vectors.faiss import FAISS

    __all__.append("FAISS")
except ImportError:
    FAISS = None  # type: ignore
