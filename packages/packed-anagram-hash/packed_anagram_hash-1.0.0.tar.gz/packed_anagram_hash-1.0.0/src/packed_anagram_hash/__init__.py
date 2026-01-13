"""
Packed Anagram Hash - Constant-time anagram comparison.

Paper: https://doi.org/10.5281/zenodo.18167975

Example:
    >>> from packed_anagram_hash import PackedAnagramHasher
    >>> hasher = PackedAnagramHasher(["store", "rotes", "tores"])
    >>> hasher.are_anagrams("store", "rotes")
    True
    
Quick usage without corpus:
    >>> from packed_anagram_hash import are_anagrams
    >>> are_anagrams("listen", "silent")
    True
"""

from .hasher import (
    PackedAnagramHasher,
    quick_hash,
    are_anagrams,
    __version__,
    __author__,
    __license__,
)

__all__ = [
    "PackedAnagramHasher",
    "quick_hash", 
    "are_anagrams",
    "__version__",
    "__author__",
    "__license__",
]
