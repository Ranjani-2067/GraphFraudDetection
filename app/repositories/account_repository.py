from __future__ import annotations
from typing import Optional
from app.database.neo4j import Neo4jConnection
class AccountRepository:
    def __init__(self,conn): self.conn=conn
    def create(self,account):
        rows=self.conn.run_write("""CREATE (a:Account {account_id:$account_id,name:$name,account_type:$account_type,risk_score:$risk_score,created_date:$created_date}) RETURN a""",account)
        if account.get("bank_id"):
            rows2=self.conn.run_query("MATCH (a:Account {account_id:$account_id}),(b:Bank {bank_id:$bank_id}) MERGE (a)-[:HOLDS_ACCOUNT_AT]->(b) RETURN count(*) AS c",{"account_id":account["account_id"],"bank_id":account["bank_id"]})
            if not rows2 or rows2[0]["c"] == 0: raise ValueError("Bank not found")
        return _clean(rows[0]["a"])
    def exists(self,account_id): return bool(self.conn.run_query("MATCH (a:Account {account_id:$account_id}) RETURN count(a) AS c",{"account_id":account_id})[0]["c"])
    def get(self,account_id):
        rows=self.conn.run_query("MATCH (a:Account {account_id:$account_id}) RETURN a",{"account_id":account_id}); return _clean(rows[0]["a"]) if rows else None
    def update(self,account_id,updates):
        if not updates:return self.get(account_id)
        allowed={k:v for k,v in updates.items() if k in {"name","account_type","risk_score"} and v is not None}
        if not allowed:return self.get(account_id)
        clause=", ".join(f"a.{k}=${k}" for k in allowed)
        rows=self.conn.run_write(f"MATCH (a:Account {{account_id:$account_id}}) SET {clause} RETURN a",{"account_id":account_id,**allowed})
        return _clean(rows[0]["a"]) if rows else None
    def delete(self,account_id):
        rows=self.conn.run_write("MATCH (a:Account {account_id:$account_id}) WITH a, count(a) AS found DETACH DELETE a RETURN found",{"account_id":account_id}); return bool(rows and rows[0]["found"])
    def list_accounts(self,limit=50,offset=0):
        rows=self.conn.run_query("MATCH (a:Account) RETURN a ORDER BY a.account_id SKIP $offset LIMIT $limit",{"offset":offset,"limit":limit}); return [_clean(r["a"]) for r in rows]
    def get_connections(self,account_id):
        devices=self.conn.run_query("MATCH (a:Account {account_id:$account_id})-[:USED_DEVICE]->(d:Device) RETURN d.device_id AS device_id,d.device_type AS device_type",{"account_id":account_id})
        ips=self.conn.run_query("MATCH (a:Account {account_id:$account_id})-[:LOGGED_IN_FROM]->(i:IPAddress) RETURN i.ip AS ip,i.geo_location AS geo_location",{"account_id":account_id})
        bank=self.conn.run_query("MATCH (a:Account {account_id:$account_id})-[:HOLDS_ACCOUNT_AT]->(b:Bank) RETURN b.bank_id AS bank_id,b.bank_name AS bank_name",{"account_id":account_id})
        shared=self.conn.run_query("MATCH (a:Account {account_id:$account_id})-[:SHARES_DEVICE_WITH]-(p:Account) RETURN DISTINCT p.account_id AS account_id",{"account_id":account_id})
        shared_ip=self.conn.run_query("MATCH (a:Account {account_id:$account_id})-[:LOGGED_IN_FROM]->(:IPAddress)<-[:LOGGED_IN_FROM]-(p:Account) WHERE p.account_id<>$account_id RETURN DISTINCT p.account_id AS account_id",{"account_id":account_id})
        return {"devices":devices,"ips":ips,"bank":bank[0] if bank else None,"shared_device_peers":[r["account_id"] for r in shared],"shared_ip_peers":[r["account_id"] for r in shared_ip]}
    def get_transactions(self,account_id,limit=100):
        return self.conn.run_query("""MATCH (s:Account)-[:SENT]->(t:Transaction)-[:RECEIVED_BY]->(r:Account) WHERE s.account_id=$account_id OR r.account_id=$account_id RETURN t.txn_id AS txn_id,s.account_id AS from_account,r.account_id AS to_account,t.amount AS amount,t.currency AS currency,t.timestamp AS timestamp,t.status AS status ORDER BY t.timestamp DESC LIMIT $limit""",{"account_id":account_id,"limit":limit})
def _clean(node): return {k:v for k,v in node.items() if not k.startswith("_")}
