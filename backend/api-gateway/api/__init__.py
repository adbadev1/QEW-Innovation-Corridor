"""
API Routes Module
=================

FastAPI router modules for different API endpoints.
"""

from . import cameras, work_zones, collection, directions, analysis

__all__ = ["cameras", "work_zones", "collection", "directions", "analysis"]
