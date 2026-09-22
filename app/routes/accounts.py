from fastapi import APIRouter,Depends,HTTPException,Query,status
from app.models.account import AccountCreate,AccountUpdate
from app.repositories.account_repository import AccountRepository
from app.routes.dependencies import account_repo
router=APIRouter(prefix="/accounts",tags=["Accounts"])
@router.post("",status_code=status.HTTP_201_CREATED)
def create_account(body:AccountCreate,repo:AccountRepository=Depends(account_repo)):
    if repo.exists(body.account_id): raise HTTPException(409,"Account already exists")
    try:return repo.create(body.model_dump())
    except Exception as exc: raise HTTPException(400,str(exc)) from exc
@router.get("")
def list_accounts(limit:int=Query(50,ge=1,le=500),offset:int=Query(0,ge=0),repo:AccountRepository=Depends(account_repo)): return repo.list_accounts(limit,offset)
@router.get("/{account_id}")
def get_account(account_id:str,repo:AccountRepository=Depends(account_repo)):
    item=repo.get(account_id)
    if item is None: raise HTTPException(404,"Account not found")
    return item
@router.put("/{account_id}")
def update_account(account_id:str,body:AccountUpdate,repo:AccountRepository=Depends(account_repo)):
    if not repo.exists(account_id): raise HTTPException(404,"Account not found")
    return repo.update(account_id,body.model_dump(exclude_none=True))
@router.delete("/{account_id}")
def delete_account(account_id:str,repo:AccountRepository=Depends(account_repo)):
    if not repo.delete(account_id): raise HTTPException(404,"Account not found")
    return {"deleted":True,"account_id":account_id}
@router.get("/{account_id}/connections")
def connections(account_id:str,repo:AccountRepository=Depends(account_repo)):
    if not repo.exists(account_id): raise HTTPException(404,"Account not found")
    return repo.get_connections(account_id)
@router.get("/{account_id}/transactions")
def transactions(account_id:str,limit:int=Query(100,ge=1,le=500),repo:AccountRepository=Depends(account_repo)):
    if not repo.exists(account_id): raise HTTPException(404,"Account not found")
    return repo.get_transactions(account_id,limit)
