"""Base adapter interface."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple
import numpy as np


class BaseAdapter(ABC):
    """Converts dataset items to QCG format (pattern, cue)."""
    
    def __init__(self, n_probe: int = 16, n_bridge: int = 16):
        self.n_probe = n_probe
        self.n_bridge = n_bridge
    
    @abstractmethod
    def encode_store(self, item: Dict[str, Any]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Encode a STORE item.
        Returns (pattern, cue) where:
          - pattern: derived from item content (unique signature)
          - cue: derived from item TEXT (for retrieval)
        """
        pass
    
    @abstractmethod
    def encode_query(self, query: Dict[str, Any]) -> np.ndarray:
        """
        Encode a QUERY item.
        Returns cue derived from QUERY TEXT only.
        expected_item_id is NOT used here (only for evaluation).
        """
        pass
