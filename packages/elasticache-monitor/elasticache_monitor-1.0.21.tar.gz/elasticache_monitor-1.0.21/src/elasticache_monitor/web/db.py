"""Database connection and session management for web UI.

Architecture:
- Main DB (elasticache_monitor.db): Job metadata only (MonitorJob, MonitorShard)
- Per-job DB (data/jobs/{job_id}.db): Commands for each job (RedisCommand, KeySizeCache)
"""

from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator
import os
import logging
import shutil

from .models import MetadataBase, CommandBase

logger = logging.getLogger("elasticache-monitor-web")

# ============================================================================
# PATHS
# ============================================================================

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# Main metadata database (with backward compatibility)
OLD_METADATA_DB_PATH = PROJECT_ROOT / "redis_monitor.db"
METADATA_DB_PATH = PROJECT_ROOT / "elasticache_monitor.db"

# Migrate old DB to new name if exists
if OLD_METADATA_DB_PATH.exists() and not METADATA_DB_PATH.exists():
    shutil.move(str(OLD_METADATA_DB_PATH), str(METADATA_DB_PATH))
    logger.info(f"Migrated database: {OLD_METADATA_DB_PATH} -> {METADATA_DB_PATH}")

METADATA_DATABASE_URL = f"sqlite:///{METADATA_DB_PATH}"

# Per-job databases directory
JOBS_DATA_DIR = PROJECT_ROOT / "data" / "jobs"


def get_job_db_path(job_id: str) -> Path:
    """Get path to job-specific database file."""
    return JOBS_DATA_DIR / f"{job_id}.db"


def get_job_db_url(job_id: str) -> str:
    """Get SQLite URL for job-specific database."""
    return f"sqlite:///{get_job_db_path(job_id)}"


# ============================================================================
# METADATA DATABASE (jobs, shards)
# ============================================================================

# Create engine for metadata DB
metadata_engine = create_engine(
    METADATA_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)

# Session factory for metadata
MetadataSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=metadata_engine)


def _migrate_metadata_db_schema() -> None:
    """Add any missing columns to the metadata database.
    
    This handles schema migrations for databases created before new columns were added.
    Called automatically at module load time to ensure columns exist before any queries.
    """
    new_columns_shards = [
        # Redis server info
        ("redis_version", "TEXT"),
        # Memory info
        ("memory_used_bytes", "INTEGER"),
        ("memory_max_bytes", "INTEGER"),
        ("memory_peak_bytes", "INTEGER"),
        ("memory_rss_bytes", "INTEGER"),
        # CPU info
        ("cpu_sys_start", "REAL"),
        ("cpu_user_start", "REAL"),
        ("cpu_sys_end", "REAL"),
        ("cpu_user_end", "REAL"),
        ("cpu_sys_delta", "REAL"),
        ("cpu_user_delta", "REAL"),
        # AWS CloudWatch metrics
        ("aws_engine_cpu_max", "REAL"),
    ]
    
    try:
        with metadata_engine.connect() as conn:
            # Check if table exists
            result = conn.execute(text(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='monitor_shards'"
            ))
            if not result.fetchone():
                return  # Table doesn't exist yet
            
            # Get existing columns
            result = conn.execute(text("PRAGMA table_info(monitor_shards)"))
            existing_columns = {row[1] for row in result.fetchall()}
            
            # Add missing columns
            for col_name, col_def in new_columns_shards:
                if col_name not in existing_columns:
                    try:
                        conn.execute(text(f"ALTER TABLE monitor_shards ADD COLUMN {col_name} {col_def}"))
                        logger.info(f"Added column {col_name} to monitor_shards table")
                    except Exception as e:
                        logger.debug(f"Could not add column {col_name}: {e}")
            
            conn.commit()
    except Exception as e:
        logger.debug(f"Could not migrate metadata schema: {e}")


def _ensure_short_urls_table() -> None:
    """Ensure the short_urls table exists for URL sharing feature."""
    try:
        with metadata_engine.connect() as conn:
            # Check if table exists
            result = conn.execute(text(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='short_urls'"
            ))
            if not result.fetchone():
                # Create the table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS short_urls (
                        id TEXT PRIMARY KEY,
                        full_url TEXT NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        hit_count INTEGER DEFAULT 0
                    )
                """))
                # Create index on full_url for deduplication lookups
                conn.execute(text(
                    "CREATE INDEX IF NOT EXISTS ix_short_urls_full_url ON short_urls(full_url)"
                ))
                conn.commit()
                logger.info("Created short_urls table for URL sharing")
    except Exception as e:
        logger.debug(f"Could not create short_urls table: {e}")


# Run migration immediately at module load time
# This ensures columns exist before any ORM queries
_migrate_metadata_db_schema()
_ensure_short_urls_table()


def init_metadata_db() -> None:
    """Initialize metadata database and create tables."""
    MetadataBase.metadata.create_all(bind=metadata_engine)
    # Migration already ran at module load, but run again to be safe
    _migrate_metadata_db_schema()
    _ensure_short_urls_table()


def get_db() -> Generator[Session, None, None]:
    """Dependency for getting metadata database session."""
    db = MetadataSessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """Context manager for metadata database session (for background tasks)."""
    db = MetadataSessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# ============================================================================
# JOB-SPECIFIC DATABASES (commands)
# ============================================================================

# Cache of job engines to avoid recreating them
_job_engines = {}
_job_sessions = {}


def get_job_engine(job_id: str):
    """Get or create SQLAlchemy engine for a job's database."""
    if job_id not in _job_engines:
        # Ensure directory exists
        JOBS_DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        # Check if DB already exists (for migration)
        db_existed = get_job_db_path(job_id).exists()
        
        db_url = get_job_db_url(job_id)
        engine = create_engine(
            db_url,
            connect_args={"check_same_thread": False},
            echo=False
        )
        _job_engines[job_id] = engine
        
        # Run migration on existing databases to add new columns
        if db_existed:
            _migrate_job_db_schema(engine, job_id)
    
    return _job_engines[job_id]


def _migrate_job_db_schema(engine, job_id: str) -> None:
    """Add any missing columns to an existing job database.
    
    This handles schema migrations for databases created before new columns were added.
    SQLite supports ALTER TABLE ... ADD COLUMN for adding new nullable columns.
    
    Note: This is called internally by get_job_engine, not directly.
    """
    # Define columns that may be missing in older databases
    # Format: (column_name, column_definition)
    new_columns = [
        ("arg_shape", "TEXT"),
        ("command_signature", "TEXT"),
        ("is_full_scan", "INTEGER DEFAULT 0"),
        ("is_lock_op", "INTEGER DEFAULT 0"),
    ]
    
    with engine.connect() as conn:
        # Check if table exists first
        result = conn.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='redis_commands'"
        ))
        if not result.fetchone():
            return  # Table doesn't exist yet, nothing to migrate
        
        # Get existing columns
        result = conn.execute(text("PRAGMA table_info(redis_commands)"))
        existing_columns = {row[1] for row in result.fetchall()}
        
        # Add missing columns
        for col_name, col_def in new_columns:
            if col_name not in existing_columns:
                try:
                    conn.execute(text(f"ALTER TABLE redis_commands ADD COLUMN {col_name} {col_def}"))
                    logger.info(f"Added column {col_name} to job {job_id} database")
                except Exception as e:
                    # Column might already exist (race condition) or other issue
                    logger.debug(f"Could not add column {col_name}: {e}")
        
        conn.commit()


def init_job_db(job_id: str) -> None:
    """Initialize a job-specific database and create tables."""
    engine = get_job_engine(job_id)
    CommandBase.metadata.create_all(bind=engine)


def get_job_session_factory(job_id: str):
    """Get session factory for a job's database."""
    if job_id not in _job_sessions:
        engine = get_job_engine(job_id)
        _job_sessions[job_id] = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return _job_sessions[job_id]


@contextmanager
def get_job_db_context(job_id: str) -> Generator[Session, None, None]:
    """Context manager for job-specific database session."""
    SessionLocal = get_job_session_factory(job_id)
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def delete_job_db(job_id: str) -> bool:
    """Delete a job's database file and cleanup cached connections."""
    # Close and remove cached engine/session
    if job_id in _job_engines:
        _job_engines[job_id].dispose()
        del _job_engines[job_id]
    if job_id in _job_sessions:
        del _job_sessions[job_id]
    
    # Delete the file
    db_path = get_job_db_path(job_id)
    if db_path.exists():
        os.remove(db_path)
        return True
    return False


def job_db_exists(job_id: str) -> bool:
    """Check if a job's database file exists."""
    return get_job_db_path(job_id).exists()


# ============================================================================
# INITIALIZATION
# ============================================================================

def init_db() -> None:
    """Initialize all databases (just metadata on startup)."""
    JOBS_DATA_DIR.mkdir(parents=True, exist_ok=True)
    init_metadata_db()
