"""
Collection Run Model
====================

Represents a camera image collection session.
"""

from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from datetime import datetime

from database import Base


class CollectionRun(Base):
    """Camera image collection run database model"""
    __tablename__ = "collection_runs"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Collection identifier
    collection_id = Column(String(100), unique=True, nullable=False, index=True)

    # Status tracking
    status = Column(String(20), default="in_progress")  # in_progress, completed, failed

    # Statistics
    total_cameras = Column(Integer, default=0)
    images_collected = Column(Integer, default=0)
    images_analyzed = Column(Integer, default=0)
    work_zones_detected = Column(Integer, default=0)
    errors = Column(Integer, default=0)

    # Detailed results
    results = Column(JSON, nullable=True)  # Detailed collection results
    error_log = Column(JSON, nullable=True)  # Array of error messages

    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Integer, nullable=True)

    def __repr__(self):
        return f"<CollectionRun {self.collection_id} - {self.status}>"

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "collection_id": self.collection_id,
            "status": self.status,
            "total_cameras": self.total_cameras,
            "images_collected": self.images_collected,
            "images_analyzed": self.images_analyzed,
            "work_zones_detected": self.work_zones_detected,
            "errors": self.errors,
            "results": self.results,
            "error_log": self.error_log,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.duration_seconds
        }
