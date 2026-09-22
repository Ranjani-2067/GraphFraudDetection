from pathlib import Path
from app.services.dataset_generator import generate_dataset, write_dataset_to_csv

def test_dataset_is_deterministic(tmp_path:Path):
    a=generate_dataset(seed=42,num_accounts=30,num_normal_transactions=80); b=generate_dataset(seed=42,num_accounts=30,num_normal_transactions=80)
    assert a.accounts==b.accounts and a.transactions==b.transactions and a.account_device==b.account_device

def test_dataset_contains_signals(tmp_path:Path):
    ds=generate_dataset(seed=42,num_accounts=40,num_normal_transactions=100)
    assert len(ds.accounts)==40; assert len(ds.transactions)>100; assert ds.suspicious_account_ids
    paths=write_dataset_to_csv(ds,tmp_path)
    assert set(paths)=={"banks.csv","accounts.csv","devices.csv","ips.csv","transactions.csv","account_bank.csv","account_device.csv","account_ip.csv"}
    assert all(Path(p).exists() for p in paths.values())
