"""
Camera Direction Model
======================

Stores AI-analyzed camera heading/direction data (Corey's work).
"""

from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from database import Base


class CameraDirection(Base):
    """Camera direction analysis database model"""
    __tablename__ = "camera_directions"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign key to camera
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=False, index=True)
    view_id = Column(Integer, nullable=True)

    # Direction analysis
    heading = Column(Float, nullable=False)  # 0-360 degrees (0 = North)
    direction = Column(String(10), nullable=False)  # N, NE, E, SE, S, SW, W, NW
    confidence = Column(String(10), default="medium")  # high, medium, low

    # Alternative headings (for multi-view cameras)
    eastbound_heading = Column(Float, nullable=True)
    westbound_heading = Column(Float, nullable=True)

    # AI analysis metadata
    model = Column(String(50), default="claude-vision")  # claude-vision, gemini-vision
    analysis_method = Column(String(50), default="satellite_comparison")

    # Timestamps
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    camera = relationship("Camera", back_populates="directions")

    # Constraints
    __table_args__ = (
        UniqueConstraint('camera_id', 'view_id', name='unique_camera_view_direction'),
    )

    def __repr__(self):
        return f"<CameraDirection {self.camera_id} - {self.direction} ({self.heading}°)>"

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "camera_id": self.camera_id,
            "view_id": self.view_id,
            "heading": self.heading,
            "direction": self.direction,
            "confidence": self.confidence,
            "eastbound_heading": self.eastbound_heading,
            "westbound_heading": self.westbound_heading,
            "model": self.model,
            "analysis_method": self.analysis_method,
            "analyzed_at": self.analyzed_at.isoformat() if self.analyzed_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
