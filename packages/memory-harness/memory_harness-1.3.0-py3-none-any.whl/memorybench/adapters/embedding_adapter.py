"""Sentence-transformers based adapter."""
import numpy as np
import hashlib
from typing import Dict, Any, Tuple
from .base import BaseAdapter


class SentenceEmbeddingAdapter(BaseAdapter):
    """
    Uses sentence-transformers for real semantic embeddings.
    Similar texts → similar cues.
    
    Install: pip install sentence-transformers
    """
    
    def __init__(self, n_probe: int = 16, n_bridge: int = 16, model_name: str = "all-MiniLM-L6-v2"):
        super().__init__(n_probe, n_bridge)
        self.model_name = model_name
        self._model = None
        self._cache = {}
    
    @property
    def model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                print(f"  Loading model: {self.model_name}...")
                self._model = SentenceTransformer(self.model_name)
            except ImportError:
                raise ImportError(
                    "sentence-transformers required.\n"
                    "Install: pip install sentence-transformers"
                )
        return self._model
    
    def _embed(self, text: str) -> np.ndarray:
        """Get embedding with caching."""
        if text not in self._cache:
            self._cache[text] = self.model.encode(text, normalize_embeddings=True)
        return self._cache[text]
    
    def _embedding_to_matrix(self, emb: np.ndarray, shape: Tuple[int, int]) -> np.ndarray:
        """Project embedding to matrix."""
        target_size = shape[0] * shape[1]
        emb_size = len(emb)
        
        if emb_size >= target_size:
            vec = emb[:target_size]
        else:
            repeats = (target_size // emb_size) + 1
            vec = np.tile(emb, repeats)[:target_size]
        
        # Normalize
        vec = vec / (np.linalg.norm(vec) + 1e-8)
        return vec.reshape(shape)
    
    def _id_to_pattern(self, item_id: str) -> np.ndarray:
        """Deterministic unique pattern per item."""
        seed = int(hashlib.sha256(f"pattern:{item_id}".encode()).hexdigest()[:8], 16)
        rng = np.random.default_rng(seed)
        vec = rng.standard_normal(self.n_probe * self.n_probe)
        vec = vec / (np.linalg.norm(vec) + 1e-8)
        P = vec.reshape((self.n_probe, self.n_probe))
        P = (P + P.T) / 2
        np.fill_diagonal(P, 0)
        return P
    
    def encode_store(self, item: Dict[str, Any]) -> Tuple[np.ndarray, np.ndarray]:
        item_id = item.get("item_id", "")
        tenant_id = item.get("tenant_id", "default")
        text = item.get("text", "")
        
        # Pattern: unique per item_id
        P = self._id_to_pattern(item_id)
        
        # Cue: semantic embedding of text (with tenant prefix)
        full_text = f"[{tenant_id}] {text}"
        emb = self._embed(full_text)
        cue = self._embedding_to_matrix(emb, (self.n_probe, self.n_bridge))
        
        return P, cue
    
    def encode_query(self, query: Dict[str, Any]) -> np.ndarray:
        tenant_id = query.get("tenant_id", "default")
        text = query.get("text", "")
        
        full_text = f"[{tenant_id}] {text}"
        emb = self._embed(full_text)
        return self._embedding_to_matrix(emb, (self.n_probe, self.n_bridge))
