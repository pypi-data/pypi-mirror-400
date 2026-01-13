"""Tests for packed_anagram_hash."""

import pytest
from packed_anagram_hash import PackedAnagramHasher, are_anagrams, quick_hash


class TestPackedAnagramHasher:
    """Tests for the corpus-optimized hasher."""
    
    @pytest.fixture
    def sample_corpus(self):
        return [
            "store", "rotes", "tores", "stroe",
            "stare", "rates", "tears", "aster",
            "listen", "silent", "enlist",
            "cat", "act", "tac",
            "dog",
            "aaa", "aa", "a",
        ]
    
    @pytest.fixture
    def hasher(self, sample_corpus):
        return PackedAnagramHasher(sample_corpus)
    
    def test_anagrams_same_hash(self, hasher):
        """Anagrams should produce identical hashes."""
        assert hasher.hash("store") == hasher.hash("rotes")
        assert hasher.hash("store") == hasher.hash("tores")
        assert hasher.hash("listen") == hasher.hash("silent")
        assert hasher.hash("cat") == hasher.hash("act")
    
    def test_non_anagrams_different_hash(self, hasher):
        """Non-anagrams should produce different hashes."""
        assert hasher.hash("store") != hasher.hash("stare")
        assert hasher.hash("cat") != hasher.hash("dog")
        assert hasher.hash("listen") != hasher.hash("store")
    
    def test_repeated_letters_distinguished(self, hasher):
        """Words with different letter counts should differ."""
        assert hasher.hash("aaa") != hasher.hash("aa")
        assert hasher.hash("aa") != hasher.hash("a")
        assert hasher.hash("aaa") != hasher.hash("a")
    
    def test_case_insensitive(self, hasher):
        """Hashing should be case-insensitive."""
        assert hasher.hash("Store") == hasher.hash("store")
        assert hasher.hash("STORE") == hasher.hash("store")
        assert hasher.hash("sToRe") == hasher.hash("ROTES")
    
    def test_are_anagrams_method(self, hasher):
        """are_anagrams method should work correctly."""
        assert hasher.are_anagrams("store", "rotes")
        assert hasher.are_anagrams("listen", "silent")
        assert not hasher.are_anagrams("store", "stare")
        assert not hasher.are_anagrams("cat", "dog")
    
    def test_group_anagrams(self, hasher, sample_corpus):
        """group_anagrams should correctly cluster words."""
        groups = hasher.group_anagrams(sample_corpus)
        
        # Find the group containing "store"
        store_hash = hasher.hash("store")
        store_group = set(groups[store_hash])
        assert store_group == {"store", "rotes", "tores", "stroe"}
        
        # Find the group containing "listen"
        listen_hash = hasher.hash("listen")
        listen_group = set(groups[listen_hash])
        assert listen_group == {"listen", "silent", "enlist"}
        
        # Singleton should be alone
        dog_hash = hasher.hash("dog")
        assert groups[dog_hash] == ["dog"]
    
    def test_total_bits_reasonable(self, hasher):
        """Total bits should fit in 64-bit register."""
        assert hasher.total_bits <= 64
    
    def test_non_alpha_ignored(self, hasher):
        """Non-alphabetic characters should be ignored."""
        assert hasher.hash("store") == hasher.hash("s-t-o-r-e")
        assert hasher.hash("store") == hasher.hash("store123")
        assert hasher.hash("store") == hasher.hash("  store  ")


class TestQuickFunctions:
    """Tests for corpus-free quick functions."""
    
    def test_quick_hash_anagrams(self):
        """quick_hash should identify anagrams."""
        assert quick_hash("store") == quick_hash("rotes")
        assert quick_hash("listen") == quick_hash("silent")
    
    def test_quick_hash_non_anagrams(self):
        """quick_hash should distinguish non-anagrams."""
        assert quick_hash("store") != quick_hash("stare")
        assert quick_hash("cat") != quick_hash("dog")
    
    def test_are_anagrams_function(self):
        """Module-level are_anagrams should work."""
        assert are_anagrams("store", "rotes")
        assert are_anagrams("listen", "silent")
        assert are_anagrams("astronomer", "moonstarer")
        assert not are_anagrams("hello", "world")


class TestEdgeCases:
    """Edge case tests."""
    
    def test_empty_string(self):
        """Empty strings should hash to 0."""
        hasher = PackedAnagramHasher(["test"])
        assert hasher.hash("") == 0
        assert hasher.are_anagrams("", "")
    
    def test_single_letter(self):
        """Single letters should work."""
        hasher = PackedAnagramHasher(["a", "b", "c"])
        assert hasher.hash("a") != hasher.hash("b")
        assert hasher.are_anagrams("a", "a")
    
    def test_long_word(self):
        """Long words should work if within bit budget."""
        corpus = ["pneumonoultramicroscopicsilicovolcanoconiosis"]
        hasher = PackedAnagramHasher(corpus)
        h = hasher.hash(corpus[0])
        assert h > 0
    
    def test_repr(self):
        """__repr__ should be informative."""
        hasher = PackedAnagramHasher(["test"])
        assert "PackedAnagramHasher" in repr(hasher)
        assert "total_bits" in repr(hasher)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
