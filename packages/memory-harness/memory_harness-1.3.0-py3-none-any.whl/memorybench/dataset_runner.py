"""
Dataset benchmark runner.
Schema:
  {"type": "store", "item_id": "1", "tenant_id": "A", "text": "..."}
  {"type": "query", "query_id": "q1", "tenant_id": "A", "text": "...", "expected_item_id": "1"}
"""
import json
import numpy as np
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, field


@dataclass
class DatasetResult:
    total_store: int
    total_query: int
    accuracy_at_1: float
    accuracy_at_k: float
    cross_tenant_error_rate: float
    collision_rate: float
    confidence_rate: float  # NEW: % of queries with clear winner
    avg_margin: float  # NEW: average (sim_top1 - sim_top2)
    forgetting_curve: List[Tuple[int, float]]
    details: Dict[str, Any] = field(default_factory=dict)


def load_dataset(path: str) -> Tuple[List[Dict], List[Dict]]:
    """Load JSONL, return (store_items, query_items)."""
    stores, queries = [], []
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            item = json.loads(line)
            item_type = item.get("type", "store")
            if item_type == "query":
                queries.append(item)
            else:
                stores.append(item)
    return stores, queries


def similarity(P1: np.ndarray, P2: np.ndarray) -> float:
    """Cosine similarity."""
    v1, v2 = P1.flatten(), P2.flatten()
    n1, n2 = np.linalg.norm(v1), np.linalg.norm(v2)
    if n1 < 1e-10 or n2 < 1e-10:
        return 0.0
    return float(np.dot(v1, v2) / (n1 * n2))


def run_dataset_benchmark(
    provider,
    dataset_path: str,
    adapter,
    k: int = 3,
    seed: int = 42,
    confidence_threshold: float = 0.1
) -> DatasetResult:
    """
    Run benchmark with proper STORE vs QUERY separation.
    """
    stores, queries = load_dataset(dataset_path)
    
    if not stores:
        raise ValueError("No store items in dataset")
    if not queries:
        raise ValueError("No query items in dataset")
    
    # Encode store items
    encoded_stores = {}
    for item in stores:
        item_id = item["item_id"]
        pattern, cue = adapter.encode_store(item)
        encoded_stores[item_id] = {
            "item": item,
            "pattern": pattern,
            "cue": cue,
            "tenant_id": item.get("tenant_id", "default")
        }
    
    # Phase 1: Store all items
    provider.reset(seed)
    store_order = []
    for item_id, enc in encoded_stores.items():
        provider.store(enc["pattern"].tolist(), enc["cue"].tolist(), steps=50)
        store_order.append(item_id)
    
    # Phase 2: Run queries
    correct_at_1 = 0
    correct_at_k = 0
    cross_tenant_errors = 0
    confident_queries = 0
    margins = []
    query_results = []
    
    for q in queries:
        query_id = q.get("query_id", q.get("item_id", "?"))
        expected_id = q.get("expected_item_id")
        query_tenant = q.get("tenant_id", "default")
        
        # Encode query (from query text only!)
        query_cue = adapter.encode_query(q)
        
        # Recall
        recalled = np.array(provider.recall(query_cue.tolist(), steps=30))
        
        # Find matches by comparing recalled vs stored patterns
        matches = []
        for item_id, enc in encoded_stores.items():
            sim = similarity(recalled, enc["pattern"])
            matches.append({
                "item_id": item_id,
                "sim": sim,
                "tenant_id": enc["tenant_id"]
            })
        matches.sort(key=lambda x: x["sim"], reverse=True)
        
        top1 = matches[0] if matches else None
        top2 = matches[1] if len(matches) > 1 else None
        topk_ids = [m["item_id"] for m in matches[:k]]
        
        # Compute margin
        margin = (top1["sim"] - top2["sim"]) if top1 and top2 else 1.0
        margins.append(margin)
        
        # Score
        hit_1 = (top1["item_id"] == expected_id) if top1 else False
        hit_k = expected_id in topk_ids
        cross_tenant = (top1["tenant_id"] != query_tenant) if top1 else False
        confident = margin >= confidence_threshold
        
        if hit_1:
            correct_at_1 += 1
        if hit_k:
            correct_at_k += 1
        if cross_tenant and not hit_1:
            cross_tenant_errors += 1
        if confident:
            confident_queries += 1
        
        query_results.append({
            "query_id": query_id,
            "expected": expected_id,
            "got": top1["item_id"] if top1 else None,
            "sim_top1": top1["sim"] if top1 else 0,
            "margin": margin,
            "hit_1": hit_1,
            "hit_k": hit_k,
            "confident": confident,
            "cross_tenant": cross_tenant,
            "top_k": topk_ids[:k],
        })
    
    n_queries = len(queries)
    accuracy_at_1 = correct_at_1 / n_queries if n_queries else 0
    accuracy_at_k = correct_at_k / n_queries if n_queries else 0
    cross_tenant_rate = cross_tenant_errors / n_queries if n_queries else 0
    confidence_rate = confident_queries / n_queries if n_queries else 0
    avg_margin = float(np.mean(margins)) if margins else 0
    
    # Collision rate
    top1_counts = {}
    for r in query_results:
        got = r["got"]
        if got:
            top1_counts[got] = top1_counts.get(got, 0) + 1
    collisions = sum(c - 1 for c in top1_counts.values() if c > 1)
    collision_rate = collisions / n_queries if n_queries else 0
    
    # Forgetting curve
    forgetting_curve = []
    checkpoints = [1, 2, 5, 10, 20, 50, 100]
    for checkpoint in checkpoints:
        if checkpoint > len(stores):
            break
        provider.reset(seed)
        subset_ids = store_order[:checkpoint]
        for item_id in subset_ids:
            enc = encoded_stores[item_id]
            provider.store(enc["pattern"].tolist(), enc["cue"].tolist(), steps=50)
        
        hits = 0
        tested = 0
        for q in queries:
            expected_id = q.get("expected_item_id")
            if expected_id not in subset_ids:
                continue
            tested += 1
            query_cue = adapter.encode_query(q)
            recalled = np.array(provider.recall(query_cue.tolist(), steps=30))
            
            best_sim, best_id = -1, None
            for item_id in subset_ids:
                enc = encoded_stores[item_id]
                sim = similarity(recalled, enc["pattern"])
                if sim > best_sim:
                    best_sim, best_id = sim, item_id
            
            if best_id == expected_id:
                hits += 1
        
        acc = hits / tested if tested else 0
        forgetting_curve.append((checkpoint, acc))
    
    return DatasetResult(
        total_store=len(stores),
        total_query=len(queries),
        accuracy_at_1=accuracy_at_1,
        accuracy_at_k=accuracy_at_k,
        cross_tenant_error_rate=cross_tenant_rate,
        collision_rate=collision_rate,
        confidence_rate=confidence_rate,
        avg_margin=avg_margin,
        forgetting_curve=forgetting_curve,
        details={
            "k": k,
            "confidence_threshold": confidence_threshold,
            "query_results": query_results,
            "tenants": list(set(s.get("tenant_id", "default") for s in stores)),
        }
    )
