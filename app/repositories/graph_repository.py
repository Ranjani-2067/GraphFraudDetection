from __future__ import annotations
class GraphRepository:
    def __init__(self,conn): self.conn=conn
    def direct_transactions(self,account_id):
        return self.conn.run_query("MATCH (a:Account {account_id:$id})-[:SENT]->(t:Transaction)-[:RECEIVED_BY]->(b:Account) RETURN a.account_id AS from_account,b.account_id AS to_account,t.txn_id AS txn_id,t.amount AS amount,t.timestamp AS timestamp ORDER BY t.timestamp DESC",{"id":account_id})
    def multi_hop_paths(self,account_id,max_hops=4):
        max_hops=max(1,min(max_hops,6)); max_rel=max_hops*2
        return self.conn.run_query(f"MATCH p=(a:Account {{account_id:$id}})-[:SENT|RECEIVED_BY*1..{max_rel}]->(b:Account) WHERE a<>b WITH p,[n IN nodes(p) WHERE n:Account | n.account_id] AS chain RETURN DISTINCT chain AS account_chain,length(p) AS hops ORDER BY hops LIMIT 100",{"id":account_id})
    def accounts_sharing_device(self,account_id): return self.conn.run_query("MATCH (a:Account {account_id:$id})-[:USED_DEVICE]->(d:Device)<-[:USED_DEVICE]-(p:Account) WHERE p<>a RETURN DISTINCT p.account_id AS account_id,d.device_id AS shared_device",{"id":account_id})
    def accounts_sharing_ip(self,account_id): return self.conn.run_query("MATCH (a:Account {account_id:$id})-[:LOGGED_IN_FROM]->(i:IPAddress)<-[:LOGGED_IN_FROM]-(p:Account) WHERE p<>a RETURN DISTINCT p.account_id AS account_id,i.ip AS shared_ip",{"id":account_id})
    def suspicious_chains(self,min_amount=5000):
        return self.conn.run_query("""MATCH (a1:Account)-[:SENT]->(t1:Transaction)-[:RECEIVED_BY]->(a2:Account)-[:SENT]->(t2:Transaction)-[:RECEIVED_BY]->(a3:Account) WHERE a1<>a3 AND t1.amount >= $min_amount AND abs(t1.amount-t2.amount) < t1.amount*0.25 RETURN a1.account_id AS hop1,a2.account_id AS hop2,a3.account_id AS hop3,t1.txn_id AS txn1,t2.txn_id AS txn2,t1.amount AS amount1,t2.amount AS amount2 LIMIT 100""",{"min_amount":min_amount})
    def highly_connected_accounts(self,min_degree=10):
        return self.conn.run_query("""MATCH (a:Account) OPTIONAL MATCH (a)-[:SENT]->(out:Transaction) WITH a,count(DISTINCT out) AS out_degree OPTIONAL MATCH (in:Transaction)-[:RECEIVED_BY]->(a) WITH a,out_degree,count(DISTINCT in) AS in_degree WITH a,out_degree,in_degree,out_degree+in_degree AS total_degree WHERE total_degree >= $min RETURN a.account_id AS account_id,out_degree,in_degree,total_degree ORDER BY total_degree DESC LIMIT 50""",{"min":min_degree})
