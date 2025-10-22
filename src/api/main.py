from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import uvicorn
from contextlib import asynccontextmanager


from ..domains.fraud import FraudDomainProcessor
from ..domains.social import SocialDomainProcessor
from ..persistence.neo4j_repo import Neo4jRepository
from ..utils.monitoring import MetricsCollector
from ..api.middleware import RateLimiter

# Pydantic models
class Transaction(BaseModel):
    transaction_id: str
    sender: str
    receiver: str
    amount: float
    timestamp: str
    upi_handle: Optional[str] = None

class AnomalyRequest(BaseModel):
    domain: str
    data: List[Dict]
    incremental: bool = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Neo4j, Redis, Metrics
    app.state.neo4j = Neo4jRepository()
    app.state.metrics = MetricsCollector()
    app.state.processors = {
        'fraud': FraudDomainProcessor(),
        'social': SocialDomainProcessor(),
        # Add more domains
    }
    yield
    # Shutdown
    await app.state.neo4j.close()


import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
app = FastAPI(
    title="Graph Anomaly Detection Platform",
    description="Production-grade anomaly detection using graph algorithms",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(CORSMiddleware, allow_origins=["*"])
app.add_middleware(RateLimiter)

@app.post("/v1/{domain}/analyze")
async def analyze_anomalies(
    domain: str,
    request: AnomalyRequest,
    neo4j: Neo4jRepository = Depends(lambda a: a.state.neo4j),
    metrics: MetricsCollector = Depends(lambda a: a.state.metrics)
):
    """Main analysis endpoint with domain routing"""
    
    processor = app.state.processors.get(domain)
    if not processor:
        raise HTTPException(status_code=400, detail=f"Domain {domain} not supported")
    
    try:
        # Record metrics
        metrics.increment(f"analysis_requests_{domain}")
        
        # Process data
        result = processor.process_data(request.data, incremental=request.incremental)
        
        # Persist results
        await neo4j.store_analysis_results(domain, result)
        
        # Record success metrics
        metrics.increment(f"successful_analyses_{domain}")
        metrics.set_gauge(f"anomalies_detected_{domain}", len(result.get('anomalies', [])))
        
        return {
            "status": "success",
            "domain": domain,
            "results": result,
            "processed_at": datetime.now().isoformat()
        }
    
    except Exception as e:
        metrics.increment(f"analysis_errors_{domain}")
        logger.error(f"Analysis failed for {domain}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "graph-anomaly-platform"}

@app.get("/metrics")
async def prometheus_metrics(metrics: MetricsCollector = Depends(lambda a: a.state.metrics)):
    return metrics.generate_prometheus()

if __name__ == "__main__":
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)