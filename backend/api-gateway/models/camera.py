"""
Camera Model
============

Represents a QEW COMPASS traffic camera.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from database import Base


class Camera(Base):
    """Camera database model"""
    __tablename__ = "cameras"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Camera identifiers
    camera_id = Column(String(50), unique=True, nullable=False, index=True)
    source = Column(String(50), default="511ON")  # COMPASS, 511ON, etc.

    # Location information
    location = Column(String(200), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    elevation = Column(Float, nullable=True)

    # Camera direction (from Corey's AI analysis)
    heading = Column(Float, nullable=True)  # 0-360 degrees
    direction = Column(String(10), nullable=True)  # N, NE, E, SE, S, SW, W, NW
    direction_confidence = Column(String(10), nullable=True)  # high, medium, low

    # Camera metadata
    active = Column(Boolean, default=True)
    views = Column(JSON, nullable=True)  # Array of view objects

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    work_zones = relationship("WorkZone", back_populates="camera")
    directions = relationship("CameraDirection", back_populates="camera")

    def __repr__(self):
        return f"<Camera {self.camera_id} at {self.location}>"

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "camera_id": self.camera_id,
            "source": self.source,
            "location": self.location,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "elevation": self.elevation,
            "heading": self.heading,
            "direction": self.direction,
            "direction_confidence": self.direction_confidence,
            "active": self.active,
            "views": self.views,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
