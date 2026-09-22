import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.services.dataset_generator import generate_dataset, write_dataset_to_csv
if __name__ == "__main__":
    ds=generate_dataset(); paths=write_dataset_to_csv(ds)
    print(f"Generated {len(ds.accounts)} accounts and {len(ds.transactions)} transactions.")
    print(f"Synthetic suspicious ground-truth accounts: {len(ds.suspicious_account_ids)}")
    for k,v in paths.items(): print(f"{k}: {v}")
