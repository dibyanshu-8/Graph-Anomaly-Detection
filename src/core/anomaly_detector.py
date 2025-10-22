import networkx as nx 
from typing import Dict,List,Any
from scipy import stats
from sklearn.ensemble import IsolationForest
import numpy as np
from .graph_engine import AnomalyResult
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
class AdvancedAnomalyDetector:
    """Multi signal anomaly detection"""
    def __init__(self,domain_config:Dict):
        self.domain=domain_config
        self.min_ring_size=domain_config.get("min_ring_size",3)
        self.centrality_threshold=domain_config.get("centrality_threshold",0.05)
        
        #ML model for statistical anomalies
        self.isolation_forest=IsolationForest(contamination=0.1,random_state=42)
        
    def detect_anomalies(self,G:nx.DiGraph)->List[AnomalyResult]:
        """comprehensive anomaly detection pipeline"""
        results=[]
        
        #detect fraud rings(stromgly connected compoents)
        rings=self._detect_rings(G)
        #detect individual anomalies (centrality + statistical)
        individual_anomalies = self._detect_individual_anomalies(G)
        #combine & score
        combined_results=self._combine_signals(rings, individual_anomalies)
        
        for result in combined_results:
            explanation = self._generate_explanation(result, G)
            anomaly_result = AnomalyResult(
                entities=result['entities'],
                score=result['score'],
                risk_level=self._classify_risk(result['score']),
                explanation=explanation,
                timestamp=datetime.now()
            )
            results.append(anomaly_result)
            
        return sorted(results, key=lambda x: x.score, reverse=True)
    
    def _detect_rings(self, G: nx.DiGraph) -> List[Dict]:
        """Find suspicious rings using strongly connected components"""
        try:
            sccs = list(nx.strongly_connected_components(G))
            rings = []
            
            for component in sccs:
                if len(component) >= self.min_ring_size:
                    subgraph = G.subgraph(component)
                    ring_metrics = self._calculate_ring_metrics(subgraph)
                    if ring_metrics['suspicious_score'] > 0.7:
                        rings.append({
                            'entities': list(component),
                            'type': 'ring',
                            'metrics': ring_metrics,
                            'score': ring_metrics['suspicious_score']
                        })
            return rings
        except Exception as e:
            logger.error(f"Ring detection failed: {e}")
            return []
        
    def _calculate_ring_metrics(self, subgraph: nx.DiGraph) -> Dict:
        """Calculate comprehensive ring metrics"""
        total_weight = sum(data.get('weight', 0) for _,_, data in subgraph.edges(data=True))
        density = nx.density(subgraph)
        avg_cycle_length = self._estimate_cycle_length(subgraph)
        
        #composite scoring
        size_score = min(len(subgraph.nodes) / 10, 1.0)
        weight_score = min(np.log(total_weight + 1) / np.log(1e6), 1.0)
        density_score = density
        cycle_score = 1.0 / (avg_cycle_length + 1) # Shorter cycles = more suspicious
        suspicious_score=(size_score*0.25+weight_score*0.35+density_score*0.25+cycle_score*0.15)
        
        return {
            'total_weight': total_weight,
            'density': density,
            'avg_cycle_length': avg_cycle_length,
            'suspicious_score': suspicious_score
        }
        
        
           
            
                        
                    
                
            
