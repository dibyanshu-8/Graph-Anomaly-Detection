# src/persistence/neo4j_repo.py

from neo4j import GraphDatabase
from typing import Dict
import os
import uuid # Import the library for generating unique IDs

class Neo4jRepository:
    """Production Neo4j integration with connection pooling"""
    
    def __init__(self):
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password")
        self._driver = GraphDatabase.driver(uri, auth=(user, password))
    
    # --- FIX: This is now a regular function, not an async one ---
    def close(self):
        """Closes the database driver connection."""
        if self._driver:
            self._driver.close()
            
    async def store_analysis_results(self, domain: str, results: Dict):
        """Store anomaly detection results"""
        async with self._driver.session() as session:
            for anomaly in results.get('anomalies', []):
                timestamp_str = anomaly['timestamp'].isoformat()
                unique_id = str(uuid.uuid4())
                
                await session.run(
                    """
                    MERGE (a:Anomaly {id: $anomaly_id, domain: $domain})
                    SET a.score = $score,
                        a.risk_level = $risk_level,
                        a.detected_at = $timestamp,
                        a.explanation = $explanation,
                        a.entities = $entities
                    """,
                    anomaly_id=unique_id,
                    domain=domain,
                    score=anomaly['score'],
                    risk_level=anomaly['risk_level'],
                    timestamp=timestamp_str,
                    explanation=str(anomaly['explanation']),
                    entities=anomaly.get('entities', [])
                )