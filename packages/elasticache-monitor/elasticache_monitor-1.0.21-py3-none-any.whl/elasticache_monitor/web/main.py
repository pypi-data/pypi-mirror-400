"""FastAPI main application for ElastiCache Hot Shard Debugger."""

import logging
import sys
import uuid
import json
import secrets
import string
from datetime import datetime
from typing import Optional, List

from fastapi import FastAPI, Request, Depends, Form, BackgroundTasks, Query
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, text
from pathlib import Path

from elasticache_monitor import __version__
from .db import init_db, get_db, get_job_db_context, delete_job_db, job_db_exists, get_job_db_path
from .models import MonitorJob, MonitorShard, RedisCommand, KeySizeCache, JobStatus, ShardStatus, ShortUrl
from .runner import run_monitoring_job, sample_key_sizes, cancel_job, is_job_running
from ..endpoints import get_replica_endpoints, get_all_endpoints

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("elasticache-monitor-web")

# Initialize FastAPI app
app = FastAPI(
    title="ElastiCache Hot Shard Debugger",
    description="Debug uneven key distribution and hot shards in ElastiCache Redis/Valkey clusters",
    version=__version__
)

# Setup templates
BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Add version and utility functions to template globals
templates.env.globals["app_version"] = __version__
templates.env.globals["min"] = min
templates.env.globals["max"] = max


# Custom Jinja2 filters
def format_bytes(value, precision=2):
    """Format bytes to human-readable format."""
    if value is None or value == 0:
        return "0 B"
    try:
        value = float(value)
    except (ValueError, TypeError):
        return str(value)
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0
    while abs(value) >= 1024 and unit_index < len(units) - 1:
        value /= 1024
        unit_index += 1
    return f"{value:.{precision}f} {units[unit_index]}"


def format_number(value, precision=1):
    """Format large numbers with K, M, B suffixes."""
    if value is None:
        return "0"
    try:
        value = float(value)
    except (ValueError, TypeError):
        return str(value)
    
    if abs(value) < 1000:
        return f"{int(value)}" if value == int(value) else f"{value:.{precision}f}"
    
    units = ['', 'K', 'M', 'B', 'T']
    unit_index = 0
    while abs(value) >= 1000 and unit_index < len(units) - 1:
        value /= 1000
        unit_index += 1
    return f"{value:.{precision}f}{units[unit_index]}"


def format_duration(seconds):
    """Format seconds to human-readable duration."""
    if seconds is None:
        return "N/A"
    try:
        seconds = int(seconds)
    except (ValueError, TypeError):
        return str(seconds)
    
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins}m {secs}s"
    else:
        hours = seconds // 3600
        mins = (seconds % 3600) // 60
        return f"{hours}h {mins}m"


# Register filters
templates.env.filters["format_bytes"] = format_bytes
templates.env.filters["format_number"] = format_number
templates.env.filters["format_duration"] = format_duration


# Mount static files
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(exist_ok=True)
(STATIC_DIR / "css").mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    logger.info("Starting Redis Hot Shard Debugger Web UI...")
    init_db()
    logger.info("Database initialized")
    logger.info("Web UI ready")


# =============================================================================
# ABOUT PAGE
# =============================================================================

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    """About page with project and author information."""
    return templates.TemplateResponse("about.html", {
        "request": request,
        "page_title": "About",
    })


# =============================================================================
# HOME PAGE
# =============================================================================

@app.get("/", response_class=HTMLResponse)
async def index(request: Request, db: Session = Depends(get_db)):
    """Home page - create new monitoring job."""
    # Get recent jobs for quick reference
    recent_jobs = db.query(MonitorJob).order_by(desc(MonitorJob.created_at)).limit(5).all()
    
    # Get distinct replication group IDs for autocomplete
    prev_replication_groups = db.query(MonitorJob.replication_group_id).distinct().order_by(
        desc(MonitorJob.created_at)
    ).limit(20).all()
    prev_replication_groups = [r[0] for r in prev_replication_groups]
    
    # Get distinct job names for autocomplete
    prev_job_names = db.query(MonitorJob.name).filter(
        MonitorJob.name.isnot(None),
        MonitorJob.name != ''
    ).distinct().order_by(desc(MonitorJob.created_at)).limit(20).all()
    prev_job_names = [r[0] for r in prev_job_names]
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "page_title": "ElastiCache Hot Shard Debugger",
        "recent_jobs": recent_jobs,
        "prev_replication_groups": prev_replication_groups,
        "prev_job_names": prev_job_names
    })


# =============================================================================
# JOB CREATION
# =============================================================================

@app.post("/jobs/create")
async def create_job(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create and start a new monitoring job."""
    form = await request.form()
    
    replication_group_id = form.get("replication_group_id", "").strip()
    password = form.get("password", "").strip()
    endpoint_type = form.get("endpoint_type", "replica")
    duration = int(form.get("duration", 60))
    region = form.get("region", "ap-south-1").strip()
    job_name = form.get("job_name", "").strip() or None
    
    # Validation
    if not replication_group_id:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "page_title": "ElastiCache Hot Shard Debugger",
            "error": "Replication Group ID is required",
            "recent_jobs": db.query(MonitorJob).order_by(desc(MonitorJob.created_at)).limit(5).all()
        })
    
    if not password:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "page_title": "ElastiCache Hot Shard Debugger",
            "error": "Redis/Valkey password is required",
            "recent_jobs": db.query(MonitorJob).order_by(desc(MonitorJob.created_at)).limit(5).all()
        })

    # Validate endpoints before creating job
    try:
        if endpoint_type == "primary":
            endpoints, error_msg = get_all_endpoints(replication_group_id, region, primary_only=True)
        else:
            endpoints, error_msg = get_replica_endpoints(replication_group_id, region)

        if not endpoints:
            return templates.TemplateResponse("index.html", {
                "request": request,
                "page_title": "ElastiCache Hot Shard Debugger",
                "error": error_msg or f"No {endpoint_type} endpoints found for {replication_group_id}",
                "recent_jobs": db.query(MonitorJob).order_by(desc(MonitorJob.created_at)).limit(5).all()
            })

    except Exception as e:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "page_title": "ElastiCache Hot Shard Debugger",
            "error": f"Failed to discover endpoints: {str(e)}",
            "recent_jobs": db.query(MonitorJob).order_by(desc(MonitorJob.created_at)).limit(5).all()
        })

    # Create job
    job_id = str(uuid.uuid4())
    job = MonitorJob(
        id=job_id,
        name=job_name,
        replication_group_id=replication_group_id,
        region=region,
        endpoint_type=endpoint_type,
        duration_seconds=duration,
        status=JobStatus.pending,
        config_json=json.dumps({
            "region": region,
            "endpoint_type": endpoint_type,
            "duration": duration
        })
    )
    db.add(job)
    db.commit()

    logger.info(f"Created job {job_id} for {replication_group_id}")

    # Start background monitoring task
    # Note: Password is passed directly (not stored in DB for security)
    background_tasks.add_task(run_monitoring_job, job_id, password)

    return RedirectResponse(url=f"/jobs/{job_id}", status_code=303)


# =============================================================================
# JOBS LIST
# =============================================================================

@app.get("/jobs", response_class=HTMLResponse)
async def list_jobs(
    request: Request, 
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=10, le=100),
    db: Session = Depends(get_db)
):
    """List all monitoring jobs with pagination."""
    # Get total count
    total_jobs = db.query(func.count(MonitorJob.id)).scalar()
    total_pages = (total_jobs + per_page - 1) // per_page  # Ceiling division
    
    # Ensure page is within bounds
    page = min(page, max(1, total_pages))
    
    # Get paginated jobs
    offset = (page - 1) * per_page
    jobs = db.query(MonitorJob).order_by(desc(MonitorJob.created_at)).offset(offset).limit(per_page).all()
    
    jobs_data = []
    for job in jobs:
        shard_count = len(job.shards)
        completed_count = sum(1 for s in job.shards if s.status == ShardStatus.completed)
        failed_count = sum(1 for s in job.shards if s.status == ShardStatus.failed)
        
        jobs_data.append({
            "job": job,
            "shard_count": shard_count,
            "completed_count": completed_count,
            "failed_count": failed_count
        })
    
    return templates.TemplateResponse("jobs.html", {
        "request": request,
        "page_title": "Jobs",
        "jobs": jobs_data,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total_jobs": total_jobs,
            "total_pages": total_pages,
            "has_prev": page > 1,
            "has_next": page < total_pages,
        }
    })


# =============================================================================
# JOB DETAIL
# =============================================================================

@app.get("/jobs/{job_id}", response_class=HTMLResponse)
async def job_detail(request: Request, job_id: str, db: Session = Depends(get_db)):
    """Job detail page with shard status - loads instantly, heavy data fetched async."""
    job = db.query(MonitorJob).filter(MonitorJob.id == job_id).first()
    
    if not job:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": "Job not found",
            "page_title": "Error"
        }, status_code=404)
    
    # Get shard stats (lightweight - from metadata DB only)
    shards_data = []
    for shard in job.shards:
        shards_data.append({
            "shard": shard,
            "command_count": shard.command_count,
            "qps": shard.qps
        })
    
    # Sort by command count descending to highlight hot shards
    shards_data.sort(key=lambda x: x['command_count'], reverse=True)
    
    # Return page immediately - chart data will be loaded async via API
    return templates.TemplateResponse("job_detail.html", {
        "request": request,
        "job": job,
        "shards": shards_data,
        "page_title": f"Job: {job.name or job.id[:8]}"
    })


# =============================================================================
# ANALYSIS PAGE - Advanced Query & Visualization
# =============================================================================

@app.get("/jobs/{job_id}/analysis", response_class=HTMLResponse)
async def job_analysis(
    request: Request,
    job_id: str,
    group_by: str = "key_pattern",
    shard_filter: Optional[str] = None,
    command_filter: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Advanced analysis page with grouping and key pattern analysis."""
    job = db.query(MonitorJob).filter(MonitorJob.id == job_id).first()
    
    if not job:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": "Job not found",
            "page_title": "Error"
        }, status_code=404)
    
    # Get available shards for filter dropdown (from metadata DB)
    shards = db.query(MonitorShard).filter(MonitorShard.job_id == job_id).all()
    
    # Initialize defaults
    commands = []
    analysis_data = []
    total_commands = 0
    unique_keys = 0
    unique_patterns = 0
    
    # Query from job-specific database if it exists
    if job_db_exists(job_id):
        with get_job_db_context(job_id) as job_db:
            # Build base filter (no job_id needed - per-job DB)
            base_filter = []
            
            if shard_filter:
                base_filter.append(RedisCommand.shard_name == shard_filter)
            
            if command_filter:
                base_filter.append(RedisCommand.command == command_filter.upper())
            
            # Get available commands for filter dropdown
            commands_raw = job_db.query(RedisCommand.command).distinct().all()
            commands = sorted([c[0] for c in commands_raw if c[0]])
            
            # Group by analysis
            if group_by == "key_pattern":
                query = job_db.query(
                    RedisCommand.key_pattern,
                    func.count(RedisCommand.id).label('count'),
                    func.avg(RedisCommand.key_size_bytes).label('avg_size'),
                    func.sum(RedisCommand.key_size_bytes).label('total_size')
                )
                if base_filter:
                    query = query.filter(*base_filter)
                results = query.filter(
                    RedisCommand.key_pattern.isnot(None)
                ).group_by(
                    RedisCommand.key_pattern
                ).order_by(
                    desc('count')
                ).limit(limit).all()
                
                analysis_data = [{
                    'name': r[0],
                    'count': r[1],
                    'avg_size': r[2],
                    'total_size': r[3]
                } for r in results]
            
            elif group_by == "shard":
                query = job_db.query(
                    RedisCommand.shard_name,
                    func.count(RedisCommand.id).label('count'),
                    func.sum(RedisCommand.key_size_bytes).label('total_size')
                )
                if base_filter:
                    query = query.filter(*base_filter)
                results = query.group_by(
                    RedisCommand.shard_name
                ).order_by(
                    desc('count')
                ).limit(limit).all()
                
                analysis_data = [{
                    'name': r[0],
                    'count': r[1],
                    'total_size': r[2]
                } for r in results]
            
            elif group_by == "command":
                query = job_db.query(
                    RedisCommand.command,
                    func.count(RedisCommand.id).label('count')
                )
                if base_filter:
                    query = query.filter(*base_filter)
                results = query.group_by(
                    RedisCommand.command
                ).order_by(
                    desc('count')
                ).limit(limit).all()
                
                analysis_data = [{
                    'name': r[0],
                    'count': r[1]
                } for r in results]
            
            elif group_by == "client_ip":
                query = job_db.query(
                    RedisCommand.client_ip,
                    func.count(RedisCommand.id).label('count')
                )
                if base_filter:
                    query = query.filter(*base_filter)
                results = query.filter(
                    RedisCommand.client_ip.isnot(None)
                ).group_by(
                    RedisCommand.client_ip
                ).order_by(
                    desc('count')
                ).limit(limit).all()
                
                analysis_data = [{
                    'name': r[0],
                    'count': r[1]
                } for r in results]
            
            elif group_by == "key":
                query = job_db.query(
                    RedisCommand.key,
                    RedisCommand.shard_name,
                    func.count(RedisCommand.id).label('count'),
                    func.max(RedisCommand.key_size_bytes).label('size')
                )
                if base_filter:
                    query = query.filter(*base_filter)
                results = query.filter(
                    RedisCommand.key.isnot(None)
                ).group_by(
                    RedisCommand.key,
                    RedisCommand.shard_name
                ).order_by(
                    desc('count')
                ).limit(limit).all()
                
                analysis_data = [{
                    'name': r[0],
                    'shard': r[1],
                    'count': r[2],
                    'size': r[3]
                } for r in results]
            
            # Get overall stats
            total_commands = job_db.query(func.count(RedisCommand.id)).scalar() or 0
            unique_keys = job_db.query(func.count(func.distinct(RedisCommand.key))).scalar() or 0
            unique_patterns = job_db.query(func.count(func.distinct(RedisCommand.key_pattern))).scalar() or 0
    
    return templates.TemplateResponse("analysis.html", {
        "request": request,
        "job": job,
        "shards": shards,
        "commands": commands,
        "group_by": group_by,
        "shard_filter": shard_filter,
        "command_filter": command_filter,
        "limit": limit,
        "analysis_data": analysis_data,
        "total_commands": total_commands,
        "unique_keys": unique_keys,
        "unique_patterns": unique_patterns,
        "page_title": f"Analysis: {job.name or job.id[:8]}"
    })


# =============================================================================
# SHARD DETAIL
# =============================================================================

@app.get("/jobs/{job_id}/shards/{shard_name}", response_class=HTMLResponse)
async def shard_detail(
    request: Request,
    job_id: str,
    shard_name: str,
    tab: str = "overview",
    db: Session = Depends(get_db)
):
    """Shard detail page with commands and analysis."""
    job = db.query(MonitorJob).filter(MonitorJob.id == job_id).first()
    shard = db.query(MonitorShard).filter(
        MonitorShard.job_id == job_id,
        MonitorShard.shard_name == shard_name
    ).first()
    
    if not job or not shard:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": "Job or shard not found",
            "page_title": "Error"
        }, status_code=404)
    
    # Initialize defaults
    command_dist = []
    top_patterns = []
    top_keys = []
    recent_commands = []
    
    # Query from job-specific database
    if job_db_exists(job_id):
        with get_job_db_context(job_id) as job_db:
            # Get command distribution
            command_dist = job_db.query(
                RedisCommand.command,
                func.count(RedisCommand.id).label('count')
            ).filter(
                RedisCommand.shard_name == shard_name
            ).group_by(
                RedisCommand.command
            ).order_by(
                desc('count')
            ).limit(10).all()
            
            # Get top key patterns
            top_patterns = job_db.query(
                RedisCommand.key_pattern,
                func.count(RedisCommand.id).label('count'),
                func.avg(RedisCommand.key_size_bytes).label('avg_size')
            ).filter(
                RedisCommand.shard_name == shard_name,
                RedisCommand.key_pattern.isnot(None)
            ).group_by(
                RedisCommand.key_pattern
            ).order_by(
                desc('count')
            ).limit(20).all()
            
            # Get top individual keys
            top_keys = job_db.query(
                RedisCommand.key,
                func.count(RedisCommand.id).label('count'),
                func.max(RedisCommand.key_size_bytes).label('size')
            ).filter(
                RedisCommand.shard_name == shard_name,
                RedisCommand.key.isnot(None)
            ).group_by(
                RedisCommand.key
            ).order_by(
                desc('count')
            ).limit(30).all()
            
            # Get recent commands - convert to dicts to avoid DetachedInstanceError
            recent_cmd_rows = job_db.query(RedisCommand).filter(
                RedisCommand.shard_name == shard_name
            ).order_by(
                desc(RedisCommand.timestamp)
            ).limit(100).all()
            
            recent_commands = [{
                'datetime_utc': cmd.datetime_utc,
                'command': cmd.command,
                'key': cmd.key,
                'client_ip': cmd.client_ip,
                'args_json': cmd.args_json
            } for cmd in recent_cmd_rows]
    
    return templates.TemplateResponse("shard_detail.html", {
        "request": request,
        "job": job,
        "shard": shard,
        "tab": tab,
        "command_dist": command_dist,
        "top_patterns": top_patterns,
        "top_keys": top_keys,
        "recent_commands": recent_commands,
        "page_title": f"Shard: {shard_name}"
    })


# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.get("/api/jobs/{job_id}/status")
async def get_job_status(job_id: str, db: Session = Depends(get_db)):
    """Get current job status for polling."""
    job = db.query(MonitorJob).filter(MonitorJob.id == job_id).first()
    
    if not job:
        return {"error": "Job not found"}
    
    shards_status = []
    for shard in job.shards:
        # Calculate total CPU delta (user + sys)
        cpu_total = None
        cpu_pct = None  # CPU utilization as percentage of wall time
        cpu_per_1k = None  # CPU ms per 1000 commands
        aws_engine_cpu = None  # AWS EngineCPUUtilization
        
        if shard.cpu_sys_delta is not None and shard.cpu_user_delta is not None:
            cpu_total = shard.cpu_sys_delta + shard.cpu_user_delta
            # CPU % = (cpu_seconds / duration_seconds) * 100
            if job.duration_seconds > 0:
                cpu_pct = (cpu_total / job.duration_seconds) * 100
            # CPU per 1K commands (in milliseconds)
            if shard.command_count > 0:
                cpu_per_1k = (cpu_total * 1000) / (shard.command_count / 1000)
        

        
        # Calculate memory usage percentage
        memory_pct = None
        if shard.memory_used_bytes and shard.memory_max_bytes and shard.memory_max_bytes > 0:
            memory_pct = (shard.memory_used_bytes / shard.memory_max_bytes) * 100
        
        shard_data = {
            "shard_name": shard.shard_name,
            "host": shard.host,
            "port": shard.port,
            "status": shard.status.value,
            "command_count": shard.command_count,
            "qps": shard.qps,
            "error": shard.error_message,
            # Redis info
            "redis_version": shard.redis_version,
            # Memory info
            "memory_used": shard.memory_used_bytes,
            "memory_max": shard.memory_max_bytes,
            "memory_peak": shard.memory_peak_bytes,
            "memory_rss": shard.memory_rss_bytes,
            "memory_pct": memory_pct,
            # CPU info
            "cpu_sys_delta": shard.cpu_sys_delta,
            "cpu_user_delta": shard.cpu_user_delta,
            "cpu_total": cpu_total,
            "cpu_pct": cpu_pct,  # Redis CPU utilization %
            "cpu_per_1k": cpu_per_1k,  # CPU ms per 1K commands
            "aws_engine_cpu_max": shard.aws_engine_cpu_max,  # AWS EngineCPUUtilization max %
        }
        shards_status.append(shard_data)
    
    # Calculate actual commands from job-specific database for accuracy
    actual_total = 0
    if job_db_exists(job_id):
        try:
            with get_job_db_context(job_id) as job_db:
                actual_total = job_db.query(func.count(RedisCommand.id)).scalar() or 0
        except:
            pass
    
    return {
        "job_id": job_id,
        "status": job.status.value,
        "total_commands": max(job.total_commands, actual_total),
        "error_message": job.error_message,
        "started_at": job.started_at.isoformat() + 'Z' if job.started_at else None,
        "shards": shards_status
    }


@app.get("/api/jobs/{job_id}/chart-data")
async def get_chart_data(
    job_id: str,
    chart_type: str = "shard_distribution",
    db: Session = Depends(get_db)
):
    """Get chart data for visualizations."""
    if not job_db_exists(job_id):
        return {"labels": [], "values": []}
    
    with get_job_db_context(job_id) as job_db:
        if chart_type == "shard_distribution":
            results = job_db.query(
                RedisCommand.shard_name,
                func.count(RedisCommand.id).label('count')
            ).group_by(
                RedisCommand.shard_name
            ).all()
            
            return {
                "labels": [r[0] for r in results],
                "values": [r[1] for r in results]
            }
        
        elif chart_type == "command_distribution":
            results = job_db.query(
                RedisCommand.command,
                func.count(RedisCommand.id).label('count')
            ).group_by(
                RedisCommand.command
            ).order_by(
                desc('count')
            ).limit(10).all()
            
            return {
                "labels": [r[0] for r in results],
                "values": [r[1] for r in results]
            }
        
        elif chart_type == "key_pattern_distribution":
            results = job_db.query(
                RedisCommand.key_pattern,
                func.count(RedisCommand.id).label('count')
            ).filter(
                RedisCommand.key_pattern.isnot(None)
            ).group_by(
                RedisCommand.key_pattern
            ).order_by(
                desc('count')
            ).limit(10).all()
            
            return {
                "labels": [r[0] for r in results],
                "values": [r[1] for r in results]
            }
    
    return {"labels": [], "values": []}


@app.get("/api/jobs/{job_id}/stats")
async def get_job_stats(job_id: str, db: Session = Depends(get_db)):
    """Get all statistics for job detail page - loaded async for fast page load."""
    job = db.query(MonitorJob).filter(MonitorJob.id == job_id).first()
    
    if not job or job.status.value != 'completed' or not job_db_exists(job_id):
        return {
            "loaded": False,
            "command_types": [],
            "command_by_shard": {},
            "top_patterns": [],
            "pattern_by_shard": {}
        }
    
    command_by_shard = {}
    pattern_by_shard = {}
    cmd_types = []
    top_patterns = []
    
    with get_job_db_context(job_id) as job_db:
        # Get all command types used
        cmd_types_raw = job_db.query(RedisCommand.command).distinct().all()
        cmd_types = sorted([c[0] for c in cmd_types_raw if c[0]])
        
        # Get command counts per shard
        shard_cmd_data = job_db.query(
            RedisCommand.shard_name,
            RedisCommand.command,
            func.count(RedisCommand.id).label('count')
        ).group_by(
            RedisCommand.shard_name,
            RedisCommand.command
        ).all()
        
        # Organize data: {shard_name: {command: count}}
        for row in shard_cmd_data:
            shard_name, cmd, count = row
            if shard_name not in command_by_shard:
                command_by_shard[shard_name] = {}
            command_by_shard[shard_name][cmd] = count
        
        # Get top 10 key patterns overall
        top_patterns_raw = job_db.query(
            RedisCommand.key_pattern,
            func.count(RedisCommand.id).label('count')
        ).filter(
            RedisCommand.key_pattern.isnot(None)
        ).group_by(
            RedisCommand.key_pattern
        ).order_by(
            func.count(RedisCommand.id).desc()
        ).limit(10).all()
        top_patterns = [p[0] for p in top_patterns_raw if p[0]]
        
        # Get pattern counts per shard (for top patterns only)
        if top_patterns:
            shard_pattern_data = job_db.query(
                RedisCommand.shard_name,
                RedisCommand.key_pattern,
                func.count(RedisCommand.id).label('count')
            ).filter(
                RedisCommand.key_pattern.in_(top_patterns)
            ).group_by(
                RedisCommand.shard_name,
                RedisCommand.key_pattern
            ).all()
            
            # Organize: {shard_name: {pattern: count}}
            for row in shard_pattern_data:
                shard_name, pattern, count = row
                if shard_name not in pattern_by_shard:
                    pattern_by_shard[shard_name] = {}
                pattern_by_shard[shard_name][pattern] = count
    
    return {
        "loaded": True,
        "command_types": cmd_types,
        "command_by_shard": command_by_shard,
        "top_patterns": top_patterns,
        "pattern_by_shard": pattern_by_shard
    }


@app.get("/api/jobs/{job_id}/insights")
async def get_job_insights(job_id: str, db: Session = Depends(get_db)):
    """
    Get aggregated insights for a job - hot shards, abuse patterns, lock contention, full scans.
    Optimized for fast dashboard rendering.
    """
    job = db.query(MonitorJob).filter(MonitorJob.id == job_id).first()
    
    if not job or job.status.value != 'completed' or not job_db_exists(job_id):
        return JSONResponse({"error": "Job not found or not completed"}, status_code=404)
    
    insights = {
        "total_commands": job.total_commands or 0,
        "hot_shards": [],
        "top_signatures": [],
        "abuse_combos": [],
        "lock_stats": {"count": 0, "percentage": 0, "top_patterns": []},
        "full_scan_stats": {"count": 0, "percentage": 0, "top_patterns": []},
        "signature_by_shard": {}
    }
    
    with get_job_db_context(job_id) as job_db:
        total = job.total_commands or 1
        
        # 1. Hot shards analysis (deviation from average)
        shard_counts = job_db.execute(text("""
            SELECT shard_name, COUNT(*) as cnt 
            FROM redis_commands 
            GROUP BY shard_name 
            ORDER BY cnt DESC
        """)).fetchall()
        
        if shard_counts:
            counts = [r[1] for r in shard_counts]
            avg_count = sum(counts) / len(counts)
            
            for shard_name, cnt in shard_counts:
                deviation = ((cnt - avg_count) / avg_count * 100) if avg_count > 0 else 0
                status = "hot" if deviation > 25 else "normal" if deviation > -25 else "cold"
                insights["hot_shards"].append({
                    "shard": shard_name,
                    "count": cnt,
                    "percentage": round(cnt / total * 100, 1),
                    "deviation": round(deviation, 1),
                    "status": status
                })
        
        # 2. Top command signatures (aggregated patterns)
        top_sigs = job_db.execute(text("""
            SELECT command_signature, COUNT(*) as cnt,
                   SUM(is_full_scan) as scan_count,
                   SUM(is_lock_op) as lock_count
            FROM redis_commands 
            WHERE command_signature IS NOT NULL
            GROUP BY command_signature 
            ORDER BY cnt DESC 
            LIMIT 20
        """)).fetchall()
        
        for sig, cnt, scan_cnt, lock_cnt in top_sigs:
            insights["top_signatures"].append({
                "signature": sig,
                "count": cnt,
                "percentage": round(cnt / total * 100, 2),
                "has_scans": (scan_cnt or 0) > 0,
                "has_locks": (lock_cnt or 0) > 0
            })
        
        # 3. Abuse combos: (client_ip + signature) - find heavy hitters
        abuse_combos = job_db.execute(text("""
            SELECT client_ip, command_signature, COUNT(*) as cnt
            FROM redis_commands 
            WHERE client_ip IS NOT NULL AND command_signature IS NOT NULL
            GROUP BY client_ip, command_signature 
            ORDER BY cnt DESC 
            LIMIT 15
        """)).fetchall()
        
        for ip, sig, cnt in abuse_combos:
            insights["abuse_combos"].append({
                "client_ip": ip,
                "signature": sig,
                "count": cnt,
                "percentage": round(cnt / total * 100, 2)
            })
        
        # 4. Lock operations stats
        lock_stats = job_db.execute(text("""
            SELECT COUNT(*) as cnt FROM redis_commands WHERE is_lock_op = 1
        """)).fetchone()
        lock_count = lock_stats[0] if lock_stats else 0
        
        lock_patterns = job_db.execute(text("""
            SELECT command_signature, COUNT(*) as cnt
            FROM redis_commands 
            WHERE is_lock_op = 1 AND command_signature IS NOT NULL
            GROUP BY command_signature 
            ORDER BY cnt DESC 
            LIMIT 5
        """)).fetchall()
        
        insights["lock_stats"] = {
            "count": lock_count,
            "percentage": round(lock_count / total * 100, 2),
            "top_patterns": [{"signature": p[0], "count": p[1]} for p in lock_patterns]
        }
        
        # 5. Full scan stats
        scan_stats = job_db.execute(text("""
            SELECT COUNT(*) as cnt FROM redis_commands WHERE is_full_scan = 1
        """)).fetchone()
        scan_count = scan_stats[0] if scan_stats else 0
        
        scan_patterns = job_db.execute(text("""
            SELECT command_signature, COUNT(*) as cnt
            FROM redis_commands 
            WHERE is_full_scan = 1 AND command_signature IS NOT NULL
            GROUP BY command_signature 
            ORDER BY cnt DESC 
            LIMIT 5
        """)).fetchall()
        
        insights["full_scan_stats"] = {
            "count": scan_count,
            "percentage": round(scan_count / total * 100, 2),
            "top_patterns": [{"signature": p[0], "count": p[1]} for p in scan_patterns]
        }
        
        # 6. Signature distribution by shard (for charts)
        sig_by_shard = job_db.execute(text("""
            SELECT shard_name, command_signature, COUNT(*) as cnt
            FROM redis_commands 
            WHERE command_signature IS NOT NULL
            GROUP BY shard_name, command_signature 
            ORDER BY cnt DESC
            LIMIT 100
        """)).fetchall()
        
        for shard, sig, cnt in sig_by_shard:
            if shard not in insights["signature_by_shard"]:
                insights["signature_by_shard"][shard] = {}
            insights["signature_by_shard"][shard][sig] = cnt
    
    return insights


@app.post("/api/jobs/{job_id}/sample-sizes")
async def trigger_size_sampling(
    job_id: str,
    password: str = Form(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """Trigger key size sampling for a job."""
    job = db.query(MonitorJob).filter(MonitorJob.id == job_id).first()
    
    if not job:
        return JSONResponse({"error": "Job not found"}, status_code=404)
    
    background_tasks.add_task(sample_key_sizes, job_id, password)
    
    return {"status": "sampling started"}


@app.post("/api/jobs/{job_id}/cancel")
async def cancel_job_endpoint(job_id: str, db: Session = Depends(get_db)):
    """Cancel a running job."""
    job = db.query(MonitorJob).filter(MonitorJob.id == job_id).first()
    
    if not job:
        return JSONResponse({"error": "Job not found"}, status_code=404)
    
    if job.status != JobStatus.running:
        return JSONResponse({"error": f"Job is not running (status: {job.status.value})"}, status_code=400)
    
    # Try to cancel the job
    if cancel_job(job_id):
        return {"status": "cancelling", "message": "Job cancellation requested"}
    else:
        return JSONResponse({"error": "Job not found in running jobs registry"}, status_code=404)


@app.delete("/api/jobs/{job_id}")
async def delete_job(job_id: str, db: Session = Depends(get_db)):
    """Delete a job and all its data."""
    job = db.query(MonitorJob).filter(MonitorJob.id == job_id).first()
    
    if not job:
        return JSONResponse({"error": "Job not found"}, status_code=404)
    
    # Delete job-specific database file (contains all commands)
    delete_job_db(job_id)
    
    # Delete metadata (shards and job record)
    db.query(MonitorShard).filter(MonitorShard.job_id == job_id).delete()
    db.delete(job)
    db.commit()
    
    return {"status": "deleted"}


# =============================================================================
# RE-RUN JOB
# =============================================================================

@app.post("/jobs/{job_id}/rerun")
async def rerun_job(
    job_id: str,
    background_tasks: BackgroundTasks,
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Re-run a job with the same configuration but new password."""
    original_job = db.query(MonitorJob).filter(MonitorJob.id == job_id).first()
    
    if not original_job:
        return JSONResponse({"error": "Job not found"}, status_code=404)
    
    # Create new job with same config
    new_job_id = str(uuid.uuid4())
    new_job = MonitorJob(
        id=new_job_id,
        name=f"{original_job.name or original_job.replication_group_id} (re-run)" if original_job.name else None,
        replication_group_id=original_job.replication_group_id,
        region=original_job.region,
        endpoint_type=original_job.endpoint_type,
        duration_seconds=original_job.duration_seconds,
        status=JobStatus.pending,
        config_json=original_job.config_json
    )
    db.add(new_job)
    db.commit()
    
    logger.info(f"Created re-run job {new_job_id} from {job_id}")
    
    # Start background monitoring
    background_tasks.add_task(run_monitoring_job, new_job_id, password)
    
    return RedirectResponse(url=f"/jobs/{new_job_id}", status_code=303)


# =============================================================================
# COMPARE JOBS
# =============================================================================

@app.get("/compare", response_class=HTMLResponse)
async def compare_jobs(
    request: Request,
    jobs: str = Query(default=""),
    db: Session = Depends(get_db)
):
    """Compare multiple monitoring jobs side by side."""
    job_ids_raw = [j.strip() for j in jobs.split(",") if j.strip()]
    
    # Remove duplicates while preserving order
    seen = set()
    job_ids = []
    for jid in job_ids_raw:
        if jid not in seen:
            seen.add(jid)
            job_ids.append(jid)
    
    # Track if duplicates were removed
    had_duplicates = len(job_ids_raw) != len(job_ids)
    
    # Get all completed jobs for the selection UI
    all_completed_jobs = db.query(MonitorJob).filter(
        MonitorJob.status == JobStatus.completed
    ).order_by(desc(MonitorJob.created_at)).limit(20).all()
    
    if len(job_ids) < 2:
        return templates.TemplateResponse("compare.html", {
            "request": request,
            "jobs": [],
            "all_jobs": all_completed_jobs,
            "stats": {},
            "page_title": "Compare Jobs",
            "had_duplicates": had_duplicates
        })
    
    # Fetch job objects
    job_objects = []
    for job_id in job_ids[:4]:  # Max 4 jobs
        job = db.query(MonitorJob).filter(MonitorJob.id == job_id).first()
        if job and job.status == JobStatus.completed:
            job_objects.append(job)
    
    if len(job_objects) < 2:
        return templates.TemplateResponse("compare.html", {
            "request": request,
            "jobs": [],
            "all_jobs": all_completed_jobs,
            "stats": {},
            "page_title": "Compare Jobs",
            "had_duplicates": had_duplicates
        })
    
    # Gather stats for each job
    stats = {}
    for job in job_objects:
        job_stats = {
            "shard_count": 0,
            "unique_keys": 0,
            "unique_patterns": 0,
            "top_commands": [],
            "top_patterns": [],
            "shard_distribution": []
        }
        
        # Shard count from main DB
        job_stats["shard_count"] = db.query(MonitorShard).filter(
            MonitorShard.job_id == job.id
        ).count()
        
        # Query job-specific DB for detailed stats
        if job_db_exists(job.id):
            with get_job_db_context(job.id) as job_db:
                # Unique keys
                unique_keys_result = job_db.query(
                    func.count(func.distinct(RedisCommand.key))
                ).filter(RedisCommand.key.isnot(None)).scalar()
                job_stats["unique_keys"] = unique_keys_result or 0
                
                # Unique patterns
                unique_patterns_result = job_db.query(
                    func.count(func.distinct(RedisCommand.key_pattern))
                ).filter(RedisCommand.key_pattern.isnot(None)).scalar()
                job_stats["unique_patterns"] = unique_patterns_result or 0
                
                # Top commands
                top_cmds = job_db.query(
                    RedisCommand.command,
                    func.count(RedisCommand.id).label('count')
                ).group_by(
                    RedisCommand.command
                ).order_by(
                    func.count(RedisCommand.id).desc()
                ).limit(10).all()
                job_stats["top_commands"] = [{"command": c, "count": cnt} for c, cnt in top_cmds]
                
                # Top patterns
                top_pats = job_db.query(
                    RedisCommand.key_pattern,
                    func.count(RedisCommand.id).label('count')
                ).filter(
                    RedisCommand.key_pattern.isnot(None)
                ).group_by(
                    RedisCommand.key_pattern
                ).order_by(
                    func.count(RedisCommand.id).desc()
                ).limit(10).all()
                job_stats["top_patterns"] = [{"pattern": p, "count": cnt} for p, cnt in top_pats]
                
                # Shard distribution
                shard_dist = job_db.query(
                    RedisCommand.shard_name,
                    func.count(RedisCommand.id).label('count')
                ).group_by(
                    RedisCommand.shard_name
                ).order_by(
                    RedisCommand.shard_name
                ).all()
                job_stats["shard_distribution"] = [{"shard_name": s, "count": cnt} for s, cnt in shard_dist]
        
        stats[job.id] = job_stats
    
    return templates.TemplateResponse("compare.html", {
        "request": request,
        "jobs": job_objects,
        "stats": stats,
        "page_title": "Compare Jobs",
        "had_duplicates": had_duplicates
    })


# =============================================================================
# CUSTOM SQL QUERY
# =============================================================================

@app.get("/query", response_class=HTMLResponse)
async def query_page(
    request: Request,
    sql: Optional[str] = None,
    job_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Custom SQL query page - queries job-specific database."""
    results = None
    error = None
    columns = []
    
    # Get all jobs for dropdown
    jobs = db.query(MonitorJob).order_by(desc(MonitorJob.created_at)).all()
    
    if sql and job_id:
        try:
            # Safety: only allow SELECT queries
            if not sql.strip().upper().startswith("SELECT"):
                error = "Only SELECT queries are allowed"
            elif not job_db_exists(job_id):
                error = f"No data found for job {job_id}. The job may not have captured any commands."
            else:
                # Query the job-specific database
                with get_job_db_context(job_id) as job_db:
                    result = job_db.execute(text(sql))
                    columns = list(result.keys())
                    results = [dict(row._mapping) for row in result.fetchall()]
        except Exception as e:
            error = str(e)
    elif sql and not job_id:
        error = "Please select a job to query"
    
    return templates.TemplateResponse("query.html", {
        "request": request,
        "sql": sql or "",
        "results": results,
        "columns": columns,
        "error": error,
        "jobs": jobs,
        "selected_job_id": job_id,
        "page_title": "SQL Query"
    })


# =============================================================================
# TIMELINE ANALYSIS
# =============================================================================

@app.get("/jobs/{job_id}/timeline", response_class=HTMLResponse)
async def job_timeline(
    request: Request,
    job_id: str,
    db: Session = Depends(get_db)
):
    """Timeline analysis view - time-series visualization of Redis traffic."""
    job = db.query(MonitorJob).filter(MonitorJob.id == job_id).first()
    if not job:
        return RedirectResponse(url="/jobs", status_code=302)
    
    # Get shards for this job
    shards = db.query(MonitorShard).filter(MonitorShard.job_id == job_id).all()
    shard_names = sorted([s.shard_name for s in shards])
    
    # Get unique commands, patterns, and signatures from the job database
    commands = []
    patterns = []
    signatures = []
    
    if job_db_exists(job_id):
        with get_job_db_context(job_id) as job_db:
            # Get unique commands
            cmd_result = job_db.execute(text(
                "SELECT DISTINCT command FROM redis_commands ORDER BY command"
            ))
            commands = [row[0] for row in cmd_result.fetchall()]
            
            # Get top patterns
            pattern_result = job_db.execute(text(
                """SELECT key_pattern, COUNT(*) as cnt 
                   FROM redis_commands 
                   WHERE key_pattern IS NOT NULL 
                   GROUP BY key_pattern 
                   ORDER BY cnt DESC 
                   LIMIT 50"""
            ))
            patterns = [row[0] for row in pattern_result.fetchall()]
            
            # Get top signatures
            sig_result = job_db.execute(text(
                """SELECT command_signature, COUNT(*) as cnt 
                   FROM redis_commands 
                   WHERE command_signature IS NOT NULL 
                   GROUP BY command_signature 
                   ORDER BY cnt DESC 
                   LIMIT 50"""
            ))
            signatures = [row[0] for row in sig_result.fetchall()]
    
    return templates.TemplateResponse("timeline.html", {
        "request": request,
        "job": job,
        "shards": shard_names,
        "commands": commands,
        "patterns": patterns,
        "signatures": signatures,
        "page_title": f"Timeline - {job.name or job.replication_group_id}"
    })


@app.get("/api/jobs/{job_id}/timeline-data")
async def get_timeline_data(
    job_id: str,
    group_by: str = "command_signature",  # command_signature, command, client_ip, key_pattern, shard_name
    shards: Optional[str] = None,  # comma-separated shard names
    filter_value: Optional[str] = None,  # legacy: specific value to filter (applies to group_by column)
    filter_command: Optional[str] = None,  # filter by command
    filter_client_ip: Optional[str] = None,  # filter by client IP
    filter_key_pattern: Optional[str] = None,  # filter by key pattern
    filter_command_signature: Optional[str] = None,  # filter by command signature
    granularity: int = 1,  # seconds per bucket
    db: Session = Depends(get_db)
):
    """Get time-series data for timeline visualization."""
    job = db.query(MonitorJob).filter(MonitorJob.id == job_id).first()
    if not job:
        return JSONResponse({"error": "Job not found"}, status_code=404)
    
    if not job_db_exists(job_id):
        return JSONResponse({"error": "No data for this job"}, status_code=404)
    
    # Parse shards
    shard_list = shards.split(",") if shards else None
    
    with get_job_db_context(job_id) as job_db:
        # Build the query based on group_by
        group_column = {
            "command_signature": "command_signature",
            "command": "command",
            "client_ip": "client_ip", 
            "key_pattern": "key_pattern",
            "shard_name": "shard_name"
        }.get(group_by, "command_signature")
        
        # Build WHERE clause
        where_clauses = ["1=1"]
        params = {}
        
        if shard_list:
            placeholders = ", ".join([f":shard_{i}" for i in range(len(shard_list))])
            where_clauses.append(f"shard_name IN ({placeholders})")
            for i, s in enumerate(shard_list):
                params[f"shard_{i}"] = s
        
        # Individual column filters
        if filter_command:
            where_clauses.append("command = :filter_command")
            params["filter_command"] = filter_command
        
        if filter_client_ip:
            where_clauses.append("client_ip LIKE :filter_client_ip")
            params["filter_client_ip"] = f"%{filter_client_ip}%"
        
        if filter_key_pattern:
            where_clauses.append("key_pattern = :filter_key_pattern")
            params["filter_key_pattern"] = filter_key_pattern
        
        if filter_command_signature:
            where_clauses.append("command_signature = :filter_command_signature")
            params["filter_command_signature"] = filter_command_signature
        
        # Legacy filter_value (applies to the group_by column)
        if filter_value:
            where_clauses.append(f"{group_column} = :filter_value")
            params["filter_value"] = filter_value
        
        where_sql = " AND ".join(where_clauses)
        
        # Query for time-series data
        # Group by time bucket and the selected dimension
        query = f"""
            SELECT 
                CAST((CAST(timestamp AS INTEGER) / :granularity) * :granularity AS INTEGER) as time_bucket,
                shard_name,
                {group_column} as group_value,
                COUNT(*) as count
            FROM redis_commands
            WHERE {where_sql}
            GROUP BY time_bucket, shard_name, {group_column}
            ORDER BY time_bucket, shard_name
        """
        params["granularity"] = granularity
        
        result = job_db.execute(text(query), params)
        rows = result.fetchall()
        
        # Process data for Chart.js
        # Structure: {time_bucket: {shard: {group_value: count}}}
        time_data = {}
        all_groups = set()
        all_shards = set()
        
        for row in rows:
            time_bucket, shard_name, group_value, count = row
            if time_bucket not in time_data:
                time_data[time_bucket] = {}
            if shard_name not in time_data[time_bucket]:
                time_data[time_bucket][shard_name] = {}
            
            group_key = group_value or "(none)"
            time_data[time_bucket][shard_name][group_key] = count
            all_groups.add(group_key)
            all_shards.add(shard_name)
        
        # Sort and prepare response
        sorted_times = sorted(time_data.keys())
        all_groups = sorted(all_groups)
        all_shards = sorted(all_shards)
        
        # Convert timestamps to readable format
        labels = []
        for ts in sorted_times:
            dt = datetime.fromtimestamp(ts)
            labels.append(dt.strftime("%H:%M:%S"))
        
        # Build datasets for Chart.js
        # Always group by the selected dimension (group_by parameter)
        datasets = []
        
        # Color palette - vibrant, distinct colors
        colors = [
            "rgba(99, 102, 241, 0.7)",   # indigo
            "rgba(16, 185, 129, 0.7)",   # emerald
            "rgba(249, 115, 22, 0.7)",   # orange
            "rgba(14, 165, 233, 0.7)",   # sky
            "rgba(244, 63, 94, 0.7)",    # rose
            "rgba(168, 85, 247, 0.7)",   # purple
            "rgba(234, 179, 8, 0.7)",    # yellow
            "rgba(20, 184, 166, 0.7)",   # teal
            "rgba(239, 68, 68, 0.7)",    # red
            "rgba(59, 130, 246, 0.7)",   # blue
            "rgba(236, 72, 153, 0.7)",   # pink
            "rgba(132, 204, 22, 0.7)",   # lime
        ]
        
        # Calculate totals per group to sort by most active
        group_totals = {}
        for group in all_groups:
            total = 0
            for ts in sorted_times:
                for shard in all_shards:
                    shard_data = time_data[ts].get(shard, {})
                    total += shard_data.get(group, 0)
            group_totals[group] = total
        
        # Sort groups by total count (descending) and take top 12
        sorted_groups = sorted(all_groups, key=lambda g: group_totals.get(g, 0), reverse=True)
        top_groups = sorted_groups[:12]
        
        # Create dataset for each group value
        for idx, group in enumerate(top_groups):
            data = []
            for ts in sorted_times:
                total = 0
                for shard in all_shards:
                    shard_data = time_data[ts].get(shard, {})
                    total += shard_data.get(group, 0)
                data.append(total)
            
            # Truncate long labels for display
            display_label = group[:35] + "..." if len(group) > 35 else group
            
            datasets.append({
                "label": display_label,
                "fullLabel": group,  # Keep full label for tooltips
                "data": data,
                "backgroundColor": colors[idx % len(colors)],
                "borderColor": colors[idx % len(colors)].replace("0.7", "1"),
                "borderWidth": 1
            })
        
        # Get summary stats
        total_commands = sum(
            sum(shard_data.values()) 
            for time_data_item in time_data.values() 
            for shard_data in time_data_item.values()
        )
        
        return JSONResponse({
            "labels": labels,
            "datasets": datasets,
            "summary": {
                "total_commands": total_commands,
                "time_range": f"{labels[0]} - {labels[-1]}" if labels else "N/A",
                "shards": list(all_shards),
                "groups": list(all_groups)[:20]
            }
        })


@app.get("/jobs/{job_id}/shard-distribution", response_class=HTMLResponse)
async def job_shard_distribution(
    request: Request,
    job_id: str,
    db: Session = Depends(get_db)
):
    """Shard distribution view - visualize commands by shard."""
    job = db.query(MonitorJob).filter(MonitorJob.id == job_id).first()
    if not job:
        return RedirectResponse(url="/jobs", status_code=302)
    
    # Get shards for this job
    shards = db.query(MonitorShard).filter(MonitorShard.job_id == job_id).all()
    shard_names = sorted([s.shard_name for s in shards])
    
    # Get unique commands, patterns, and signatures from the job database
    commands = []
    patterns = []
    signatures = []
    
    if job_db_exists(job_id):
        with get_job_db_context(job_id) as job_db:
            # Get unique commands
            cmd_result = job_db.execute(text(
                "SELECT DISTINCT command FROM redis_commands ORDER BY command"
            ))
            commands = [row[0] for row in cmd_result.fetchall()]
            
            # Get top patterns
            pattern_result = job_db.execute(text(
                """SELECT key_pattern, COUNT(*) as cnt 
                   FROM redis_commands 
                   WHERE key_pattern IS NOT NULL 
                   GROUP BY key_pattern 
                   ORDER BY cnt DESC 
                   LIMIT 50"""
            ))
            patterns = [row[0] for row in pattern_result.fetchall()]
            
            # Get top signatures
            sig_result = job_db.execute(text(
                """SELECT command_signature, COUNT(*) as cnt 
                   FROM redis_commands 
                   WHERE command_signature IS NOT NULL 
                   GROUP BY command_signature 
                   ORDER BY cnt DESC 
                   LIMIT 50"""
            ))
            signatures = [row[0] for row in sig_result.fetchall()]
    
    return templates.TemplateResponse("shard_distribution.html", {
        "request": request,
        "job": job,
        "shards": shard_names,
        "commands": commands,
        "patterns": patterns,
        "signatures": signatures,
        "page_title": f"Shard Distribution - {job.name or job.replication_group_id}"
    })


@app.get("/api/jobs/{job_id}/shard-distribution-data")
async def get_shard_distribution_data(
    job_id: str,
    group_by: str = "command_signature",  # command_signature, command, client_ip, key_pattern
    filter_command: Optional[str] = None,
    filter_client_ip: Optional[str] = None,
    filter_key_pattern: Optional[str] = None,
    filter_command_signature: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get shard distribution data - commands grouped by shard, stacked by group_by dimension."""
    job = db.query(MonitorJob).filter(MonitorJob.id == job_id).first()
    if not job:
        return JSONResponse({"error": "Job not found"}, status_code=404)
    
    if not job_db_exists(job_id):
        return JSONResponse({"error": "No data for this job"}, status_code=404)
    
    with get_job_db_context(job_id) as job_db:
        # Build the query based on group_by
        group_column = {
            "command_signature": "command_signature",
            "command": "command",
            "client_ip": "client_ip", 
            "key_pattern": "key_pattern"
        }.get(group_by, "command_signature")
        
        # Build WHERE clause
        where_clauses = ["1=1"]
        params = {}
        
        if filter_command:
            where_clauses.append("command = :filter_command")
            params["filter_command"] = filter_command
        
        if filter_client_ip:
            where_clauses.append("client_ip LIKE :filter_client_ip")
            params["filter_client_ip"] = f"%{filter_client_ip}%"
        
        if filter_key_pattern:
            where_clauses.append("key_pattern = :filter_key_pattern")
            params["filter_key_pattern"] = filter_key_pattern
        
        if filter_command_signature:
            where_clauses.append("command_signature = :filter_command_signature")
            params["filter_command_signature"] = filter_command_signature
        
        where_sql = " AND ".join(where_clauses)
        
        # Query: group by shard and the selected dimension
        query = f"""
            SELECT shard_name, {group_column}, COUNT(*) as count
            FROM redis_commands
            WHERE {where_sql}
            GROUP BY shard_name, {group_column}
            ORDER BY shard_name, count DESC
        """
        
        result = job_db.execute(text(query), params)
        rows = result.fetchall()
        
        # Process into shard-based structure
        shard_data = {}
        total_commands = 0
        
        for row in rows:
            shard_name, group_value, count = row
            if shard_name not in shard_data:
                shard_data[shard_name] = {"breakdown": {}}
            
            group_key = group_value or "(none)"
            shard_data[shard_name]["breakdown"][group_key] = count
            total_commands += count
        
        # Convert to list format
        shards = []
        for shard_name in sorted(shard_data.keys()):
            shards.append({
                "name": shard_name,
                "breakdown": shard_data[shard_name]["breakdown"]
            })
        
        return JSONResponse({
            "shards": shards,
            "total_commands": total_commands,
            "group_by": group_by
        })


@app.get("/api/jobs/{job_id}/filter-options")
async def get_filter_options(
    job_id: str,
    filter_command: Optional[str] = None,
    filter_client_ip: Optional[str] = None,
    filter_key_pattern: Optional[str] = None,
    filter_command_signature: Optional[str] = None,
    filter_shard: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get available filter options based on current filter criteria.
    
    Returns only options that would produce results given the current filters.
    """
    job = db.query(MonitorJob).filter(MonitorJob.id == job_id).first()
    if not job:
        return JSONResponse({"error": "Job not found"}, status_code=404)
    
    if not job_db_exists(job_id):
        return JSONResponse({"error": "No data for this job"}, status_code=404)
    
    with get_job_db_context(job_id) as job_db:
        # Build base WHERE clause from current filters
        where_clauses = ["1=1"]
        params = {}
        
        if filter_command:
            where_clauses.append("command = :filter_command")
            params["filter_command"] = filter_command
        
        if filter_client_ip:
            where_clauses.append("client_ip LIKE :filter_client_ip")
            params["filter_client_ip"] = f"%{filter_client_ip}%"
        
        if filter_key_pattern:
            where_clauses.append("key_pattern = :filter_key_pattern")
            params["filter_key_pattern"] = filter_key_pattern
        
        if filter_command_signature:
            where_clauses.append("command_signature = :filter_command_signature")
            params["filter_command_signature"] = filter_command_signature
        
        if filter_shard:
            # Handle comma-separated shard list
            shard_list = [s.strip() for s in filter_shard.split(",") if s.strip()]
            if shard_list:
                placeholders = ", ".join([f":shard_{i}" for i in range(len(shard_list))])
                where_clauses.append(f"shard_name IN ({placeholders})")
                for i, s in enumerate(shard_list):
                    params[f"shard_{i}"] = s
        
        where_sql = " AND ".join(where_clauses)
        
        # Get available commands (excluding current command filter for this query)
        cmd_where = [c for c in where_clauses if "filter_command" not in c]
        cmd_params = {k: v for k, v in params.items() if "filter_command" not in k}
        cmd_query = f"""
            SELECT DISTINCT command, COUNT(*) as cnt
            FROM redis_commands 
            WHERE {' AND '.join(cmd_where) if cmd_where else '1=1'}
            GROUP BY command
            ORDER BY cnt DESC
            LIMIT 50
        """
        commands = [row[0] for row in job_db.execute(text(cmd_query), cmd_params).fetchall()]
        
        # Get available key patterns (excluding current key_pattern filter)
        pattern_where = [c for c in where_clauses if "filter_key_pattern" not in c]
        pattern_params = {k: v for k, v in params.items() if "filter_key_pattern" not in k}
        pattern_query = f"""
            SELECT DISTINCT key_pattern, COUNT(*) as cnt
            FROM redis_commands 
            WHERE {' AND '.join(pattern_where) if pattern_where else '1=1'} AND key_pattern IS NOT NULL
            GROUP BY key_pattern
            ORDER BY cnt DESC
            LIMIT 50
        """
        patterns = [row[0] for row in job_db.execute(text(pattern_query), pattern_params).fetchall()]
        
        # Get available signatures (excluding current signature filter)
        sig_where = [c for c in where_clauses if "filter_command_signature" not in c]
        sig_params = {k: v for k, v in params.items() if "filter_command_signature" not in k}
        sig_query = f"""
            SELECT DISTINCT command_signature, COUNT(*) as cnt
            FROM redis_commands 
            WHERE {' AND '.join(sig_where) if sig_where else '1=1'} AND command_signature IS NOT NULL
            GROUP BY command_signature
            ORDER BY cnt DESC
            LIMIT 50
        """
        signatures = [row[0] for row in job_db.execute(text(sig_query), sig_params).fetchall()]
        
        # Get available shards (excluding current shard filter)
        shard_where = [c for c in where_clauses if "shard_" not in c]
        shard_params = {k: v for k, v in params.items() if "shard_" not in k}
        shard_query = f"""
            SELECT DISTINCT shard_name, COUNT(*) as cnt
            FROM redis_commands 
            WHERE {' AND '.join(shard_where) if shard_where else '1=1'}
            GROUP BY shard_name
            ORDER BY shard_name
        """
        shards = [row[0] for row in job_db.execute(text(shard_query), shard_params).fetchall()]
        
        # Get matching count with all current filters
        count_query = f"SELECT COUNT(*) FROM redis_commands WHERE {where_sql}"
        matching_count = job_db.execute(text(count_query), params).scalar()
        
        return JSONResponse({
            "commands": commands,
            "patterns": patterns,
            "signatures": signatures,
            "shards": shards,
            "matching_count": matching_count
        })


# ============================================================================
# SHORT URL SHARING SYSTEM
# ============================================================================

def generate_short_id(length: int = 7) -> str:
    """Generate a short alphanumeric ID for URLs."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


@app.post("/api/short-urls")
async def create_short_url(request: Request, db: Session = Depends(get_db)):
    """Create a short URL for sharing page state.
    
    Request body: { "full_url": "/jobs/123/timeline?group_by=command" }
    Response: { "short_url": "/s/Ab3kP9", "full_url": "...", "is_new": true }
    """
    try:
        body = await request.json()
        full_url = body.get("full_url", "").strip()
        
        if not full_url:
            return JSONResponse({"error": "full_url is required"}, status_code=400)
        
        # Validate URL starts with /
        if not full_url.startswith("/"):
            return JSONResponse({"error": "full_url must start with /"}, status_code=400)
        
        # Check if this URL already exists (deduplication)
        existing = db.query(ShortUrl).filter(ShortUrl.full_url == full_url).first()
        if existing:
            return JSONResponse({
                "short_url": f"/s/{existing.id}",
                "full_url": existing.full_url,
                "is_new": False
            })
        
        # Generate unique short ID
        for _ in range(10):  # Max attempts
            short_id = generate_short_id()
            if not db.query(ShortUrl).filter(ShortUrl.id == short_id).first():
                break
        else:
            return JSONResponse({"error": "Could not generate unique short URL"}, status_code=500)
        
        # Create new short URL
        short_url = ShortUrl(
            id=short_id,
            full_url=full_url,
            created_at=datetime.utcnow(),
            hit_count=0
        )
        db.add(short_url)
        db.commit()
        
        logger.info(f"Created short URL: /s/{short_id} -> {full_url}")
        
        return JSONResponse({
            "short_url": f"/s/{short_id}",
            "full_url": full_url,
            "is_new": True
        })
        
    except Exception as e:
        logger.error(f"Error creating short URL: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/s/{short_id}")
async def redirect_short_url(short_id: str, db: Session = Depends(get_db)):
    """Redirect from short URL to full URL."""
    short_url = db.query(ShortUrl).filter(ShortUrl.id == short_id).first()
    
    if not short_url:
        return HTMLResponse(
            content="<h1>404 - Short URL Not Found</h1><p>This link may have expired or never existed.</p>",
            status_code=404
        )
    
    # Increment hit count
    short_url.hit_count = (short_url.hit_count or 0) + 1
    db.commit()
    
    return RedirectResponse(url=short_url.full_url, status_code=302)


# ============================================================================
# STATIC FILES (JS, CSS)
# ============================================================================

# Mount static files directory
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
