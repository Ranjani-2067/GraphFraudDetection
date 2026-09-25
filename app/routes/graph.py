from typing import Optional
from fastapi import APIRouter,Depends,Query
from app.routes.dependencies import graph_repo,analytics
from app.repositories.graph_repository import GraphRepository
from app.algorithms.graph_algorithms import GraphAnalytics
router=APIRouter(prefix="/graph",tags=["Graph Analytics"])
@router.get("/direct-transactions/{account_id}")
def direct(account_id:str,repo:GraphRepository=Depends(graph_repo)): return repo.direct_transactions(account_id)
@router.get("/multi-hop/{account_id}")
def multihop(account_id:str,max_hops:int=Query(4,ge=1,le=6),repo:GraphRepository=Depends(graph_repo)): return repo.multi_hop_paths(account_id,max_hops)
@router.get("/shared-device/{account_id}")
def shared_device(account_id:str,repo:GraphRepository=Depends(graph_repo)): return repo.accounts_sharing_device(account_id)
@router.get("/shared-ip/{account_id}")
def shared_ip(account_id:str,repo:GraphRepository=Depends(graph_repo)): return repo.accounts_sharing_ip(account_id)
@router.get("/suspicious-chains")
def suspicious(min_amount:float=Query(5000,gt=0),repo:GraphRepository=Depends(graph_repo)): return repo.suspicious_chains(min_amount)
@router.get("/high-connectivity")
def high_connectivity(min_degree:int=Query(10,ge=1),repo:GraphRepository=Depends(graph_repo)): return repo.highly_connected_accounts(min_degree)
@router.get("/components")
def components(a:GraphAnalytics=Depends(analytics)): return a.weak_components()
@router.get("/communities")
def communities(a:GraphAnalytics=Depends(analytics)): return a.louvain()
@router.get("/pagerank")
def pagerank(a:GraphAnalytics=Depends(analytics)): return a.pagerank()
@router.get("/cycles")
def cycles(max_cycle_length:int=Query(6,ge=2,le=8),max_cycles:int=Query(100,ge=1,le=500),max_span_days:Optional[int]=Query(14,ge=1,description="Filter out cycles whose transactions span more than this many days; omit for unfiltered structural cycles."),a:GraphAnalytics=Depends(analytics)): return a.cycles(max_cycle_length,max_cycles,max_span_days)
