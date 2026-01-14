"""
Dataset Schema Validation
========================

Standard JSONL format for Memory Harness benchmarks.

STORE items:
  {"type": "store", "item_id": "1", "tenant_id": "acme", "text": "..."}

QUERY items:
  {"type": "query", "query_id": "q1", "tenant_id": "acme", "text": "...", "expected_item_id": "1"}

Fields:
  - type: "store" | "query" (required)
  - item_id: unique identifier for store items (required for store)
  - query_id: unique identifier for query items (optional, defaults to auto)
  - tenant_id: namespace/tenant identifier (required)
  - text: content to encode (required)
  - expected_item_id: item_id that should be retrieved (required for query)
  - label: optional category/tag
  - metadata: optional dict of extra fields
"""
import json
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass


@dataclass
class ValidationError:
    line: int
    field: str
    message: str


def validate_dataset(path: str) -> Tuple[bool, List[ValidationError], Dict[str, Any]]:
    """
    Validate a JSONL dataset file.
    Returns (is_valid, errors, stats)
    """
    errors = []
    stats = {
        "total_lines": 0,
        "store_count": 0,
        "query_count": 0,
        "tenants": set(),
        "store_ids": set(),
        "expected_ids": set(),
    }
    
    try:
        with open(path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                stats["total_lines"] += 1
                
                try:
                    item = json.loads(line)
                except json.JSONDecodeError as e:
                    errors.append(ValidationError(line_num, "JSON", f"Invalid JSON: {e}"))
                    continue
                
                # Check type
                item_type = item.get("type", "store")
                
                if item_type == "store":
                    stats["store_count"] += 1
                    
                    # Required fields
                    if "item_id" not in item:
                        errors.append(ValidationError(line_num, "item_id", "Missing required field 'item_id'"))
                    else:
                        if item["item_id"] in stats["store_ids"]:
                            errors.append(ValidationError(line_num, "item_id", f"Duplicate item_id: {item['item_id']}"))
                        stats["store_ids"].add(item["item_id"])
                    
                    if "tenant_id" not in item:
                        errors.append(ValidationError(line_num, "tenant_id", "Missing required field 'tenant_id'"))
                    else:
                        stats["tenants"].add(item["tenant_id"])
                    
                    if "text" not in item:
                        errors.append(ValidationError(line_num, "text", "Missing required field 'text'"))
                
                elif item_type == "query":
                    stats["query_count"] += 1
                    
                    if "tenant_id" not in item:
                        errors.append(ValidationError(line_num, "tenant_id", "Missing required field 'tenant_id'"))
                    else:
                        stats["tenants"].add(item["tenant_id"])
                    
                    if "text" not in item:
                        errors.append(ValidationError(line_num, "text", "Missing required field 'text'"))
                    
                    if "expected_item_id" not in item:
                        errors.append(ValidationError(line_num, "expected_item_id", "Missing required field 'expected_item_id'"))
                    else:
                        stats["expected_ids"].add(item["expected_item_id"])
                
                else:
                    errors.append(ValidationError(line_num, "type", f"Unknown type: {item_type}"))
    
    except FileNotFoundError:
        errors.append(ValidationError(0, "file", f"File not found: {path}"))
        return False, errors, stats
    
    # Cross-validation: check that expected_ids exist in store_ids
    missing_refs = stats["expected_ids"] - stats["store_ids"]
    if missing_refs:
        errors.append(ValidationError(0, "reference", f"Query references non-existent items: {missing_refs}"))
    
    # Convert sets for JSON serialization
    stats["tenants"] = list(stats["tenants"])
    stats["store_ids"] = len(stats["store_ids"])
    stats["expected_ids"] = len(stats["expected_ids"])
    
    is_valid = len(errors) == 0
    return is_valid, errors, stats


def print_validation_report(path: str):
    """Print a human-readable validation report."""
    is_valid, errors, stats = validate_dataset(path)
    
    print(f"\n{'='*50}")
    print(f"DATASET VALIDATION: {path}")
    print(f"{'='*50}")
    print(f"Store items:  {stats['store_count']}")
    print(f"Query items:  {stats['query_count']}")
    print(f"Tenants:      {stats['tenants']}")
    print(f"{'='*50}")
    
    if is_valid:
        print("✅ VALID")
    else:
        print(f"❌ INVALID ({len(errors)} errors)")
        for e in errors[:10]:
            print(f"  Line {e.line}: [{e.field}] {e.message}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more errors")
    
    return is_valid
