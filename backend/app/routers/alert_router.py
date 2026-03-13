from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.alert import Alert
from app.models.user import User
from app.utils.security import get_current_user

router = APIRouter(prefix="/alerts", tags=["Alerts"])


class AlertOut(BaseModel):
    id: int
    location: Optional[str]
    severity: str
    latitude: Optional[float]
    longitude: Optional[float]

    class Config:
        from_attributes = True


class SOSPayload(BaseModel):
    latitude: float
    longitude: float
    user_id: Optional[int] = None


@router.get("", response_model=List[AlertOut])
def get_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return all active alerts."""
    return db.query(Alert).order_by(Alert.created_at.desc()).all()


@router.post("/sos", response_model=AlertOut, status_code=status.HTTP_201_CREATED)
def sos_alert(
    payload: SOSPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Store an SOS emergency alert triggered by the user."""
    alert = Alert(
        location=f"SOS @ ({round(payload.latitude, 4)}, {round(payload.longitude, 4)})",
        severity="sos",
        latitude=payload.latitude,
        longitude=payload.longitude,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert
