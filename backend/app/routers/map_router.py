from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.complaint import Complaint
from app.services.heatmap_service import compute_heatmap

router = APIRouter(prefix="/map", tags=["Map"])

# Leaflet marker colour per issue type
ISSUE_COLORS = {
    "pothole":     "red",
    "garbage":     "yellow",
    "streetlight": "black",
    "water_leak":  "blue",
}


@router.get("/complaints")
def map_complaints(db: Session = Depends(get_db)):
    """Return all complaint coordinates and metadata for Leaflet markers."""
    complaints = db.query(Complaint).filter(
        Complaint.latitude.isnot(None),
        Complaint.longitude.isnot(None),
    ).all()

    return [
        {
            "id":          c.id,
            "latitude":    c.latitude,
            "longitude":   c.longitude,
            "issue_type":  c.issue_type,
            "color":       ISSUE_COLORS.get(c.issue_type, "gray"),
            "description": c.description,
            "priority":    c.priority,
            "status":      c.status,
            "created_at":  c.created_at.isoformat() if c.created_at else None,
        }
        for c in complaints
    ]


@router.get("/heatmap")
def map_heatmap(db: Session = Depends(get_db)):
    """Return clustered complaint coordinates with intensity for a heatmap layer."""
    points = db.query(
        Complaint.latitude, Complaint.longitude
    ).filter(
        Complaint.latitude.isnot(None),
        Complaint.longitude.isnot(None),
    ).all()

    data = [{"latitude": p.latitude, "longitude": p.longitude} for p in points]
    return compute_heatmap(data)
