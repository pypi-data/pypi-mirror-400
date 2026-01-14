"""Embedder module for local vector operations."""

from mielto.internals.embedder.base import Embedder, is_embedder

# Optional: Export FastEmbedEmbedder if fastembed is installed
try:
    from mielto.internals.embedder.fast_embed import FastEmbedEmbedder

    __all__ = ["Embedder", "is_embedder", "FastEmbedEmbedder"]
except ImportError:
    # FastEmbed not installed, only export protocol
    __all__ = ["Embedder", "is_embedder"]
