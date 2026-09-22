import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.database.neo4j import get_connection
from app.database.schema import wipe_all_data
if __name__ == "__main__":
    conn=get_connection()
    if not conn.verify_connectivity(): raise SystemExit("Neo4j is not reachable.")
    wipe_all_data(conn)
    print("All Neo4j data deleted. Constraints and indexes were retained.")
    conn.close()
