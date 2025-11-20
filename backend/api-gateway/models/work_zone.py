"""
Work Zone Model
===============

Represents a detected work zone from AI analysis.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from database import Base


class WorkZone(Base):
    """Work zone detection database model"""
    __tablename__ = "work_zones"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign key to camera
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=False, index=True)
    view_id = Column(Integer, nullable=True)  # Specific camera view

    # Location (copied from camera for faster queries)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    # Detection details
    risk_score = Column(Integer, nullable=False)  # 1-10
    confidence = Column(Float, nullable=False)  # 0.0-1.0

    # Work zone elements
    workers = Column(Integer, default=0)
    vehicles = Column(Integer, default=0)
    equipment = Column(Integer, default=0)
    barriers = Column(Boolean, default=False)

    # Analysis results
    hazards = Column(JSON, nullable=True)  # Array of hazard strings
    violations = Column(JSON, nullable=True)  # Array of MTO BOOK 7 violations
    recommendations = Column(JSON, nullable=True)  # Array of recommendations

    # MTO BOOK 7 compliance
    mto_book_compliance = Column(Boolean, default=False)

    # Image reference
    gcp_image_url = Column(String(500), nullable=True)
    collection_id = Column(String(100), nullable=True)

    # AI model metadata
    model = Column(String(50), default="gemini-2.0-flash-exp")
    synthetic = Column(Boolean, default=False)  # Test vs real data

    # Status tracking
    status = Column(String(20), default="active")  # active, resolved, archived
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    detected_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    camera = relationship("Camera", back_populates="work_zones")

    def __repr__(self):
        return f"<WorkZone {self.id} - Risk {self.risk_score}/10 at Camera {self.camera_id}>"

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "camera_id": self.camera_id,
            "view_id": self.view_id,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "risk_score": self.risk_score,
            "confidence": self.confidence,
            "workers": self.workers,
            "vehicles": self.vehicles,
            "equipment": self.equipment,
            "barriers": self.barriers,
            "hazards": self.hazards,
            "violations": self.violations,
            "recommendations": self.recommendations,
            "mto_book_compliance": self.mto_book_compliance,
            "gcp_image_url": self.gcp_image_url,
            "collection_id": self.collection_id,
            "model": self.model,
            "synthetic": self.synthetic,
            "status": self.status,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "detected_at": self.detected_at.isoformat() if self.detected_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
