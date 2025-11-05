# src/core/graph_engine.py

import networkx as nx
from typing import Dict, List, Any
from abc import ABC, abstractmethod
import logging
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class AnomalyResult:
    entities: List[str]
    score: float
    risk_level: str
    explanation: Dict[str, Any]
    timestamp: datetime

class BaseGraphEngine(ABC):
    """Abstract base for domain-specific graph processing"""
    @abstractmethod
    def build_graph(self, data: List[Dict]) -> nx.DiGraph:
        pass

    @abstractmethod
    def extract_features(self, graph: nx.DiGraph) -> Dict[str, Any]:
        """This is the required abstract method."""
        pass

class UniversalGraphEngine(BaseGraphEngine):
    """Domain-agnostic graph engine with incremental updates"""
    def __init__(self, domain_config: Dict):
        self.domain = domain_config
        self.time_decay_factor = domain_config.get('time_decay', 0.1)

    def build_graph(self, data: List[Dict]) -> nx.DiGraph:
        """Builds weighted directed graph with domain-specific weights"""
        G = nx.DiGraph()

        for item in data:
            source = item[self.domain['source_field']]
            target = item[self.domain['target_field']]
            weight = self._calculate_weight(item)
            
            edge_data = {
                'weight': weight,
                'timestamp': item.get('timestamp', datetime.now()),
                'raw_data': item
            }
            if G.has_edge(source, target):
                existing = G[source][target]
                existing['weight'] += weight
                existing['count'] = existing.get('count', 1) + 1
            else:
                edge_data['count'] = 1
                G.add_edge(source, target, **edge_data)

        self._add_node_features(G)
        return G

    
    def extract_features(self, graph: nx.DiGraph) -> Dict[str, Any]:
        """
        Extracts high-level features from the entire graph.
        This fulfills the contract from BaseGraphEngine.
        """
        if not graph:
            return {}
            
        return {
            "node_count": graph.number_of_nodes(),
            "edge_count": graph.number_of_edges(),
            "density": nx.density(graph),
            "avg_clustering": nx.average_clustering(graph.to_undirected()),
            "connected_components": nx.number_weakly_connected_components(graph)
        }
    

    def _calculate_weight(self, item: Dict) -> float:
        """Domain-specific weight calculation"""
        base_weight = item.get(self.domain.get('weight_field', 'amount'), 1.0)
        return float(base_weight)

    def _add_node_features(self, G: nx.DiGraph):
        """Compute node-level features for anomaly detection"""
        if G.number_of_nodes() == 0:
            return
            
        pagerank = nx.pagerank(G, alpha=0.85)
        for node in G.nodes:
            # Clustering needs an undirected graph view
            clustering_graph = G.to_undirected()
            node_data = {
                'in_degree': G.in_degree(node),
                'out_degree': G.out_degree(node),
                'clustering': nx.clustering(clustering_graph, node),
                'page_rank': pagerank.get(node, 0)
            }
            G.nodes[node].update(node_data)

    def incremental_update(self, G: nx.DiGraph, new_data: List[Dict]) -> nx.DiGraph:
        """Incrementally update graph without a full rebuild"""
        logger.info(f"Incremental update with {len(new_data)} new records")
        for item in new_data:
            source = item[self.domain['source_field']]
            target = item[self.domain['target_field']]
            weight = self._calculate_weight(item)
            
            if not G.has_edge(source, target):
                G.add_edge(source, target, weight=weight, count=1, raw_data=[item])
            else:
                G[source][target]['weight'] += weight
                G[source][target]['count'] += 1
                if 'raw_data' not in G[source][target]:
                    G[source][target]['raw_data'] = []
                G[source][target]['raw_data'].append(item)
            
            self._update_node_features(G, source, target)
        return G

    def _update_node_features(self, G: nx.DiGraph, source: str, target: str):
        """Efficiently update node features after an edge addition"""
        pagerank = nx.pagerank(G, alpha=0.85) # Recompute pagerank for affected area
        for node in [source, target]:
            if node in G:
                G.nodes[node]['in_degree'] = G.in_degree(node)
                G.nodes[node]['out_degree'] = G.out_degree(node)
                G.nodes[node]['page_rank'] = pagerank.get(node, 0)