"""N-gram based adapter with semantic similarity."""
import numpy as np
import hashlib
from typing import Dict, Any, Tuple, List, Set
from .base import BaseAdapter


class NgramAdapter(BaseAdapter):
    """
    Character n-gram based embedding.
    Similar texts → similar cues (key property).
    """
    
    def __init__(self, n_probe: int = 16, n_bridge: int = 16, ngram_size: int = 3):
        super().__init__(n_probe, n_bridge)
        self.ngram_size = ngram_size
    
    def _text_to_ngrams(self, text: str) -> Set[str]:
        """Extract character n-grams."""
        text = text.lower().strip()
        ngrams = set()
        for i in range(len(text) - self.ngram_size + 1):
            ngrams.add(text[i:i + self.ngram_size])
        # Add word-level features
        for word in text.split():
            if len(word) >= 3:
                ngrams.add(f"W:{word[:6]}")
        return ngrams
    
    def _ngrams_to_vector(self, ngrams: Set[str], dim: int) -> np.ndarray:
        """Convert n-grams to dense vector via hashing."""
        vec = np.zeros(dim)
        for ng in ngrams:
            h = int(hashlib.md5(ng.encode()).hexdigest()[:8], 16)
            idx = h % dim
            sign = 1 if (h >> 31) & 1 else -1
            vec[idx] += sign
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec
    
    def _id_to_vector(self, id_str: str, dim: int) -> np.ndarray:
        """Deterministic ID → vector."""
        seed = int(hashlib.sha256(id_str.encode()).hexdigest()[:8], 16)
        rng = np.random.default_rng(seed)
        vec = rng.standard_normal(dim)
        return vec / (np.linalg.norm(vec) + 1e-8)
    
    def _text_to_cue(self, text: str, tenant_id: str) -> np.ndarray:
        """Text → cue matrix."""
        ngrams = self._text_to_ngrams(text)
        
        # Text embedding
        text_dim = self.n_probe * self.n_bridge
        if ngrams:
            cue_vec = self._ngrams_to_vector(ngrams, text_dim)
        else:
            cue_vec = self._id_to_vector(text, text_dim)
        
        # Add tenant bias (small, to separate tenants)
        tenant_vec = self._id_to_vector(f"tenant:{tenant_id}", text_dim) * 0.2
        cue_vec = cue_vec + tenant_vec
        cue_vec = cue_vec / (np.linalg.norm(cue_vec) + 1e-8)
        
        return cue_vec.reshape((self.n_probe, self.n_bridge))
    
    def encode_store(self, item: Dict[str, Any]) -> Tuple[np.ndarray, np.ndarray]:
        item_id = item.get("item_id", "")
        tenant_id = item.get("tenant_id", "default")
        text = item.get("text", "")
        
        # Pattern: unique per item
        pattern_vec = self._id_to_vector(f"pattern:{item_id}", self.n_probe * self.n_probe)
        P = pattern_vec.reshape((self.n_probe, self.n_probe))
        P = (P + P.T) / 2
        np.fill_diagonal(P, 0)
        
        # Cue: from TEXT (semantic)
        cue = self._text_to_cue(text, tenant_id)
        
        return P, cue
    
    def encode_query(self, query: Dict[str, Any]) -> np.ndarray:
        tenant_id = query.get("tenant_id", "default")
        text = query.get("text", "")
        return self._text_to_cue(text, tenant_id)
