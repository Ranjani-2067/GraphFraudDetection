from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field
class AccountCreate(BaseModel):
    account_id:str=Field(...,min_length=1,max_length=64); name:str=Field(...,min_length=1,max_length=200); account_type:str=Field(...,pattern="^(savings|checking|business)$"); bank_id:Optional[str]=None; risk_score:float=Field(0.0,ge=0,le=1); created_date:Optional[str]=None
class AccountUpdate(BaseModel):
    name:Optional[str]=Field(None,min_length=1,max_length=200); account_type:Optional[str]=Field(None,pattern="^(savings|checking|business)$"); risk_score:Optional[float]=Field(None,ge=0,le=1)
class AccountResponse(BaseModel):
    account_id:str; name:str; account_type:str; risk_score:float; created_date:Optional[str]=None
