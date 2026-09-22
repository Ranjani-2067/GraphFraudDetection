import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.config import settings
from app.database.neo4j import get_connection
from app.database.schema import initialize_schema
from app.database.seed import run_full_ingestion
if __name__ == "__main__":
    conn=get_connection()
    if not conn.verify_connectivity(): raise SystemExit("Neo4j is not reachable. Start it and check .env.")
    initialize_schema(conn)
    print(run_full_ingestion(conn,settings.data_dir))
    conn.close()
