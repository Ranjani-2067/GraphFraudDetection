"""
Review-2 API smoke test.

Hits every endpoint of the running FastAPI app and checks it responds with
a sane status code and shape. Run this AFTER `python run.py` and AFTER
seeding the database (scripts/seed_db.py).

Usage:
    python smoke_test.py
    python smoke_test.py --base-url http://127.0.0.1:8000
"""
from __future__ import annotations
import argparse
import sys
import urllib.request
import urllib.error
import json

PASS = "PASS"
FAIL = "FAIL"


def call(base_url: str, method: str, path: str, body: dict | None = None, expect: int = 200):
    url = f"{base_url}{path}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            status = resp.status
            payload = json.loads(resp.read().decode() or "null")
    except urllib.error.HTTPError as e:
        status = e.code
        try:
            payload = json.loads(e.read().decode() or "null")
        except Exception:
            payload = None
    except Exception as e:
        return FAIL, None, f"request error: {e}"

    ok = status == expect
    return (PASS if ok else FAIL), payload, f"expected {expect}, got {status}"


def summarize(payload, limit=120):
    s = json.dumps(payload)[:limit]
    return s + ("..." if len(json.dumps(payload)) > limit else "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default="http://127.0.0.1:8000")
    args = ap.parse_args()
    base = args.base_url.rstrip("/")

    results = []

    def check(name, method, path, body=None, expect=200):
        status, payload, note = call(base, method, path, body, expect)
        results.append((name, status, note))
        marker = "\u2713" if status == PASS else "\u2717"
        print(f"[{status}] {marker} {name:<40} {note}")
        return payload

    print(f"== Review-2 smoke test against {base} ==\n")

    # --- System ---
    health = check("GET /health", "GET", "/health")
    if isinstance(health, dict) and not health.get("neo4j_connected"):
        print("\n!! Neo4j is not connected according to /health. Fix that before trusting the rest of these results. !!\n")

    check("GET /", "GET", "/")

    # --- Accounts: full CRUD (Insert, Retrieve, Update, Delete) ---
    test_account_id = "ACC_SMOKETEST_0001"
    create_acc_body = {
        "account_id": test_account_id,
        "name": "Smoke Test Account",
        "account_type": "savings",
        "risk_score": 0.0,
    }
    check("POST /accounts (create)", "POST", "/accounts", body=create_acc_body, expect=201)
    check(f"GET /accounts/{test_account_id} (verify create)", "GET", f"/accounts/{test_account_id}")
    check(f"PUT /accounts/{test_account_id} (update)", "PUT", f"/accounts/{test_account_id}",
          body={"name": "Smoke Test Account (Updated)", "risk_score": 0.42}, expect=200)
    updated = check(f"GET /accounts/{test_account_id} (verify update)", "GET", f"/accounts/{test_account_id}")
    if isinstance(updated, dict) and updated.get("risk_score") != 0.42:
        print(f"  !! update did not persist as expected: got risk_score={updated.get('risk_score')}")
    check(f"DELETE /accounts/{test_account_id} (cleanup)", "DELETE", f"/accounts/{test_account_id}")
    check(f"GET /accounts/{test_account_id} (verify delete, expect 404)", "GET", f"/accounts/{test_account_id}", expect=404)

    # --- Accounts ---
    accounts = check("GET /accounts", "GET", "/accounts?limit=5")
    sample_account = None
    if isinstance(accounts, list) and accounts:
        sample_account = accounts[0]["account_id"]
        check(f"GET /accounts/{sample_account}", "GET", f"/accounts/{sample_account}")
        check(f"GET /accounts/{sample_account}/connections", "GET", f"/accounts/{sample_account}/connections")
        check(f"GET /accounts/{sample_account}/transactions", "GET", f"/accounts/{sample_account}/transactions?limit=5")
    else:
        print("!! No accounts returned \u2014 did you run scripts/seed_db.py? Skipping account-dependent checks. !!")

    check("GET /accounts/DOES_NOT_EXIST (expect 404)", "GET", "/accounts/DOES_NOT_EXIST", expect=404)

    # --- Graph analytics ---
    if sample_account:
        check(f"GET /graph/direct-transactions/{sample_account}", "GET", f"/graph/direct-transactions/{sample_account}")
        check(f"GET /graph/multi-hop/{sample_account}", "GET", f"/graph/multi-hop/{sample_account}?max_hops=3")
        check(f"GET /graph/shared-device/{sample_account}", "GET", f"/graph/shared-device/{sample_account}")
        check(f"GET /graph/shared-ip/{sample_account}", "GET", f"/graph/shared-ip/{sample_account}")

    check("GET /graph/suspicious-chains", "GET", "/graph/suspicious-chains?min_amount=5000")
    check("GET /graph/high-connectivity", "GET", "/graph/high-connectivity?min_degree=5")
    components = check("GET /graph/components", "GET", "/graph/components")
    communities = check("GET /graph/communities", "GET", "/graph/communities")
    pagerank = check("GET /graph/pagerank", "GET", "/graph/pagerank")
    cycles = check("GET /graph/cycles", "GET", "/graph/cycles?max_cycle_length=6")

    # --- Fraud rings ---
    rings = check("GET /fraud-rings", "GET", "/fraud-rings")
    if isinstance(rings, list) and rings:
        first_ring = rings[0]["ring_id"]
        check(f"GET /fraud-rings/{first_ring}", "GET", f"/fraud-rings/{first_ring}")

    # --- Write path (create + cleanup) ---
    if sample_account and isinstance(accounts, list) and len(accounts) > 1:
        other_account = accounts[1]["account_id"]
        txn_body = {
            "txn_id": "TXN_SMOKETEST_0001",
            "from_account": sample_account,
            "to_account": other_account,
            "amount": 42.5,
            "currency": "INR",
            "timestamp": "2026-09-24T12:00:00",
            "status": "completed",
        }
        check("POST /transactions (create)", "POST", "/transactions", body=txn_body, expect=201)
        check("GET /transactions/TXN_SMOKETEST_0001", "GET", "/transactions/TXN_SMOKETEST_0001")
        check("PUT /transactions/TXN_SMOKETEST_0001 (update)", "PUT", "/transactions/TXN_SMOKETEST_0001",
              body={"status": "flagged"}, expect=200)
        updated_txn = check("GET /transactions/TXN_SMOKETEST_0001 (verify update)", "GET", "/transactions/TXN_SMOKETEST_0001")
        if isinstance(updated_txn, dict) and updated_txn.get("status") != "flagged":
            print(f"  !! update did not persist as expected: got status={updated_txn.get('status')}")
        check("DELETE /transactions/TXN_SMOKETEST_0001 (cleanup)", "DELETE", "/transactions/TXN_SMOKETEST_0001")

    # --- Summary ---
    print("\n== Summary ==")
    passed = sum(1 for _, s, _ in results if s == PASS)
    failed = [r for r in results if r[1] == FAIL]
    print(f"{passed}/{len(results)} checks passed.")
    if failed:
        print("\nFailed checks:")
        for name, _, note in failed:
            print(f"  - {name}: {note}")
        sys.exit(1)

    if isinstance(rings, list):
        print(f"\nFraud rings detected: {len(rings)}")
    if isinstance(cycles, list):
        print(f"Transaction cycles detected: {len(cycles)}")
    if isinstance(components, list):
        print(f"Weakly connected components: {len(components)}")
    if isinstance(communities, list):
        print(f"Louvain communities: {len(communities)}")
    if isinstance(pagerank, list):
        print(f"PageRank scores computed for {len(pagerank)} accounts")


if __name__ == "__main__":
    main()
