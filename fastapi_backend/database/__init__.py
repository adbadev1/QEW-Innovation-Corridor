"""
Database module for FastAPI backend
Unified database access for camera data and AI assessments
"""
from .camera_db import CameraDatabase
from .direction_db import DirectionDatabase

__all__ = ['CameraDatabase', 'DirectionDatabase']

