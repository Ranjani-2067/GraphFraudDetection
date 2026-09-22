from __future__ import annotations
from app.database.neo4j import Neo4jConnection
class TransactionRepository:
    def __init__(self,conn): self.conn=conn
    def accounts_exist(self,sender,receiver):
        rows=self.conn.run_query("MATCH (s:Account {account_id:$s}),(r:Account {account_id:$r}) RETURN count(*) AS c",{"s":sender,"r":receiver}); return bool(rows and rows[0]["c"])
    def create(self,txn):
        rows=self.conn.run_write("""MATCH (s:Account {account_id:$from_account}),(r:Account {account_id:$to_account}) CREATE (t:Transaction {txn_id:$txn_id,amount:$amount,currency:$currency,timestamp:$timestamp,status:$status}) CREATE (s)-[:SENT]->(t) CREATE (t)-[:RECEIVED_BY]->(r) RETURN t""",txn)
        node=_clean(rows[0]["t"]); node.update({"from_account":txn["from_account"],"to_account":txn["to_account"]}); return node
    def get(self,txn_id):
        rows=self.conn.run_query("MATCH (s:Account)-[:SENT]->(t:Transaction {txn_id:$txn_id})-[:RECEIVED_BY]->(r:Account) RETURN t,s.account_id AS from_account,r.account_id AS to_account",{"txn_id":txn_id})
        if not rows:return None
        node=_clean(rows[0]["t"]); node.update({"from_account":rows[0]["from_account"],"to_account":rows[0]["to_account"]}); return node
    def update(self,txn_id,updates):
        allowed={k:v for k,v in updates.items() if k in {"amount","status"} and v is not None}
        if not allowed:return self.get(txn_id)
        clause=", ".join(f"t.{k}=${k}" for k in allowed); rows=self.conn.run_write(f"MATCH (t:Transaction {{txn_id:$txn_id}}) SET {clause} RETURN t",{"txn_id":txn_id,**allowed}); return self.get(txn_id) if rows else None
    def delete(self,txn_id):
        rows=self.conn.run_write("MATCH (t:Transaction {txn_id:$txn_id}) WITH t, count(t) AS found DETACH DELETE t RETURN found",{"txn_id":txn_id}); return bool(rows and rows[0]["found"])
    def exists(self,txn_id):
        rows=self.conn.run_query("MATCH (t:Transaction {txn_id:$txn_id}) RETURN count(t) AS c",{"txn_id":txn_id}); return bool(rows and rows[0]["c"])
def _clean(node): return {k:v for k,v in node.items() if not k.startswith("_")}
