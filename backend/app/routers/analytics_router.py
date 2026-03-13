from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from app.database import get_db
from app.models.complaint import Complaint
from app.models.alert import Alert
from app.models.user import User
from app.utils.security import get_current_user

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard")
def dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return top-level KPI stats for the dashboard."""
    total      = db.query(Complaint).count()
    resolved   = db.query(Complaint).filter(Complaint.status == "resolved").count()
    alerts     = db.query(Alert).count()
    risk_zones = db.query(Alert).filter(Alert.severity == "high").count()

    return {
        "total_complaints": total,
        "resolved_issues":  resolved,
        "active_alerts":    alerts,
        "high_risk_zones":  risk_zones,
    }


@router.get("/types")
def complaint_types(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return complaint counts grouped by issue_type for a Chart.js pie/bar chart."""
    rows = (
        db.query(Complaint.issue_type, func.count(Complaint.id).label("count"))
        .group_by(Complaint.issue_type)
        .all()
    )
    return [{"issue_type": r.issue_type, "count": r.count} for r in rows]


@router.get("/timeline")
def timeline(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return complaint counts grouped by date (last 30 days) for a timeline chart."""
    rows = (
        db.query(
            func.date(Complaint.created_at).label("date"),
            func.count(Complaint.id).label("count"),
        )
        .group_by(func.date(Complaint.created_at))
        .order_by(func.date(Complaint.created_at))
        .all()
    )
    return [{"date": str(r.date), "count": r.count} for r in rows]


@router.get("/locations")
def locations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return complaints grouped by approximate location bucket."""
    complaints = db.query(Complaint).filter(
        Complaint.latitude.isnot(None),
        Complaint.longitude.isnot(None),
    ).all()

    # Group by a coarse 0.05° bucket (~5 km)
    BUCKET = 0.05
    from collections import defaultdict
    buckets = defaultdict(int)
    for c in complaints:
        key = (round(round(c.latitude / BUCKET) * BUCKET, 3),
               round(round(c.longitude / BUCKET) * BUCKET, 3))
        buckets[key] += 1

    return [
        {"latitude": lat, "longitude": lon, "count": cnt}
        for (lat, lon), cnt in sorted(buckets.items(), key=lambda x: -x[1])
    ]
