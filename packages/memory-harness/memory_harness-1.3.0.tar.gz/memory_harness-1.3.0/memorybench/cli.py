#!/usr/bin/env python3
"""Memory Harness CLI - Benchmark AI memory systems"""
import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error
import getpass

from . import __version__

API_URL = os.getenv("MEMORYBENCH_API_URL", "https://memory-harness-api-production.up.railway.app")
CONFIG_PATH = os.path.expanduser("~/.memorybench/config.json")


def api_request(method, path, data=None, token=None):
    url = f"{API_URL}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        try:
            error = json.loads(error_body)
            raise Exception(error.get("detail", str(e)))
        except json.JSONDecodeError:
            raise Exception(f"HTTP {e.code}: {error_body}")


def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            return json.load(f)
    return {}


def save_config(config):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f)


def compute_score(r):
    return round(
        35 * r.get("accuracy_at_1", 0) +
        15 * r.get("accuracy_at_k", 0) +
        25 * (1 - r.get("cross_tenant_error_rate", 0)) +
        10 * (1 - r.get("collision_rate", 0)) +
        15 * r.get("confidence_rate", 0)
    , 1)


def grade(score):
    if score >= 90: return "A"
    if score >= 80: return "B"
    if score >= 70: return "C"
    if score >= 60: return "D"
    return "F"


def cmd_login(args):
    password = args.password or getpass.getpass("Password: ")
    result = api_request("POST", "/auth/login", {"email": args.email, "password": password})
    token = result.get("access_token") or result.get("token")
    if not token:
        print("Login failed")
        return 1
    save_config({"token": token, "email": args.email})
    print(f"Logged in as {args.email}")
    return 0


def cmd_run(args):
    config = load_config()
    token = config.get("token")
    if not token:
        print("Not logged in. Run: memorybench login -e EMAIL")
        return 1
    providers = api_request("GET", "/providers", token=token)
    if not providers:
        print("No providers configured.")
        return 1
    provider = providers[0]
    print(f"Provider: {provider['name']}")
    print("Running audit...")
    run = api_request("POST", "/audits/run", {"provider_id": provider["id"], "seeds": args.seeds}, token=token)
    run_id = run["id"]
    while run["status"] in ("pending", "running"):
        time.sleep(2)
        run = api_request("GET", f"/audits/{run_id}", token=token)
    if run["status"] == "failed":
        print("FAILED")
        return 1
    results = run.get("results", [])
    passed = sum(1 for r in results if r["passed"])
    score = (passed / len(results) * 100) if results else 0
    print("=" * 50)
    for r in results:
        s = "PASS" if r["passed"] else "FAIL"
        print(f" {s}  {r['test_id']:25} {r['score']:.3f}")
    print("=" * 50)
    print(f" Score: {score:.0f}/100 ({passed}/{len(results)})")
    with open(args.output, "w") as f:
        json.dump({"version": __version__, "score": score, "tests": results}, f, indent=2)
    print(f"Report: {args.output}")
    return 0 if passed == len(results) else 1


def cmd_validate(args):
    from .dataset_schema import validate_dataset
    is_valid, errors, stats = validate_dataset(args.dataset)
    print(f"\nDataset: {args.dataset}")
    print(f"  Store: {stats['store_count']}  Query: {stats['query_count']}  Tenants: {', '.join(stats['tenants'])}")
    if is_valid:
        print("Valid")
        return 0
    else:
        print(f"Invalid ({len(errors)} errors)")
        for e in errors[:3]:
            print(f"  Line {e.line}: {e.message}")
        return 1


def cmd_dataset(args):
    if getattr(args, "sample", False):
        import tempfile
        import importlib.resources as res
        from pathlib import Path as P
        sample = res.files("memorybench").joinpath("examples/sample_dataset.jsonl")
        tmp = tempfile.NamedTemporaryFile(prefix="memorybench_sample_", suffix=".jsonl", delete=False)
        tmp.write(sample.read_bytes())
        tmp.close()
        args.dataset = str(P(tmp.name).resolve())
        print(f"Using sample dataset: {args.dataset}")

    if not getattr(args, "dataset", None):
        raise SystemExit("ERR: missing --dataset (or use --sample)")
    if not getattr(args, "provider_endpoint", None):
        raise SystemExit("ERR: missing --provider-endpoint")

    from .http_provider import HttpProvider
    provider = HttpProvider(args.provider_endpoint)

    name = (getattr(args, "adapter", None) or "text").lower()
    if name in ("text", "ngram"):
        from .adapters.ngram_adapter import NgramAdapter
        try:
            adapter = NgramAdapter(n_probe=args.n_probe, n_bridge=getattr(args, "n_bridge", 0))
        except TypeError:
            try:
                adapter = NgramAdapter(n_probe=args.n_probe)
            except TypeError:
                adapter = NgramAdapter()
    elif name == "hash":
        from .adapters.hash_adapter import HashAdapter
        try:
            adapter = HashAdapter(n_probe=args.n_probe, n_bridge=getattr(args, "n_bridge", 0))
        except TypeError:
            try:
                adapter = HashAdapter(n_probe=args.n_probe)
            except TypeError:
                adapter = HashAdapter()
    elif name == "embedding":
        from .adapters.embedding_adapter import EmbeddingAdapter
        adapter = EmbeddingAdapter()
    else:
        raise SystemExit(f"ERR: unknown adapter '{name}'")

    from .dataset_runner import run_dataset_benchmark
    result = run_dataset_benchmark(
        provider=provider,
        dataset_path=args.dataset,
        adapter=adapter,
        k=args.k,
        seed=args.seed,
        confidence_threshold=args.confidence_threshold,
    )

    score = compute_score(result.__dict__)
    g = grade(score)
    print(f"\n{'='*50}")
    print(f" Score: {score}/100  Grade: {g}")
    print(f" Accuracy@1: {result.accuracy_at_1:.1%}")
    print(f" Accuracy@{args.k}: {result.accuracy_at_k:.1%}")
    print(f" Confidence: {result.confidence_rate:.1%}")
    print(f"{'='*50}")

    report = {"version": __version__, "score": score, "grade": g, **result.__dict__}
    with open(args.output, "w") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"Report: {args.output}")

    pub = getattr(args, "publish", None)
    if pub:
        try:
            from .publish import publish_report
            resp = publish_report(pub, report)
            rid = (resp or {}).get("run_id") or (resp or {}).get("id") or ""
            print(f"Published: run_id={rid} {pub}")
        except Exception as e:
            print(f"Publish failed: {e}")

    return 0 if score >= args.pass_threshold else 1


def main():
    p = argparse.ArgumentParser(prog="memorybench", description="Memory Harness CLI")
    p.add_argument("-v", "--version", action="version", version=f"%(prog)s {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("login", help="Authenticate")
    s.add_argument("-e", "--email", required=True)
    s.add_argument("-p", "--password")

    s = sub.add_parser("run", help="Run 7-test audit")
    s.add_argument("-o", "--output", default="report.json")
    s.add_argument("-s", "--seeds", type=int, nargs="+", default=[0, 1, 2])

    s = sub.add_parser("validate", help="Validate dataset")
    s.add_argument("-d", "--dataset", required=True)

    s = sub.add_parser("dataset", help="Benchmark dataset")
    s.add_argument("--sample", action="store_true", help="Use bundled sample dataset")
    s.add_argument("--publish", help="Publish report to URL (POST JSON)")
    s.add_argument("-d", "--dataset", required=False)
    s.add_argument("-a", "--adapter", default="text", choices=["hash", "text", "ngram", "embedding"])
    s.add_argument("-o", "--output", default="dataset_report.json")
    s.add_argument("-k", type=int, default=3)
    s.add_argument("--seed", type=int, default=42)
    s.add_argument("--n-probe", type=int, default=16)
    s.add_argument("--n-bridge", type=int, default=16)
    s.add_argument("--confidence-threshold", type=float, default=0.1)
    s.add_argument("--pass-threshold", type=int, default=70, help="Minimum score to pass")
    s.add_argument("--provider-endpoint", required=False, help="Provider URL")

    args = p.parse_args()
    cmds = {"login": cmd_login, "run": cmd_run, "validate": cmd_validate, "dataset": cmd_dataset}
    return cmds[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
