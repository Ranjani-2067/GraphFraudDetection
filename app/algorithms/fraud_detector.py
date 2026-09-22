from __future__ import annotations
from collections import defaultdict
class FraudDetector:
    def __init__(self,analytics,graph_repo): self.analytics=analytics; self.graph_repo=graph_repo
    def detect(self):
        communities=self.analytics.louvain(); components=self.analytics.weak_components(); ranks=self.analytics.pagerank(); cycles=self.analytics.cycles()
        community_by={a:c["community_id"] for c in communities for a in c["member_accounts"]}; component_by={a:c["component_id"] for c in components for a in c["member_accounts"]}; rank_by={r["account_id"]:r["score"] for r in ranks}
        signals=defaultdict(set); related=defaultdict(set)
        for cyc in cycles:
            for a in cyc["accounts"]: signals[a].add("transaction_cycle"); related[a].update(x for x in cyc["transactions"] if x)
        for row in self.graph_repo.suspicious_chains():
            for a in (row["hop1"],row["hop2"],row["hop3"]): signals[a].add("similar_amount_layering")
            for t in (row["txn1"],row["txn2"]):
                for a in (row["hop1"],row["hop2"],row["hop3"]): related[a].add(t)
        # Shared device/IP signals are computed from graph patterns rather than ground-truth labels.
        for row in self.graph_repo.highly_connected_accounts(min_degree=10): signals[row["account_id"]].add("high_connectivity")
        # Aggregate device/IP peers for all accounts only where shared relationships exist.
        for row in self.graph_repo.conn.run_query("MATCH (a:Account)-[:SHARES_DEVICE_WITH]-(b:Account) WHERE a.account_id < b.account_id RETURN a.account_id AS a,b.account_id AS b"):
            signals[row["a"]].add("shared_device"); signals[row["b"]].add("shared_device")
        for row in self.graph_repo.conn.run_query("MATCH (a:Account)-[:LOGGED_IN_FROM]->(i:IPAddress)<-[:LOGGED_IN_FROM]-(b:Account) WHERE a.account_id < b.account_id RETURN a.account_id AS a,b.account_id AS b"):
            signals[row["a"]].add("shared_ip"); signals[row["b"]].add("shared_ip")
        groups=defaultdict(set)
        for account,sigs in signals.items():
            if sigs: groups[community_by.get(account,-1)].add(account)
        results=[]
        for idx,(community,accounts) in enumerate(sorted(groups.items(),key=lambda x:(x[0],sorted(x[1]))),1):
            if len(accounts)<2: continue
            sig=sorted({s for a in accounts for s in signals[a]}); risk=min(1.0,0.15*len(sig)+0.05*min(len(accounts),10)+sum(rank_by.get(a,0) for a in accounts))
            txns=sorted({t for a in accounts for t in related[a]})
            results.append({"ring_id":f"RING{idx:03d}","member_accounts":sorted(accounts),"signals":sig,"community_id":None if community==-1 else community,"component_id":component_by.get(next(iter(accounts))),"related_transactions":txns[:50],"risk_score":round(risk,4),"risk_score_type":"heuristic"})
        return results
