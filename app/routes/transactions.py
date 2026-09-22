from fastapi import APIRouter,Depends,HTTPException,status
from app.models.transaction import TransactionCreate,TransactionUpdate
from app.repositories.transaction_repository import TransactionRepository
from app.routes.dependencies import transaction_repo
router=APIRouter(prefix="/transactions",tags=["Transactions"])
@router.post("",status_code=status.HTTP_201_CREATED)
def create_transaction(body:TransactionCreate,repo:TransactionRepository=Depends(transaction_repo)):
    if repo.exists(body.txn_id): raise HTTPException(409,"Transaction already exists")
    if body.from_account==body.to_account: raise HTTPException(400,"Sender and receiver must differ")
    if not repo.accounts_exist(body.from_account,body.to_account): raise HTTPException(404,"Sender or receiver account not found")
    try:return repo.create(body.model_dump())
    except Exception as exc: raise HTTPException(400,str(exc)) from exc
@router.get("/{txn_id}")
def get_transaction(txn_id:str,repo:TransactionRepository=Depends(transaction_repo)):
    item=repo.get(txn_id)
    if item is None: raise HTTPException(404,"Transaction not found")
    return item
@router.put("/{txn_id}")
def update_transaction(txn_id:str,body:TransactionUpdate,repo:TransactionRepository=Depends(transaction_repo)):
    if not repo.exists(txn_id): raise HTTPException(404,"Transaction not found")
    return repo.update(txn_id,body.model_dump(exclude_none=True))
@router.delete("/{txn_id}")
def delete_transaction(txn_id:str,repo:TransactionRepository=Depends(transaction_repo)):
    if not repo.delete(txn_id): raise HTTPException(404,"Transaction not found")
    return {"deleted":True,"txn_id":txn_id}
