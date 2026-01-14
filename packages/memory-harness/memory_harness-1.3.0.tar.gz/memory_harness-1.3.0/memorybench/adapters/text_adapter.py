"""Text adapter: converts text items to QCG patterns."""
import numpy as np
import hashlib
from typing import Dict, Any
from .base import BaseAdapter


class TextAdapter(BaseAdapter):
    """
    Converts text items to patterns using deterministic hashing.
    
    Dataset format:
    {"item_id": "1", "tenant_id": "A", "text": "...", "label": "optional"}
    """
    
    def _text_to_vector(self, text: str, dim: int) -> np.ndarray:
        """Deterministic text -> vector using hash."""
        h = hashlib.sha256(text.encode()).hexdigest()
        # Use hash bytes as seed for reproducible random vector
        seed = int(h[:8], 16)
        rng = np.random.default_rng(seed)
        return rng.standard_normal(dim)
    
    def to_pattern(self, item: Dict[str, Any]) -> np.ndarray:
        """Text + item_id -> symmetric pattern matrix."""
        text = item.get("text", "")
        item_id = item.get("item_id", "")
        combined = f"{item_id}:{text}"
        
        vec = self._text_to_vector(combined, self.n_probe * self.n_probe)
        P = vec.reshape((self.n_probe, self.n_probe))
        P = (P + P.T) / 2  # Symmetric
        np.fill_diagonal(P, 0)
        return P
    
    def to_cue(self, item: Dict[str, Any]) -> np.ndarray:
        """tenant_id + item_id -> cue matrix."""
        tenant_id = item.get("tenant_id", "default")
        item_id = item.get("item_id", "")
        combined = f"cue:{tenant_id}:{item_id}"
        
        vec = self._text_to_vector(combined, self.n_probe * self.n_bridge)
        return vec.reshape((self.n_probe, self.n_bridge))
