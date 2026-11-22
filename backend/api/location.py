from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.models.entities import Complaint
from backend.services.location_service import location_service
from backend.schemas.dashboard import MapMarker

router = APIRouter(prefix="/api/location", tags=["Location & Maps"])

@router.get("/geocode")
def geocode_address(query: str = Query(..., min_length=2)):
    lat, lon, formatted_address = location_service.geocode(query)
    return {
        "query": query,
        "latitude": lat,
        "longitude": lon,
        "formatted_address": formatted_address
    }

@router.get("/markers", response_model=List[MapMarker])
def get_map_markers(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Complaint).filter(Complaint.latitude.isnot(None), Complaint.longitude.isnot(None))
    if status:
        query = query.filter(Complaint.status == status)
    if priority:
        query = query.filter(Complaint.priority == priority)
    if category:
        query = query.filter(Complaint.category == category)

    complaints = query.all()
    markers = [
        MapMarker(
            id=c.id,
            category=c.category,
            department_id=c.department_id,
            priority=c.priority,
            status=c.status,
            latitude=c.latitude,
            longitude=c.longitude,
            location_text=c.location_text,
            cluster_id=c.cluster_id
        )
        for c in complaints
    ]
    return markers
