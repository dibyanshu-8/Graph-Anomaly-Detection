# src/api/models.py

from pydantic import BaseModel
from typing import List, Dict, Optional

# Pydantic models for request and response validation
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