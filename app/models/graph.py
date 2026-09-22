from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field
class ComponentResult(BaseModel): component_id:int; member_accounts:list[str]; component_size:int
class CommunityResult(BaseModel): community_id:int; member_accounts:list[str]; community_size:int
class PageRankResult(BaseModel): account_id:str; score:float
class CycleResult(BaseModel): accounts:list[str]; transactions:list[str]; length:int
class FraudRingResult(BaseModel):
    ring_id:str; member_accounts:list[str]; signals:list[str]; community_id:Optional[int]=None; component_id:Optional[int]=None; related_transactions:list[str]=Field(default_factory=list); risk_score:float; risk_score_type:str="heuristic"
class HealthResponse(BaseModel): status:str; neo4j_connected:bool; gds_available:Optional[bool]=None; detail:Optional[str]=None
