from fastapi import APIRouter,Depends
from app.algorithms.fraud_detector import FraudDetector
from app.routes.dependencies import detector
router=APIRouter(prefix="/fraud-rings",tags=["Fraud Detection"])
@router.get("")
def rings(d:FraudDetector=Depends(detector)): return d.detect()
@router.get("/{ring_id}")
def ring(ring_id:str,d:FraudDetector=Depends(detector)):
    for item in d.detect():
        if item["ring_id"]==ring_id:return item
    return {"detail":"Fraud ring not found"}
