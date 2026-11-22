from datetime import datetime, timezone, timedelta
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from backend.models.entities import Complaint, IncidentCluster
from backend.services.location_service import location_service
from backend.core.logging import logger

def text_similarity(t1: str, t2: str) -> float:
    """Calculates word-token Jaccard semantic similarity between two descriptions."""
    words1 = set(t1.lower().split())
    words2 = set(t2.lower().split())
    if not words1 or not words2:
        return 0.0
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    return len(intersection) / len(union)

class ClusteringService:
    def check_and_cluster(
        self,
        db: Session,
        new_complaint: Complaint,
        proximity_meters: float = 350.0,
        hours_window: int = 72
    ) -> Optional[IncidentCluster]:
        """Detects whether a newly registered complaint is a duplicate/part of an active incident cluster."""
        if not new_complaint.latitude or not new_complaint.longitude:
            return None

        now = datetime.now(timezone.utc)
        since_time = now - timedelta(hours=hours_window)

        # 1. First, check existing active clusters in the same category
        active_clusters = db.query(IncidentCluster).filter(
            IncidentCluster.category == new_complaint.category,
            IncidentCluster.status == "ACTIVE"
        ).all()

        for cluster in active_clusters:
            dist = location_service.haversine_distance_meters(
                new_complaint.latitude, new_complaint.longitude,
                cluster.center_latitude, cluster.center_longitude
            )
            if dist <= proximity_meters:
                logger.info(f"Complaint {new_complaint.id} matched existing cluster {cluster.id} (Distance: {dist:.1f}m)")
                cluster.report_count += 1
                cluster.last_reported_at = now
                new_complaint.cluster_id = cluster.id

                # Escalate priority when multiple citizens report
                if cluster.report_count >= 3:
                    new_complaint.priority = "CRITICAL"
                    new_complaint.priority_score = min(100, new_complaint.priority_score + 15)

                db.commit()
                db.refresh(cluster)
                return cluster

        # 2. Check candidate individual complaints within proximity and time window
        candidates = db.query(Complaint).filter(
            Complaint.id != new_complaint.id,
            Complaint.category == new_complaint.category,
            Complaint.created_at >= since_time,
            Complaint.latitude.isnot(None),
            Complaint.longitude.isnot(None)
        ).all()

        for candidate in candidates:
            dist = location_service.haversine_distance_meters(
                new_complaint.latitude, new_complaint.longitude,
                candidate.latitude, candidate.longitude
            )
            sim = text_similarity(new_complaint.raw_description, candidate.raw_description)

            # Match condition: close proximity (<300m) or high semantic text overlap (>0.40) within 500m
            if dist <= proximity_meters or (dist <= 500.0 and sim >= 0.35):
                logger.info(f"Duplicate detected between {new_complaint.id} and {candidate.id} (dist: {dist:.1f}m, sim: {sim:.2f})")

                # If candidate is already in a cluster, join it
                if candidate.cluster_id:
                    cluster = db.query(IncidentCluster).filter(IncidentCluster.id == candidate.cluster_id).first()
                    if cluster:
                        cluster.report_count += 1
                        cluster.last_reported_at = now
                        new_complaint.cluster_id = cluster.id
                        db.commit()
                        db.refresh(cluster)
                        return cluster

                # Otherwise, form a NEW incident cluster
                cluster_count = db.query(IncidentCluster).count()
                candidate_cluster_num = 100 + cluster_count + 1
                cluster_id = f"INC-{candidate_cluster_num}"
                while db.query(IncidentCluster).filter(IncidentCluster.id == cluster_id).first() is not None:
                    candidate_cluster_num += 1
                    cluster_id = f"INC-{candidate_cluster_num}"
                
                title = f"{new_complaint.category.replace('_', ' ').title()} near {new_complaint.landmark or new_complaint.location_text or 'Location'}"
                new_cluster = IncidentCluster(
                    id=cluster_id,
                    title=title,
                    category=new_complaint.category,
                    center_latitude=(new_complaint.latitude + candidate.latitude) / 2.0,
                    center_longitude=(new_complaint.longitude + candidate.longitude) / 2.0,
                    status="ACTIVE",
                    report_count=2,
                    first_reported_at=candidate.created_at,
                    last_reported_at=now
                )
                db.add(new_cluster)
                db.flush()

                # Link both complaints
                candidate.cluster_id = new_cluster.id
                new_complaint.cluster_id = new_cluster.id
                
                # Boost priority
                new_complaint.priority = "HIGH"
                new_complaint.priority_score = min(100, new_complaint.priority_score + 10)
                candidate.priority = "HIGH"
                candidate.priority_score = min(100, candidate.priority_score + 10)

                db.commit()
                db.refresh(new_cluster)
                logger.info(f"Formed new incident cluster {new_cluster.id} grouping {candidate.id} and {new_complaint.id}")
                return new_cluster

        return None

clustering_service = ClusteringService()
