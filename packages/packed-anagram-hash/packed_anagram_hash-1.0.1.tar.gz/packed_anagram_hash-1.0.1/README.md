# Packed Anagram Hash

**Constant-time anagram comparison using packed bit-width representation.**

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18168195.svg)](https://doi.org/10.5281/zenodo.18168195)
[![PyPI version](https://badge.fury.io/py/packed-anagram-hash.svg)](https://pypi.org/project/packed-anagram-hash/)
[![License: CC0-1.0](https://img.shields.io/badge/License-CC0_1.0-lightgrey.svg)](http://creativecommons.org/publicdomain/zero/1.0/)

## Why?

Standard anagram detection methods have hidden costs:

| Method | Hash Cost | Compare Cost | Key Size |
|--------|-----------|--------------|----------|
| Sorted String | O(n log n) | O(n) | n bytes |
| Count Array | O(n) | O(26) | 104 bytes |
| **Packed Bit-Width** | **O(n)** | **O(1)** | **8 bytes** |

This package provides **26× faster comparison** than count arrays and **n× faster** than sorted strings, with 6-13× smaller keys.

## Installation

```bash
pip install packed-anagram-hash
```

## Quick Start

```python
from packed_anagram_hash import PackedAnagramHasher

# Initialize with your corpus
corpus = ["store", "rotes", "tores", "stare", "rates", "tears"]
hasher = PackedAnagramHasher(corpus)

# Hash words - anagrams produce identical hashes
h1 = hasher.hash("store")
h2 = hasher.hash("rotes")
h3 = hasher.hash("stare")

assert h1 == h2  # True - same letters
assert h1 != h3  # True - different letters

# Group anagrams
groups = hasher.group_anagrams(corpus)
# {hash1: ["store", "rotes", "tores"], hash2: ["stare", "rates", "tears"]}
```

## How It Works

1. **Pre-compute** maximum letter frequency per character in your corpus
2. **Allocate** minimal bits per letter (e.g., 'e' max 4 occurrences → 3 bits)
3. **Pack** into single 64-bit register (~50-60 bits for English)
4. **Hash** by accumulating: `h += (1 << offset[letter])`

Addition commutes, so anagrams produce identical hashes. Comparison is single CPU instruction.

## API Reference

### `PackedAnagramHasher(corpus)`

Initialize hasher with a corpus to determine bit-widths.

**Parameters:**
- `corpus`: Iterable of strings to analyze for letter frequencies

**Attributes:**
- `bit_widths`: List of bits allocated per letter (a-z)
- `offsets`: Bit offset for each letter in the packed hash
- `total_bits`: Total bits used (must be ≤64 for single-register operation)

### `hasher.hash(word) -> int`

Compute packed hash for a word.

**Parameters:**
- `word`: String to hash (case-insensitive, non-alphabetic characters ignored)

**Returns:**
- 64-bit integer hash

### `hasher.group_anagrams(words) -> dict[int, list[str]]`

Group words by anagram equivalence.

**Parameters:**
- `words`: Iterable of strings to group

**Returns:**
- Dictionary mapping hash → list of anagram words

### `hasher.are_anagrams(word1, word2) -> bool`

Check if two words are anagrams.

## Advanced: Multi-Register Extension

For corpora requiring >64 bits (extremely long words or large alphabets), the algorithm extends to multiple registers. See the [paper](https://doi.org/10.5281/zenodo.18168195) for details.

## Citation

If you use this in academic work:

```bibtex
@software{brown_2025_packed_anagram,
  author       = {Brown, Nicholas David},
  title        = {Packed Bit-Width Anagram Hashing: A Constant-Time 
                  Comparison Algorithm for Anagram Equivalence},
  year         = 2025,
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.18168195},
  url          = {https://doi.org/10.5281/zenodo.18168195}
}
```

## License

CC0 1.0 Universal - Public Domain. Use freely.
