"""
VectorAlign - Bilingual Word Alignment using Multilingual Embeddings

A spiritual implementation of SimAlign by CIS, LMU Munich.
"""

from .align import align, get_embeddings_batch

__version__ = "0.1.0"
__all__ = ["align", "get_embeddings_batch", "__version__"]
