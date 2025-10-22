from neo4j import GraphDatabase
from typing import List, Dict, Any
import asyncio
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
load_dotenv()  # Add at top of files
uri = os.getenv('NEO4J_URI')
# etc.
class Neo4jRepository:
    """Production Neo4j integration with connection pooling"""
    
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="password"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    async def store_transaction(self, domain: str, transaction: Dict):
        """Store transaction as graph nodes/edges"""
        async with self.driver.session() as session:
            await session.run(
                """
                MERGE (a:Entity {id: $sender, domain: $domain})
                MERGE (b:Entity {id: $receiver, domain: $domain})
                MERGE (a)-[t:TRANSACTION {
                    domain: $domain,
                    amount: $amount,
                    timestamp: $timestamp,
                    weight: $weight
                }]->(b)
                """,
                domain=domain,
                sender=transaction['sender'],
                receiver=transaction['receiver'],
                amount=transaction.get('amount', 0),
                timestamp=transaction.get('timestamp'),
                weight=transaction.get('weight', 1.0)
            )
    
    async def store_analysis_results(self, domain: str, results: Dict):
        """Store anomaly detection results"""
        async with self.driver.session() as session:
            for anomaly in results.get('anomalies', []):
                await session.run(
                    """
                    MERGE (a:Anomaly {id: $anomaly_id, domain: $domain})
                    SET a.score = $score,
                        a.risk_level = $risk_level,
                        a.detected_at = $timestamp,
                        a.explanation = $explanation
                    """,
                    anomaly_id=f"{domain}_{anomaly['entities'][0]}_{results['timestamp']}",
                    domain=domain,
                    score=anomaly['score'],
                    risk_level=anomaly['risk_level'],
                    timestamp=results['timestamp'],
                    explanation=str(anomaly['explanation'])
                )
    
    async def query_historical_anomalies(self, domain: str, limit: int = 100):
        """Query historical anomalies for analysis"""
        async with self.driver.session() as session:
            result = await session.run(
                """
                MATCH (a:Anomaly {domain: $domain})
                RETURN a.id, a.score, a.risk_level, a.detected_at, a.explanation
                ORDER BY a.detected_at DESC
                LIMIT $limit
                """,
                domain=domain, limit=limit
            )
            return await result.data()
    
    async def close(self):
        await self.driver.close()

@asynccontextmanager
async def get_neo4j_session(driver):
    """Context manager for Neo4j sessions"""
    async with driver.session() as session:
        yield session