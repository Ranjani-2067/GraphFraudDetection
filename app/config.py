from __future__ import annotations
import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")

def _get_bool(name: str, default: bool) -> bool:
    val = os.getenv(name)
    return default if val is None else val.strip().lower() in {"1", "true", "yes", "on"}

@dataclass(frozen=True)
class Settings:
    neo4j_uri: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user: str = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password: str = os.getenv("NEO4J_PASSWORD", "password")
    neo4j_database: str = os.getenv("NEO4J_DATABASE", "neo4j")
    gds_enabled: bool = _get_bool("GDS_ENABLED", False)
    dataset_seed: int = int(os.getenv("DATASET_SEED", "42"))
    num_accounts: int = int(os.getenv("NUM_ACCOUNTS", "120"))
    num_normal_transactions: int = int(os.getenv("NUM_NORMAL_TRANSACTIONS", "400"))
    api_title: str = "Graph-Based Financial Fraud Detection API"
    api_version: str = "1.0.0-review2"
    data_dir: str = os.getenv("DATA_DIR", str(ROOT_DIR / "data"))

settings = Settings()
