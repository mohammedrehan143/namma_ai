from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.core.database import get_db
from backend.models.entities import IncidentCluster, Complaint
from backend.schemas.cluster import IncidentClusterResponse

router = APIRouter(prefix="/api/clusters", tags=["Incident Clusters"])

@router.get("", response_model=List[IncidentClusterResponse])
def list_incident_clusters(
    status: Optional[str] = Query("ACTIVE"),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(IncidentCluster)
    if status:
        query = query.filter(IncidentCluster.status == status)
    if category:
        query = query.filter(IncidentCluster.category == category)

    clusters = query.order_by(desc(IncidentCluster.report_count)).all()
    results = []
    for cl in clusters:
        complaint_ids = [c.id for c in cl.complaints]
        results.append(
            IncidentClusterResponse(
                id=cl.id,
                title=cl.title,
                category=cl.category,
                center_latitude=cl.center_latitude,
                center_longitude=cl.center_longitude,
                status=cl.status,
                report_count=cl.report_count,
                first_reported_at=cl.first_reported_at,
                last_reported_at=cl.last_reported_at,
                complaint_ids=complaint_ids
            )
        )
    return results

@router.get("/{cluster_id}", response_model=dict)
def get_incident_cluster_detail(cluster_id: str, db: Session = Depends(get_db)):
    cluster = db.query(IncidentCluster).filter(IncidentCluster.id == cluster_id).first()
    if not cluster:
        raise HTTPException(status_code=404, detail="Incident cluster not found")

    complaints_data = [
        {
            "id": c.id,
            "status": c.status,
            "priority": c.priority,
            "raw_description": c.raw_description,
            "location_text": c.location_text,
            "latitude": c.latitude,
            "longitude": c.longitude,
            "citizen_name": c.citizen.name if c.citizen else None,
            "citizen_phone": c.citizen.phone if c.citizen else None,
            "created_at": c.created_at
        }
        for c in cluster.complaints
    ]

    return {
        "id": cluster.id,
        "title": cluster.title,
        "category": cluster.category,
        "status": cluster.status,
        "report_count": cluster.report_count,
        "center_latitude": cluster.center_latitude,
        "center_longitude": cluster.center_longitude,
        "first_reported_at": cluster.first_reported_at,
        "last_reported_at": cluster.last_reported_at,
        "affected_citizens_count": cluster.report_count,
        "complaints": complaints_data
    }
