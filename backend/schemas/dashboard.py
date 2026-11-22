from typing import List, Optional
from pydantic import BaseModel

class DashboardStats(BaseModel):
    total: int
    open: int
    in_progress: int
    resolved: int
    reopened: int
    critical: int
    high: int
    medium: int
    low: int
    sla_breached: int

class MapMarker(BaseModel):
    id: str
    category: str
    department_id: Optional[str] = None
    priority: str
    status: str
    latitude: float
    longitude: float
    location_text: Optional[str] = None
    cluster_id: Optional[str] = None
