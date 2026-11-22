from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

class IncidentClusterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    category: str
    center_latitude: float
    center_longitude: float
    status: str
    report_count: int
    first_reported_at: datetime
    last_reported_at: datetime
    complaint_ids: List[str] = []
