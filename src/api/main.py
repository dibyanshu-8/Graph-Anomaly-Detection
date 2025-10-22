# src/api/main.py

from fastapi import FastAPI, HTTPException, Depends, Response
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
import logging # Import the logging library

# Import from our own modules
from ..domains.fraud import FraudDomainProcessor
from ..persistence.neo4j_repo import Neo4jRepository
from ..utils.monitoring import metrics_collector
from .middleware import rate_limit
from .models import AnomalyRequest

# This function runs on startup and shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("INFO:     Starting up application...")
    app.state.neo4j = Neo4jRepository()
    app.state.processors = {'fraud': FraudDomainProcessor()}
    metrics_collector.start_server()
    yield
    print("INFO:     Shutting down application...")
    # --- FIX: Removed 'await' from the close call ---
    app.state.neo4j.close()

# Create the main FastAPI application instance
app = FastAPI(
    title="Graph Anomaly Detection Platform",
    description="Production-grade anomaly detection using graph algorithms",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(CORSMiddleware, allow_origins=["*"])

@app.post("/v1/{domain}/analyze", dependencies=[Depends(rate_limit(limit=20, per=60))])
async def analyze_anomalies(domain: str, request: AnomalyRequest):
    processor = app.state.processors.get(domain)
    if not processor:
        raise HTTPException(status_code=400, detail=f"Domain '{domain}' not supported")
    
    try:
        metrics_collector.increment("analysis_requests", domain=domain)
        result = processor.process_data(request.data, incremental=request.incremental)
        await app.state.neo4j.store_analysis_results(domain, result)
        metrics_collector.increment("successful_analyses", domain=domain)
        metrics_collector.set_gauge("anomalies_detected", len(result.get('anomalies', [])), domain=domain)
        
        return {
            "status": "success",
            "domain": domain,
            "results": result,
            "processed_at": datetime.now().isoformat()
        }
    
    except Exception as e:
        # --- FIX: Added detailed logging to see the real error in the terminal ---
        logging.exception(f"An error occurred during analysis for domain '{domain}': {e}")
        metrics_collector.increment("analysis_errors", domain=domain)
        raise HTTPException(status_code=500, detail="An internal error occurred during analysis.")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "graph-anomaly-platform"}

@app.get("/metrics")
async def prometheus_metrics():
    return Response(content=metrics_collector.generate_prometheus(), media_type="text/plain")