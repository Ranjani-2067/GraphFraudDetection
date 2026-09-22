from __future__ import annotations
import csv
import os
from app.database.neo4j import Neo4jConnection
BATCH_SIZE = 500

def _read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def _batches(rows, size=BATCH_SIZE):
    for i in range(0, len(rows), size):
        yield rows[i:i + size]

def _load(conn, rows, cypher):
    for batch in _batches(rows):
        if batch:
            conn.run_write(cypher, {"rows": batch})
    return len(rows)

def load_banks(conn, rows):
    return _load(conn, rows, """UNWIND $rows AS row MERGE (b:Bank {bank_id: row.bank_id}) SET b.bank_name=row.bank_name, b.branch_code=row.branch_code""")
def load_accounts(conn, rows):
    return _load(conn, rows, """UNWIND $rows AS row MERGE (a:Account {account_id: row.account_id}) SET a.name=row.name, a.account_type=row.account_type, a.risk_score=toFloat(row.risk_score), a.created_date=row.created_date""")
def load_devices(conn, rows):
    return _load(conn, rows, """UNWIND $rows AS row MERGE (d:Device {device_id: row.device_id}) SET d.device_type=row.device_type""")
def load_ips(conn, rows):
    return _load(conn, rows, """UNWIND $rows AS row MERGE (i:IPAddress {ip: row.ip}) SET i.geo_location=row.geo_location""")
def load_account_bank(conn, rows):
    return _load(conn, rows, """UNWIND $rows AS row MATCH (a:Account {account_id: row.account_id}), (b:Bank {bank_id: row.bank_id}) MERGE (a)-[:HOLDS_ACCOUNT_AT]->(b)""")
def load_account_device(conn, rows):
    return _load(conn, rows, """UNWIND $rows AS row MATCH (a:Account {account_id: row.account_id}), (d:Device {device_id: row.device_id}) MERGE (a)-[:USED_DEVICE]->(d)""")
def load_account_ip(conn, rows):
    return _load(conn, rows, """UNWIND $rows AS row MATCH (a:Account {account_id: row.account_id}), (i:IPAddress {ip: row.ip}) MERGE (a)-[:LOGGED_IN_FROM]->(i)""")
def load_transactions(conn, rows):
    return _load(conn, rows, """UNWIND $rows AS row MATCH (s:Account {account_id: row.from_account}), (r:Account {account_id: row.to_account}) MERGE (t:Transaction {txn_id: row.txn_id}) SET t.amount=toFloat(row.amount), t.currency=row.currency, t.timestamp=row.timestamp, t.status=row.status MERGE (s)-[:SENT]->(t) MERGE (t)-[:RECEIVED_BY]->(r)""")
def derive_shared_device_edges(conn):
    rows = conn.run_write("""MATCH (a1:Account)-[:USED_DEVICE]->(d:Device)<-[:USED_DEVICE]-(a2:Account) WHERE a1.account_id < a2.account_id MERGE (a1)-[r:SHARES_DEVICE_WITH]->(a2) SET r.via_device=d.device_id RETURN count(r) AS count""")
    return rows[0]["count"] if rows else 0

def run_full_ingestion(conn, data_dir):
    report = {}
    loaders = [("banks.csv","banks",load_banks),("accounts.csv","accounts",load_accounts),("devices.csv","devices",load_devices),("ips.csv","ips",load_ips),("account_bank.csv","account_bank_edges",load_account_bank),("account_device.csv","account_device_edges",load_account_device),("account_ip.csv","account_ip_edges",load_account_ip),("transactions.csv","transactions",load_transactions)]
    for filename, key, loader in loaders:
        path = os.path.join(data_dir, filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing dataset file: {path}")
        report[key] = loader(conn, _read_csv(path))
    report["shares_device_with_edges"] = derive_shared_device_edges(conn)
    return report
