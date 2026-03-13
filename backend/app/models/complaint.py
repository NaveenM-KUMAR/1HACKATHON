from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class Complaint(Base):
    __tablename__ = "complaints"

    id            = Column(Integer, primary_key=True, index=True)
    user_id       = Column(Integer, ForeignKey("users.id"), nullable=True)
    image_url     = Column(String, nullable=True)
    description   = Column(String, nullable=True)
    issue_type    = Column(String, nullable=False)     # pothole | garbage | streetlight | water_leak
    latitude      = Column(Float, nullable=True)
    longitude     = Column(Float, nullable=True)
    priority      = Column(String, default="medium")   # low | medium | high
    ai_confidence = Column(Float, nullable=True)
    status        = Column(String, default="pending")  # pending | in_progress | resolved
    created_at    = Column(DateTime(timezone=True), server_default=func.now())
