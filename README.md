# Graph-Based Financial Fraud Detection — Review 2 Codebase

Neo4j + FastAPI implementation for the Review-2 prototype.

## Quick start

1. Copy `.env.example` to `.env`.
2. Start Neo4j: `docker compose up -d`.
3. Install dependencies: `python -m pip install -r requirements.txt`.
4. Generate deterministic data: `python scripts/generate_dataset.py`.
5. Initialize schema: `python scripts/init_db.py`.
6. Load data: `python scripts/seed_db.py`.
7. Start API: `python run.py`.
8. Open `http://127.0.0.1:8000/docs`.

The graph algorithms use NetworkX over the account transaction graph, so the core prototype does not require the optional Neo4j GDS plugin. If GDS is installed, `/health` reports its availability.

## Reset

`python scripts/reset_db.py` deletes all graph data while retaining constraints/indexes.

## Tests

`pytest -q`
