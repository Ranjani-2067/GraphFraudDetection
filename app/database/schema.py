from __future__ import annotations
from app.database.neo4j import Neo4jConnection

CONSTRAINT_STATEMENTS = [
    "CREATE CONSTRAINT account_id_unique IF NOT EXISTS FOR (a:Account) REQUIRE a.account_id IS UNIQUE",
    "CREATE CONSTRAINT txn_id_unique IF NOT EXISTS FOR (t:Transaction) REQUIRE t.txn_id IS UNIQUE",
    "CREATE CONSTRAINT device_id_unique IF NOT EXISTS FOR (d:Device) REQUIRE d.device_id IS UNIQUE",
    "CREATE CONSTRAINT ip_address_unique IF NOT EXISTS FOR (i:IPAddress) REQUIRE i.ip IS UNIQUE",
    "CREATE CONSTRAINT bank_id_unique IF NOT EXISTS FOR (b:Bank) REQUIRE b.bank_id IS UNIQUE",
    "CREATE CONSTRAINT ring_id_unique IF NOT EXISTS FOR (r:FraudRing) REQUIRE r.ring_id IS UNIQUE",
]
INDEX_STATEMENTS = [
    "CREATE INDEX account_risk_score_idx IF NOT EXISTS FOR (a:Account) ON (a.risk_score)",
    "CREATE INDEX txn_timestamp_idx IF NOT EXISTS FOR (t:Transaction) ON (t.timestamp)",
    "CREATE INDEX txn_status_idx IF NOT EXISTS FOR (t:Transaction) ON (t.status)",
]

def initialize_schema(conn: Neo4jConnection):
    for stmt in CONSTRAINT_STATEMENTS + INDEX_STATEMENTS:
        conn.run_write(stmt)
    return {"constraints": len(CONSTRAINT_STATEMENTS), "indexes": len(INDEX_STATEMENTS)}

def drop_all_constraints_and_indexes(conn: Neo4jConnection):
    for row in conn.run_query("SHOW CONSTRAINTS YIELD name RETURN name"):
        name = row.get("name")
        if name:
            conn.run_write(f"DROP CONSTRAINT `{name}` IF EXISTS")
    for row in conn.run_query("SHOW INDEXES YIELD name, type RETURN name, type"):
        name = row.get("name")
        if name:
            conn.run_write(f"DROP INDEX `{name}` IF EXISTS")

def wipe_all_data(conn: Neo4jConnection):
    conn.run_write("MATCH (n) DETACH DELETE n")
