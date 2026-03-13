from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class ComplaintOut(BaseModel):
    id: int
    user_id: Optional[int]
    image_url: Optional[str]
    description: Optional[str]
    issue_type: str
    latitude: Optional[float]
    longitude: Optional[float]
    priority: Optional[str]
    ai_confidence: Optional[float]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class ComplaintStatusUpdate(BaseModel):
    status: str   # pending | in_progress | resolved


class AIDetectionInput(BaseModel):
    image_url: Optional[str] = None
    detected_issue: str
    confidence: float
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    description: Optional[str] = None
