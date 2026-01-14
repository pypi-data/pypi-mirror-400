"""Graph adapter: converts graph items to QCG patterns."""
import numpy as np
from typing import Dict, Any, List
from .base import BaseAdapter


class GraphAdapter(BaseAdapter):
    """
    Converts graph items (edges) to patterns.
    
    Dataset format:
    {"item_id": "1", "tenant_id": "A", "edges": [[0,1], [1,2], [2,3]], "query_nodes": [0,1]}
    """
    
    def to_pattern(self, item: Dict[str, Any]) -> np.ndarray:
        """Edges -> adjacency-like pattern matrix."""
        edges = item.get("edges", [])
        P = np.zeros((self.n_probe, self.n_probe))
        
        for edge in edges:
            if len(edge) >= 2:
                i, j = edge[0] % self.n_probe, edge[1] % self.n_probe
                P[i, j] = 1.0
                P[j, i] = 1.0  # Symmetric
        
        np.fill_diagonal(P, 0)
        
        # Normalize
        norm = np.linalg.norm(P)
        if norm > 0:
            P = P / norm * 2.0
        
        return P
    
    def to_cue(self, item: Dict[str, Any]) -> np.ndarray:
        """Query nodes + tenant -> cue matrix."""
        tenant_id = item.get("tenant_id", "default")
        item_id = item.get("item_id", "")
        query_nodes = item.get("query_nodes", [])
        
        # Deterministic cue from tenant + item
        seed_str = f"cue:{tenant_id}:{item_id}:{query_nodes}"
        seed = int(hashlib.sha256(seed_str.encode()).hexdigest()[:8], 16)
        rng = np.random.default_rng(seed)
        
        return rng.standard_normal((self.n_probe, self.n_bridge))


import hashlib
