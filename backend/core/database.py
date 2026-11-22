from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.core.config import settings
from backend.core.logging import logger

# Normalize Supabase/PostgreSQL connection string if using postgres:// prefix
db_url = settings.DATABASE_URL
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

# Gracefully fallback to local SQLite if placeholders have not yet been replaced with real credentials
if "[YOUR-PASSWORD]" in db_url or "[YOUR-PROJECT-REF]" in db_url or "your-project" in db_url:
    logger.warning("Supabase placeholder detected in DATABASE_URL. Falling back to local SQLite until real credentials are saved in .env.")
    db_url = "sqlite:///./namma_ai.db"

# SQLite or PostgreSQL/Supabase configuration
connect_args = {}
engine_kwargs = {
    "pool_pre_ping": True
}

if db_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False
else:
    # Supabase / PostgreSQL cloud pooling parameters
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20
    engine_kwargs["pool_recycle"] = 300

engine = create_engine(
    db_url,
    connect_args=connect_args,
    **engine_kwargs
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_db_connection() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return False
