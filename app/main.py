from __future__ import annotations
from fastapi import FastAPI
from app.config import settings
from app.database.neo4j import get_connection
from app.routes import accounts,transactions,graph,fraud
app=FastAPI(title=settings.api_title,version=settings.api_version,description="Review-2 prototype for graph-based financial fraud detection using Neo4j.")
app.include_router(accounts.router); app.include_router(transactions.router); app.include_router(graph.router); app.include_router(fraud.router)
@app.get("/health",tags=["System"])
def health():
    conn=get_connection(); connected=conn.verify_connectivity(); gds=None; detail=None
    if connected:
        try:
            rows=conn.run_query("RETURN gds.version() AS version")
            gds=bool(rows and rows[0].get("version"))
        except Exception:
            gds=False
    else: detail="Neo4j is not reachable. Start Neo4j and verify NEO4J_URI/NEO4J_USER/NEO4J_PASSWORD."
    return {"status":"ok" if connected else "degraded","neo4j_connected":connected,"gds_available":gds,"detail":detail}
@app.get("/",tags=["System"])
def root(): return {"project":"Graph-Based Financial Fraud Detection","version":settings.api_version,"docs":"/docs"}
