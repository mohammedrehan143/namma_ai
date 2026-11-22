from backend.core.database import engine, Base, SessionLocal
from backend.models.entities import Department, ComplaintCategory, SLARule, User
from backend.core.logging import logger

def init_database():
    """Initializes tables and pre-populates master data."""
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if departments exist
        if db.query(Department).count() == 0:
            logger.info("Seeding default civic departments...")
            departments = [
                Department(id="ROADS", name="Road Maintenance & Infrastructure", description="Potholes, asphalt damage, road cave-ins, footpaths", default_sla_hours=24),
                Department(id="SANITATION", name="Solid Waste Management", description="Garbage dumps, debris, uncollected waste", default_sla_hours=12),
                Department(id="DRAINAGE", name="Stormwater & Drain Department", description="Blocked drains, open manholes, stormwater flooding", default_sla_hours=12),
                Department(id="WATER", name="Water Supply & Pipeline Maintenance", description="Pipe bursts, contaminated water, leakage", default_sla_hours=18),
                Department(id="ELECTRICAL", name="Street Lighting & Power Grid", description="Broken streetlights, hanging wires, electrical hazards", default_sla_hours=24),
                Department(id="PUBLIC_WORKS", name="Public Works & Parks", description="Fallen trees, broken fences, public property damage", default_sla_hours=48),
            ]
            db.add_all(departments)
            db.commit()

            logger.info("Seeding default SLA rules...")
            sla_rules = []
            for dept in departments:
                sla_rules.extend([
                    SLARule(department_id=dept.id, priority="CRITICAL", max_resolution_hours=4, warning_threshold_hours=2),
                    SLARule(department_id=dept.id, priority="HIGH", max_resolution_hours=24, warning_threshold_hours=18),
                    SLARule(department_id=dept.id, priority="MEDIUM", max_resolution_hours=48, warning_threshold_hours=36),
                    SLARule(department_id=dept.id, priority="LOW", max_resolution_hours=72, warning_threshold_hours=60),
                ])
            db.add_all(sla_rules)
            db.commit()

            logger.info("Seeding default complaint categories...")
            categories = [
                ComplaintCategory(id="ROAD_DAMAGE", name="Road Damage & Potholes", description="Potholes, cracked asphalt, road cave-ins", department_id="ROADS", default_priority="HIGH"),
                ComplaintCategory(id="GARBAGE", name="Garbage & Waste Accumulation", description="Overflowing bins, illegal garbage dumping", department_id="SANITATION", default_priority="MEDIUM"),
                ComplaintCategory(id="DRAINAGE", name="Stormwater Drainage & Manholes", description="Blocked storm drains, open hazardous manholes", department_id="DRAINAGE", default_priority="HIGH"),
                ComplaintCategory(id="SEWAGE", name="Sewage Leakage & Overflow", description="Sewage line leaks, foul odor, wastewater puddles", department_id="DRAINAGE", default_priority="HIGH"),
                ComplaintCategory(id="WATER_LEAK", name="Water Pipeline Leakage", description="Fresh water pipeline bursts, supply disruptions", department_id="WATER", default_priority="MEDIUM"),
                ComplaintCategory(id="STREETLIGHT", name="Street Lighting", description="Broken streetlights, unlit stretches, wire issues", department_id="ELECTRICAL", default_priority="LOW"),
                ComplaintCategory(id="PUBLIC_INFRA", name="Public Infrastructure & Trees", description="Fallen tree branches, damaged footpaths", department_id="PUBLIC_WORKS", default_priority="LOW"),
                ComplaintCategory(id="OTHER", name="General Civic Issues", description="Other municipal and civic grievances", department_id="PUBLIC_WORKS", default_priority="LOW"),
            ]
            db.add_all(categories)
            db.commit()

        # Seed default test officer and supervisor
        if db.query(User).filter(User.phone == "+919876543210").first() is None:
            demo_users = [
                User(id="usr-officer-roads", name="Officer Vikram Sharma", phone="+919876543210", email="vikram.roads@namma.gov.in", role="OFFICER", department_id="ROADS"),
                User(id="usr-supervisor", name="Supervisor Ananya Rao", phone="+919876543211", email="ananya.sup@namma.gov.in", role="SUPERVISOR", department_id="ROADS"),
                User(id="usr-admin", name="Admin Control", phone="+919876543212", email="admin@namma.gov.in", role="ADMIN"),
            ]
            db.add_all(demo_users)
            db.commit()
            logger.info("Default staff seeded successfully.")

    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
