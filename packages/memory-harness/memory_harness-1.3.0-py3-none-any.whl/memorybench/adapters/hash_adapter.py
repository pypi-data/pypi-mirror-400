"""Hash-based adapter (baseline, deterministic)."""
import numpy as np
import hashlib
from typing import Dict, Any, Tuple
from .base import BaseAdapter


class HashAdapter(BaseAdapter):
    """
    Deterministic hash-based encoding.
    Good for debugging. Not for semantic similarity.
    """
    
    def _hash_to_vector(self, text: str, dim: int, salt: str = "") -> np.ndarray:
        h = hashlib.sha256(f"{salt}:{text}".encode()).hexdigest()
        seed = int(h[:8], 16)
        rng = np.random.default_rng(seed)
        vec = rng.standard_normal(dim)
        return vec / (np.linalg.norm(vec) + 1e-8)
    
    def encode_store(self, item: Dict[str, Any]) -> Tuple[np.ndarray, np.ndarray]:
        item_id = item.get("item_id", "")
        tenant_id = item.get("tenant_id", "default")
        text = item.get("text", "")
        
        # Pattern: unique per item (from item_id)
        pattern_vec = self._hash_to_vector(item_id, self.n_probe * self.n_probe, "pattern")
        P = pattern_vec.reshape((self.n_probe, self.n_probe))
        P = (P + P.T) / 2
        np.fill_diagonal(P, 0)
        
        # Cue: from TEXT content (for retrieval matching)
        cue_vec = self._hash_to_vector(f"{tenant_id}:{text}", self.n_probe * self.n_bridge, "cue")
        cue = cue_vec.reshape((self.n_probe, self.n_bridge))
        
        return P, cue
    
    def encode_query(self, query: Dict[str, Any]) -> np.ndarray:
        tenant_id = query.get("tenant_id", "default")
        text = query.get("text", "")
        
        # Cue: from QUERY text (must match store cue if text is similar)
        cue_vec = self._hash_to_vector(f"{tenant_id}:{text}", self.n_probe * self.n_bridge, "cue")
        return cue_vec.reshape((self.n_probe, self.n_bridge))
