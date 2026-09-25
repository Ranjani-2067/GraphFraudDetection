from __future__ import annotations
import networkx as nx
EDGES_QUERY="""MATCH (a:Account)-[:SENT]->(t:Transaction)-[:RECEIVED_BY]->(b:Account) RETURN a.account_id AS source,b.account_id AS target,t.txn_id AS txn_id,t.amount AS amount,t.timestamp AS timestamp"""
ACCOUNTS_QUERY="MATCH (a:Account) RETURN a.account_id AS account_id"
def fetch_transaction_edges(conn): return conn.run_query(EDGES_QUERY)
def fetch_account_ids(conn): return [r["account_id"] for r in conn.run_query(ACCOUNTS_QUERY)]
def build_directed_multigraph(conn):
    g=nx.MultiDiGraph(); g.add_nodes_from(fetch_account_ids(conn))
    for r in fetch_transaction_edges(conn): g.add_edge(r["source"],r["target"],txn_id=r["txn_id"],amount=float(r["amount"] or 0),timestamp=r.get("timestamp"))
    return g
def build_simple_weighted_graph(conn):
    m=build_directed_multigraph(conn); g=nx.DiGraph(); g.add_nodes_from(m.nodes())
    for u,v in m.edges(): g.add_edge(u,v,weight=g[u][v]["weight"]+1 if g.has_edge(u,v) else 1)
    return g
