import networkx as nx
from app.algorithms.graph_algorithms import GraphAnalytics
class FakeConn:
    def run_query(self,cypher,parameters=None):
        if "MATCH (a:Account) RETURN a.account_id" in cypher:return [{"account_id":x} for x in ["A","B","C","D","E"]]
        return [
            {"source":"A","target":"B","txn_id":"T1","amount":1000},
            {"source":"B","target":"C","txn_id":"T2","amount":900},
            {"source":"C","target":"D","txn_id":"T3","amount":800},
            {"source":"D","target":"A","txn_id":"T4","amount":700},
            {"source":"A","target":"E","txn_id":"T5","amount":50},
        ]

def test_graph_algorithms():
    a=GraphAnalytics(FakeConn())
    assert a.weak_components()[0]["component_size"]==5
    assert a.louvain()
    assert len(a.pagerank())==5
    assert any(c["length"]==4 for c in a.cycles(max_cycle_length=4))
