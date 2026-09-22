import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.database.neo4j import get_connection
from app.database.schema import initialize_schema
if __name__ == "__main__":
    conn=get_connection()
    if not conn.verify_connectivity(): raise SystemExit("Neo4j is not reachable. Start it and check .env.")
    print(initialize_schema(conn))
    conn.close()
