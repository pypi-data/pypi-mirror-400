"""Mielto Python Client Library.

Official Python client for interacting with the Mielto API.
"""

from mielto.client.async_mielto import AsyncMielto
from mielto.client.mielto import Mielto

__version__ = "0.1.1"
__all__ = ["Mielto", "AsyncMielto"]


def get_faiss():
    """Lazy import FAISS to avoid requiring it if not used."""
    from mielto.internals.vectors.faiss import FAISS

    return FAISS
