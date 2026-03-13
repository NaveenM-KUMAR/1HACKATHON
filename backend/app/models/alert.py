from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id         = Column(Integer, primary_key=True, index=True)
    location   = Column(String, nullable=True)
    severity   = Column(String, default="medium")   # low | medium | high | sos
    latitude   = Column(Float, nullable=True)
    longitude  = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
