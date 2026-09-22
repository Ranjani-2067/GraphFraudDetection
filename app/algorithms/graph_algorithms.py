from __future__ import annotations
import networkx as nx
from app.algorithms.graph_projection import build_directed_multigraph, build_simple_weighted_graph

class GraphAnalytics:
    def __init__(self,conn): self.conn=conn
    def weak_components(self):
        g=build_directed_multigraph(self.conn); comps=sorted(nx.weakly_connected_components(g),key=lambda x:(-len(x),sorted(x)[0] if x else "")); return [{"component_id":i,"member_accounts":sorted(c),"component_size":len(c)} for i,c in enumerate(comps)]
    def louvain(self):
        g=build_simple_weighted_graph(self.conn).to_undirected()
        if not g.nodes:return []
        communities=nx.community.louvain_communities(g,weight="weight",seed=42)
        communities=sorted(communities,key=lambda c:(-len(c),sorted(c)[0] if c else ""))
        return [{"community_id":i,"member_accounts":sorted(c),"community_size":len(c)} for i,c in enumerate(communities)]
    def pagerank(self):
        g=build_simple_weighted_graph(self.conn); scores=nx.pagerank(g,weight="weight") if g.nodes else {}; return [{"account_id":a,"score":float(s)} for a,s in sorted(scores.items(),key=lambda x:(-x[1],x[0]))]
    def cycles(self,max_cycle_length=6,max_cycles=100):
        g=build_directed_multigraph(self.conn); result=[]; seen=set()
        for cyc in nx.simple_cycles(nx.DiGraph(g), length_bound=max_cycle_length):
            if len(cyc)<2 or len(cyc)>max_cycle_length: continue
            key=min(tuple(cyc[i:]+cyc[:i]) for i in range(len(cyc)))
            if key in seen: continue
            seen.add(key); txns=[]
            for i,u in enumerate(cyc):
                v=cyc[(i+1)%len(cyc)]; data=g.get_edge_data(u,v) or {}; first=next(iter(data.values()),None)
                if first: txns.append(first.get("txn_id"))
            result.append({"accounts":cyc,"transactions":txns,"length":len(cyc)})
            if len(result)>=max_cycles: break
        return result
