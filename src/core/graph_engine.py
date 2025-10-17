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
    
