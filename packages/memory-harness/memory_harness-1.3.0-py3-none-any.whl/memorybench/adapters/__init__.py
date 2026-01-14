from .base import BaseAdapter
from .hash_adapter import HashAdapter
from .ngram_adapter import NgramAdapter

ADAPTERS = {
    "hash": HashAdapter,
    "ngram": NgramAdapter,
    "text": NgramAdapter,
}

# Optional: sentence-transformers (lazy load)
def _get_embedding_adapter():
    from .embedding_adapter import SentenceEmbeddingAdapter
    return SentenceEmbeddingAdapter

try:
    # Test import without loading model
    import importlib.util
    if importlib.util.find_spec("sentence_transformers"):
        ADAPTERS["embedding"] = _get_embedding_adapter
        ADAPTERS["minilm"] = _get_embedding_adapter
except:
    pass


def get_adapter(name: str, **kwargs):
    """Get adapter by name, handling lazy loading."""
    if name not in ADAPTERS:
        raise ValueError(f"Unknown adapter: {name}. Available: {list(ADAPTERS.keys())}")
    
    adapter_or_factory = ADAPTERS[name]
    if callable(adapter_or_factory) and not isinstance(adapter_or_factory, type):
        # It's a factory function
        AdapterClass = adapter_or_factory()
    else:
        AdapterClass = adapter_or_factory
    
    return AdapterClass(**kwargs)
