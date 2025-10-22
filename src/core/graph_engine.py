import networkx as nx 
from typing import Dict,List,Any,Optional
from abc import ABC,abstractmethod
import logging
from dataclasses import dataclass
from datetime import datetime

logger=logging.getLogger(__name__)

@dataclass
class AnomalyResult:
    entities:List[str]
    score:float
    risk_level:str
    explanation:Dict[str,Any]
    timestamp:datetime
    
class BaseGraphEngine(ABC):
    """Abstract base for domain-specific graph processing"""
    @abstractmethod
    def build_graph(self,data:List[Dict])->nx.DiGraph:
        pass
    
    @abstractmethod
    def extract_features(self,graph:nx.DiGraph)->Dict[str,Any]:
        pass
    
class UniversalGraphEngine(BaseGraphEngine):
    """Domain-agnostic graph engine with incremental updates"""
    def __init__(self,domain_config:Dict):
        self.domain=domain_config
        self.time_decay_factor=domain_config.get('time_decay',0.1)
        
    def build_graph(self,data:List[Dict])->nx.DiGraph:
        """build weighted directed graph with domain-specific weights"""
        G=nx.DiGraph()
        
        #Add notes & edges based on domain schema
        for item in data:
            source=item[self.domain['source_field']]
            target=item[self.domain['target_field']]
            
            #domain specific weight calculation
            weight=self._calculate_weight(item)
            
            edge_data={
                'weight':weight,
                'timestamp':item.get('timestamp',datetime.now()),
                'raw_data':item
            }
            if G.has_edge(source,target):
                #aggregate multiple edges
                existing=G[source][target]
                existing['weight']+=weight
                existing['count']+=1
            else:
                edge_data['count']=1
                G.add_edge(source,target,**edge_data)
            
        self._add_node_features(G)
        return G
    
    def _calculate_weight(self,item:Dict)->float:
        """domain specific weight calculation"""
        base_weight=item.get(self.domain['weight_field'],1.0)
        
        #time decay for temporal data
        if 'timestamp' in item:
            days_old=(datetime.now()-item['timestamp']).days
            base_weight *= (0.9 ** days_old) #exponential decay
            
        return base_weight
    
    def _add_node_features(self,G:nx.DiGraph):
        """compute node level features for anomaly detection"""
        for node in G.nodes:
            node_data={
                'in_degree':G.in_degree(node),
                'out_degree':G.out_degree(node),
                'clustering':nx.clustering(G,node),
                'page_rank':nx.pagerank(G,alpha=0.85).get(node,0)
                
            }
            G.nodes[node].update(node_data)
            
    def incremental_update(self,G:nx.DiGraph,new_data:List[Dict])->nx.DiGraph:
        """incrementally update graph updates without full rebuild"""
        logger.info(f"Incremental update with {len(new_data)} new records")
        for item in new_data:
            source=item[self.domain['source_field']]
            target=item[self.domain['target_field']]
            weight=self._calculate_weight(item)
            
            #add/update edge incrementally
            if not G.has_edge(source,target):
                G.add_edge(source,target,weight=weight,count=1,raw_data=[item])
            else:
                G[source][target]['weight']+=weight
                G[source][target]['count']+=1
                G[source][target]['raw_data'].append(item)
                
            # update affetced nodes
            self._update_node_features(G,source,target)
        return G
    
    def _update_node_features(self,G:nx.DiGraph,source:str,target:str):
        """efficiently update node features after edge addition"""
        for node in [source,target]:
            if node in G:
                G.nodes[node]['in_degree']=G.in_degree(node)
                G.nodes[node]['out_degree']=G.out_degree(node)
                
                
        
            