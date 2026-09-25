"""
Compares /fraud-rings output from the running API against the dataset
generator's known ground-truth suspicious accounts.

Run this AFTER the API is up and seeded with the same seed/params as
your .env (defaults: seed=42, 120 accounts, 400 normal transactions).

Usage:
    python verify_ground_truth.py
    python verify_ground_truth.py --base-url http://127.0.0.1:8000
"""
from __future__ import annotations
import argparse
import json
import urllib.request

from app.config import settings
from app.services.dataset_generator import generate_dataset


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default="http://127.0.0.1:8000")
    args = ap.parse_args()

    # Regenerate the SAME dataset (same seed -> same accounts, deterministic)
    ds = generate_dataset(
        seed=settings.dataset_seed,
        num_accounts=settings.num_accounts,
        num_normal_transactions=settings.num_normal_transactions,
    )
    ground_truth = ds.suspicious_account_ids
    print(f"Ground-truth suspicious accounts (from generator): {len(ground_truth)}")

    # Pull what the live API currently flags
    url = f"{args.base_url.rstrip('/')}/fraud-rings"
    with urllib.request.urlopen(url, timeout=15) as resp:
        rings = json.loads(resp.read().decode())

    detected = set()
    for ring in rings:
        detected.update(ring.get("member_accounts", []))
    print(f"Accounts flagged across {len(rings)} detected rings: {len(detected)}")

    true_positives = ground_truth & detected
    missed = ground_truth - detected
    extra = detected - ground_truth

    print(f"\nTrue positives (known-suspicious AND flagged): {len(true_positives)}")
    print(f"Missed (known-suspicious but NOT flagged):       {len(missed)}")
    print(f"Extra (flagged but not deliberately suspicious): {len(extra)}")

    if ground_truth:
        recall = len(true_positives) / len(ground_truth)
        print(f"\nRecall on synthetic ground truth: {recall:.1%}")
    if detected:
        precision = len(true_positives) / len(detected)
        print(f"Precision on synthetic ground truth: {precision:.1%}")

    print("\nNote: 'extra' accounts aren't necessarily false positives \u2014 the generator's")
    print("normal-transaction traffic can coincidentally form patterns too (e.g. an account")
    print("that happens to sit in a cycle by chance). Worth a line in your report either way.")


if __name__ == "__main__":
    main()
