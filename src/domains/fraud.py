from typing import Dict, List, Any
from ..core.graph_engine import UniversalGraphEngine
from ..core.anomaly_detector import AdvancedAnomalyDetector

class FraudDomainProcessor:
    """Banking fraud detection with UPI-specific patterns"""
    
    DOMAIN_CONFIG = {
        'name': 'fraud',
        'source_field': 'sender',
        'target_field': 'receiver',
        'weight_field': 'amount',
        'min_ring_size': 3,
        'centrality_threshold': 0.05,
        'upi_patterns': True  # India-specific
    }
    
    def __init__(self):
        self.engine = UniversalGraphEngine(self.DOMAIN_CONFIG)
        self.detector = AdvancedAnomalyDetector(self.DOMAIN_CONFIG)
    
    def process_transactions(self, transactions: List[Dict]) -> Dict:
        """Process banking transactions with fraud-specific logic"""
        # Preprocess UPI-specific patterns
        processed_data = self._preprocess_upi_patterns(transactions)
        
        # Build or update graph incrementally
        G = self.engine.build_graph(processed_data)
        
        # Detect anomalies
        anomalies = self.detector.detect_anomalies(G)
        
        # UPI-specific analysis
        upi_anomalies = self._detect_upi_fraud_patterns(transactions)
        
        return {
            'anomalies': [a.__dict__ for a in anomalies],
            'upi_alerts': upi_anomalies,
            'summary': self._generate_fraud_summary(anomalies)
        }
    
    def _preprocess_upi_patterns(self, transactions: List[Dict]) -> List[Dict]:
        """India-specific UPI fraud preprocessing"""
        processed = []
        for tx in transactions:
            # Detect UPI handle rotation (common fraud)
            if 'upi_handle' in tx:
                tx['handle_stability'] = self._calculate_handle_stability(tx)
            
            # Festival fraud spike detection
            tx['is_festival_period'] = self._is_festival_period(tx['timestamp'])
            
            processed.append(tx)
        return processed
    
    def _detect_upi_fraud_patterns(self, transactions: List[Dict]) -> List[Dict]:
        """UNIQUE FEATURE: UPI-specific fraud patterns"""
        alerts = []
        
        # Handle recycling detection
        handle_usage = {}
        for tx in transactions:
            handle = tx.get('upi_handle')
            if handle:
                handle_usage[handle] = handle_usage.get(handle, 0) + 1
        
        for handle, count in handle_usage.items():
            if count > 50:  # Suspicious handle reuse
                alerts.append({
                    'type': 'handle_recycling',
                    'handle': handle,
                    'transaction_count': count,
                    'risk': 'HIGH'
                })
        
        return alerts