import os
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.complaint import Complaint
from app.models.alert import Alert
from app.models.user import User
from app.schemas.complaint_schema import ComplaintOut, ComplaintStatusUpdate, AIDetectionInput
from app.utils.security import get_current_user

router = APIRouter(tags=["Complaints"])

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Map frontend issue labels → normalized keys
ISSUE_TYPE_MAP = {
    "pothole": "pothole",
    "garbage": "garbage",
    "streetlight": "streetlight",
    "street light": "streetlight",
    "water leak": "water_leak",
    "water_leak": "water_leak",
}

CLUSTER_RADIUS = 0.05   # ~5 km in degrees
CLUSTER_THRESHOLD = 5   # number of complaints to trigger an auto-alert


def _normalize_issue(raw: str) -> str:
    return ISSUE_TYPE_MAP.get(raw.lower().strip(), raw.lower().strip())


def _auto_alert(db: Session, lat: Optional[float], lon: Optional[float]) -> None:
    """Create a high-severity cluster alert when >= CLUSTER_THRESHOLD complaints are nearby."""
    if lat is None or lon is None:
        return
    nearby = db.query(Complaint).filter(
        Complaint.latitude.isnot(None),
        Complaint.longitude.isnot(None),
        Complaint.latitude.between(lat - CLUSTER_RADIUS, lat + CLUSTER_RADIUS),
        Complaint.longitude.between(lon - CLUSTER_RADIUS, lon + CLUSTER_RADIUS),
    ).count()

    if nearby >= CLUSTER_THRESHOLD:
        # Only create one alert per rough location (debounce)
        existing = db.query(Alert).filter(
            Alert.latitude.between(lat - CLUSTER_RADIUS, lat + CLUSTER_RADIUS),
            Alert.longitude.between(lon - CLUSTER_RADIUS, lon + CLUSTER_RADIUS),
            Alert.severity == "high",
        ).first()
        if not existing:
            alert = Alert(
                location=f"({round(lat, 4)}, {round(lon, 4)})",
                severity="high",
                latitude=lat,
                longitude=lon,
            )
            db.add(alert)
            db.commit()


# ── CREATE COMPLAINT ──────────────────────────────────────────────────────────
@router.post("/complaints/create", response_model=ComplaintOut, status_code=status.HTTP_201_CREATED)
async def create_complaint(
    issue_type:    str           = Form(...),
    description:   Optional[str] = Form(None),
    latitude:      Optional[float] = Form(None),
    longitude:     Optional[float] = Form(None),
    priority:      Optional[str] = Form("medium"),
    ai_confidence: Optional[float] = Form(None),
    image:         Optional[UploadFile] = File(None),
    db:            Session = Depends(get_db),
    current_user:  User = Depends(get_current_user),
):
    image_url = None
    if image and image.filename:
        ext = os.path.splitext(image.filename)[1]
        filename = f"{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as f:
            f.write(await image.read())
        image_url = f"/uploads/{filename}"

    complaint = Complaint(
        user_id=current_user.id,
        image_url=image_url,
        description=description,
        issue_type=_normalize_issue(str(issue_type)),
        latitude=latitude,
        longitude=longitude,
        priority=priority,
        ai_confidence=ai_confidence,
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)

    _auto_alert(db, latitude, longitude)
    return complaint


# ── ALL COMPLAINTS ────────────────────────────────────────────────────────────
@router.get("/complaints/all", response_model=List[ComplaintOut])
def get_all_complaints(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Complaint).order_by(Complaint.created_at.desc()).all()


# ── FEED (recent 20) ──────────────────────────────────────────────────────────
@router.get("/complaints/feed", response_model=List[ComplaintOut])
def get_feed(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Complaint).order_by(Complaint.created_at.desc()).limit(20).all()


# ── UPDATE STATUS ─────────────────────────────────────────────────────────────
@router.put("/complaints/{complaint_id}/status", response_model=ComplaintOut)
def update_status(
    complaint_id: int,
    payload: ComplaintStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    complaint.status = payload.status
    db.commit()
    db.refresh(complaint)
    return complaint


# ── DELETE COMPLAINT ──────────────────────────────────────────────────────────
@router.delete("/complaints/{complaint_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_complaint(
    complaint_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    db.delete(complaint)
    db.commit()


# ── AI DETECTION CONVERTER ────────────────────────────────────────────────────
@router.post("/ai/convert-detection", response_model=ComplaintOut, status_code=status.HTTP_201_CREATED)
def convert_detection(
    payload: AIDetectionInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Convert a TensorFlow.js COCO-SSD detection result into a complaint entry."""
    # Assign priority based on confidence
    if payload.confidence >= 0.85:
        priority = "high"
    elif payload.confidence >= 0.6:
        priority = "medium"
    else:
        priority = "low"

    complaint = Complaint(
        user_id=current_user.id,
        image_url=payload.image_url,
        description=payload.description or f"AI detected: {payload.detected_issue}",
        issue_type=_normalize_issue(payload.detected_issue),
        latitude=payload.latitude,
        longitude=payload.longitude,
        priority=priority,
        ai_confidence=payload.confidence,
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)

    _auto_alert(db, payload.latitude, payload.longitude)
    return complaint
