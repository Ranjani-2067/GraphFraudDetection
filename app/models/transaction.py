from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field
class TransactionCreate(BaseModel):
    txn_id:str=Field(...,min_length=1,max_length=64); from_account:str=Field(...,min_length=1); to_account:str=Field(...,min_length=1); amount:float=Field(...,gt=0); currency:str=Field("INR",min_length=3,max_length=3); timestamp:str=Field(...); status:str=Field("completed",pattern="^(completed|pending|flagged)$")
class TransactionUpdate(BaseModel):
    amount:Optional[float]=Field(None,gt=0); status:Optional[str]=Field(None,pattern="^(completed|pending|flagged)$")
class TransactionResponse(BaseModel):
    txn_id:str; from_account:str; to_account:str; amount:float; currency:str; timestamp:str; status:str
