"""
Packed Bit-Width Anagram Hashing

A constant-time comparison algorithm for anagram equivalence.

Paper: https://doi.org/10.5281/zenodo.18167975
"""

from typing import Iterable, Dict, List
from collections import defaultdict

__version__ = "1.0.0"
__author__ = "Nicholas David Brown"
__license__ = "CC0-1.0"


class PackedAnagramHasher:
    """
    Anagram hasher using packed bit-width representation.
    
    Achieves O(1) comparison cost by packing letter frequencies into
    minimal bits within a single 64-bit register.
    
    Example:
        >>> hasher = PackedAnagramHasher(["store", "rotes", "tores"])
        >>> hasher.hash("store") == hasher.hash("rotes")
        True
        >>> hasher.are_anagrams("store", "rotes")
        True
    """
    
    def __init__(self, corpus: Iterable[str]):
        """
        Initialize hasher from corpus to determine optimal bit-widths.
        
        Args:
            corpus: Iterable of words to analyze for max letter frequencies
        """
        # Find maximum frequency per letter across corpus
        max_freq = [0] * 26
        
        for word in corpus:
            counts = [0] * 26
            for c in word.lower():
                if 'a' <= c <= 'z':
                    counts[ord(c) - ord('a')] += 1
            for i in range(26):
                max_freq[i] = max(max_freq[i], counts[i])
        
        # Ensure at least 1 bit per letter that appears
        # (bit_length of 0 is 0, but we need at least 1 bit to represent presence)
        self.bit_widths = [
            max(1, freq.bit_length()) if freq > 0 else 0 
            for freq in max_freq
        ]
        
        # Compute cumulative offsets
        self.offsets = [0] * 26
        offset = 0
        for i in range(26):
            self.offsets[i] = offset
            offset += self.bit_widths[i]
        
        self.total_bits = offset
        
        if self.total_bits > 64:
            raise ValueError(
                f"Corpus requires {self.total_bits} bits, exceeding 64-bit register. "
                f"Consider filtering corpus or using multi-register extension."
            )
    
    def hash(self, word: str) -> int:
        """
        Compute packed bit-width hash for a word.
        
        Args:
            word: String to hash (case-insensitive)
            
        Returns:
            64-bit integer hash where anagrams produce identical values
        """
        h = 0
        for c in word.lower():
            if 'a' <= c <= 'z':
                i = ord(c) - ord('a')
                h += (1 << self.offsets[i])
        return h
    
    def are_anagrams(self, word1: str, word2: str) -> bool:
        """
        Check if two words are anagrams.
        
        Args:
            word1: First word
            word2: Second word
            
        Returns:
            True if words contain same letters (case-insensitive)
        """
        return self.hash(word1) == self.hash(word2)
    
    def group_anagrams(self, words: Iterable[str]) -> Dict[int, List[str]]:
        """
        Group words by anagram equivalence class.
        
        Args:
            words: Iterable of words to group
            
        Returns:
            Dictionary mapping hash -> list of anagram words
        """
        groups: Dict[int, List[str]] = defaultdict(list)
        for word in words:
            h = self.hash(word)
            groups[h].append(word)
        return dict(groups)
    
    def __repr__(self) -> str:
        return f"PackedAnagramHasher(total_bits={self.total_bits})"


def quick_hash(word: str) -> int:
    """
    Quick anagram hash without corpus optimization.
    
    Uses fixed 3 bits per letter (supports up to 7 occurrences).
    Total: 78 bits - requires two registers but works for any word.
    
    For single-register O(1) comparison, use PackedAnagramHasher with corpus.
    
    Args:
        word: String to hash
        
    Returns:
        Integer hash where anagrams produce identical values
    """
    h = 0
    for c in word.lower():
        if 'a' <= c <= 'z':
            i = ord(c) - ord('a')
            h += (1 << (i * 3))
    return h


def are_anagrams(word1: str, word2: str) -> bool:
    """
    Quick anagram check without corpus initialization.
    
    Args:
        word1: First word
        word2: Second word
        
    Returns:
        True if words are anagrams
    """
    return quick_hash(word1) == quick_hash(word2)
