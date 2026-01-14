# Memory Harness

**Benchmark and validate AI memory systems. Detect regressions, leakage, and shortcuts.**

[![PyPI](https://img.shields.io/pypi/v/memory-harness)](https://pypi.org/project/memory-harness/)
```
==================================================
 MEMORY BENCHMARK REPORT
==================================================
 Accuracy@1:      83.3%  pass
 Accuracy@3:     100.0%  pass
 Cross-tenant:     0.0%  pass
 Collision:       16.7%  pass
 Confidence:      83.3%  pass
==================================================
 SCORE: 90.0/100  GRADE: A
==================================================
```

## Install
```bash
pip install memory-harness httpx
```

## Quick Start

### 1. Create your dataset (`data.jsonl`)
```jsonl
{"type":"store","item_id":"doc1","tenant_id":"acme","text":"Customer bought 3 widgets"}
{"type":"store","item_id":"doc2","tenant_id":"acme","text":"Support ticket: login issue"}
{"type":"store","item_id":"doc3","tenant_id":"globex","text":"New user signup from France"}
{"type":"store","item_id":"doc4","tenant_id":"globex","text":"User upgraded to premium"}
{"type":"query","query_id":"q1","tenant_id":"acme","text":"customer purchase","expected_item_id":"doc1"}
{"type":"query","query_id":"q2","tenant_id":"acme","text":"login problem support","expected_item_id":"doc2"}
{"type":"query","query_id":"q3","tenant_id":"globex","text":"new customer france","expected_item_id":"doc3"}
{"type":"query","query_id":"q4","tenant_id":"globex","text":"plan upgrade","expected_item_id":"doc4"}
```

### 2. Run benchmark
```bash
memorybench dataset -d data.jsonl --provider-endpoint https://your-memory-api.com --n-probe 16
```

### 3. Get your score
```
SCORE: 90.0/100  GRADE: A
PASS (threshold: 70)
```

## Metrics

| Metric | What it measures | Target |
|--------|------------------|--------|
| **Accuracy@1** | Exact match rate | ≥70% |
| **Accuracy@k** | Correct item in top-k | ≥90% |
| **Cross-tenant** | Data leakage between tenants | <5% |
| **Collision** | Different queries → same result | <20% |
| **Confidence** | Clear winner (margin) | ≥80% |

## Grading

| Grade | Score | CI Exit |
|-------|-------|---------|
| A | 90-100 | 0 (pass) |
| B | 80-89 | 0 (pass) |
| C | 70-79 | 0 (pass) |
| D | 60-69 | 1 (fail) |
| F | <60 | 1 (fail) |

## CI Integration

Add to `.github/workflows/memory-audit.yml`:
```yaml
name: Memory Audit
on: [push, pull_request]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install
        run: pip install memory-harness httpx
      
      - name: Run Memory Benchmark
        run: |
          memorybench dataset \
            -d tests/memory_data.jsonl \
            --provider-endpoint ${{ secrets.MEMORY_API_URL }} \
            --n-probe 16 \
            --pass-threshold 70
      
      - name: Upload Report
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: memory-report
          path: dataset_report.*
```

**Setup:**
1. Add `MEMORY_API_URL` to repository secrets
2. Create `tests/memory_data.jsonl` with your test data
3. Push — CI fails if score < 70

## Dataset Format

**Store items** (what to remember):
```json
{"type":"store","item_id":"unique_id","tenant_id":"namespace","text":"content"}
```

**Query items** (retrieval tests):
```json
{"type":"query","query_id":"q1","tenant_id":"namespace","text":"search query","expected_item_id":"unique_id"}
```

### Validate before running
```bash
memorybench validate -d data.jsonl
```

## CLI Reference
```bash
memorybench --version                    # Version
memorybench validate -d FILE             # Validate dataset
memorybench dataset -d FILE [OPTIONS]    # Run benchmark
```

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `-d, --dataset` | required | JSONL file |
| `--provider-endpoint` | - | Memory API URL |
| `--n-probe` | 16 | Pattern dimension |
| `--pass-threshold` | 70 | Minimum score |
| `-a, --adapter` | text | hash, text, embedding |
| `-o, --output` | dataset_report.json | Report file |

## Provider API

Your memory endpoint must implement:
```
POST /reset   {"seed": int}
POST /store   {"pattern": [[float]], "cue": [[float]], "learn_steps": int}
POST /recall  {"cue": [[float]], "steps": int} → {"pattern": [[float]]}
```

## License

MIT
