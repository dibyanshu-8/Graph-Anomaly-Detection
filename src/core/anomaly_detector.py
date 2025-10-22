# src/core/anomaly_detector.py

import networkx as nx
from typing import Dict, List
import numpy as np
from sklearn.ensemble import IsolationForest
from datetime import datetime
import logging

from .graph_engine import AnomalyResult

logger = logging.getLogger(__name__)

class AdvancedAnomalyDetector:
    """Multi-signal anomaly detection with explainability"""
    
    def __init__(self, domain_config: Dict):
        self.domain = domain_config
        self.min_ring_size = domain_config.get('min_ring_size', 3)
        self.centrality_threshold = domain_config.get('centrality_threshold', 0.05)
        
        self.isolation_forest = IsolationForest(contamination=0.1, random_state=42)
    
    def detect_anomalies(self, G: nx.DiGraph) -> List[AnomalyResult]:
        """Comprehensive anomaly detection pipeline"""
        if G.number_of_nodes() == 0:
            return []

        results = []
        
        rings = self._detect_rings(G)
        individual_anomalies = self._detect_individual_anomalies(G)
        
        combined_results = self._combine_signals(rings, individual_anomalies)
        
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

    # --- THIS IS THE NEW, REQUIRED METHOD ---
    def _extract_node_features(self, G: nx.DiGraph) -> Dict[str, List[float]]:
        """
        Extracts features from each node into a dictionary for the ML model.
        This was the missing method causing the 500 error.
        """
        features = {}
        for node, data in G.nodes(data=True):
            features[node] = [
                data.get('in_degree', 0),
                data.get('out_degree', 0),
                data.get('clustering', 0),
                data.get('page_rank', 0)
            ]
        return features
    # ----------------------------------------

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
        total_weight = sum(d.get('weight', 0) for _, _, d in subgraph.edges(data=True))
        density = nx.density(subgraph)
        
        suspicious_score = (density * 0.5) + (min(np.log1p(total_weight) / 10, 1.0) * 0.5)

        return {
            'total_weight': total_weight,
            'density': density,
            'suspicious_score': suspicious_score
        }

    def _detect_individual_anomalies(self, G: nx.DiGraph) -> Dict:
        """Multi-signal individual anomaly detection"""
        anomalies = {}
        
        node_features = self._extract_node_features(G)
        
        # Only run ML model if there's enough data to be meaningful
        if len(node_features) > 10:
            feature_matrix = np.array(list(node_features.values()))
            ml_scores = self.isolation_forest.fit_predict(feature_matrix)
            
            # Additional logic for ML-based anomalies would go here...

        # For now, let's just use centrality for small graphs
        betweenness = nx.betweenness_centrality(G, weight='weight')
        for node, score in betweenness.items():
            if score > self.centrality_threshold:
                anomalies[node] = {
                    'type': 'individual',
                    'entities': [node],
                    'score': score * 5, # Scale score to be comparable
                    'centrality_score': score,
                }
        return anomalies

    def _combine_signals(self, rings: List, individual_anomalies: Dict) -> List[Dict]:
        """Combines ring and individual anomaly signals."""
        # Simple combination for now, just return rings
        # A more advanced system could merge entities found in both
        return rings + list(individual_anomalies.values())
    
    def _generate_explanation(self, result: Dict, G: nx.DiGraph) -> Dict:
        """Explainable decisions for regulatory compliance"""
        explanation = { 'detection_method': result.get('type', 'unknown') }
        if result.get('type') == 'ring':
            explanation['summary'] = f"Coordinated activity in a ring of {len(result['entities'])}."
        else:
            explanation['summary'] = f"High centrality score of {result.get('centrality_score', 0):.3f} indicates a key broker role."
        return explanation

    def _classify_risk(self, score: float) -> str:
        if score > 0.9: return "CRITICAL"
        elif score > 0.7: return "HIGH"
        elif score > 0.5: return "MEDIUM"
        else: return "LOW"