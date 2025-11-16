"""
Database module for AI Camera Direction Assessment
Manages camera direction assessments from AI analysis
"""
import sqlite3
from typing import Dict, List, Optional
from datetime import datetime


class DirectionDatabase:
    """Database for storing AI camera direction assessments"""
    
    def __init__(self, db_path: str = 'data/camera_directions.db'):
        """Initialize database connection"""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.create_tables()
    
    def create_tables(self):
        """Create database tables"""
        # AI Direction Assessments table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_direction_assessments (
                assessment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                camera_id INTEGER NOT NULL,
                view_id INTEGER NOT NULL,
                
                -- Camera Information
                location TEXT,
                latitude REAL,
                longitude REAL,
                camera_url TEXT,
                
                -- Image Paths
                satellite_image_path TEXT,
                camera_image_path TEXT,
                
                -- AI Assessment Results
                direction TEXT NOT NULL,
                confidence_score REAL,
                compass_direction_8 TEXT,
                compass_direction_16 TEXT,
                heading_degrees REAL,
                
                -- AI Analysis Details
                landmarks_identified TEXT,
                reasoning TEXT,
                satellite_analysis TEXT,
                camera_analysis TEXT,
                landmark_matches TEXT,
                
                -- Metadata
                assessment_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ai_model TEXT,
                processing_time_seconds REAL,
                status TEXT DEFAULT 'completed',
                error_message TEXT,
                
                UNIQUE(camera_id, view_id)
            )
        ''')
        
        # Create indexes
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_camera_view 
            ON ai_direction_assessments(camera_id, view_id)
        ''')
        
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_direction 
            ON ai_direction_assessments(direction)
        ''')
        
        self.conn.commit()
    
    def insert_assessment(self, assessment: Dict) -> int:
        """Insert or update AI direction assessment"""
        self.cursor.execute('''
            INSERT OR REPLACE INTO ai_direction_assessments (
                camera_id, view_id, location, latitude, longitude, camera_url,
                satellite_image_path, camera_image_path,
                direction, confidence_score, compass_direction_8, compass_direction_16, heading_degrees,
                landmarks_identified, reasoning, satellite_analysis, camera_analysis, landmark_matches,
                ai_model, processing_time_seconds, status, error_message
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            assessment['camera_id'],
            assessment['view_id'],
            assessment.get('location'),
            assessment.get('latitude'),
            assessment.get('longitude'),
            assessment.get('camera_url'),
            assessment.get('satellite_image_path'),
            assessment.get('camera_image_path'),
            assessment['direction'],
            assessment.get('confidence_score'),
            assessment.get('compass_direction_8'),
            assessment.get('compass_direction_16'),
            assessment.get('heading_degrees'),
            assessment.get('landmarks_identified'),
            assessment.get('reasoning'),
            assessment.get('satellite_analysis'),
            assessment.get('camera_analysis'),
            assessment.get('landmark_matches'),
            assessment.get('ai_model', 'claude-3-5-sonnet-20241022'),
            assessment.get('processing_time_seconds'),
            assessment.get('status', 'completed'),
            assessment.get('error_message')
        ))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_assessment(self, camera_id: int, view_id: int) -> Optional[Dict]:
        """Get assessment for specific camera view"""
        self.cursor.execute('''
            SELECT * FROM ai_direction_assessments
            WHERE camera_id = ? AND view_id = ?
        ''', (camera_id, view_id))
        result = self.cursor.fetchone()
        return dict(result) if result else None
    
    def get_all_assessments(self) -> List[Dict]:
        """Get all assessments"""
        self.cursor.execute('''
            SELECT * FROM ai_direction_assessments
            ORDER BY assessment_timestamp DESC
        ''')
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_assessments_by_direction(self, direction: str) -> List[Dict]:
        """Get all assessments for a specific direction"""
        self.cursor.execute('''
            SELECT * FROM ai_direction_assessments
            WHERE direction = ?
            ORDER BY camera_id, view_id
        ''', (direction,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_pending_cameras(self, source_db_path: str) -> List[Dict]:
        """Get cameras that haven't been assessed yet"""
        # Connect to source database
        source_conn = sqlite3.connect(source_db_path)
        source_conn.row_factory = sqlite3.Row
        source_cursor = source_conn.cursor()
        
        # Get all camera views
        source_cursor.execute('''
            SELECT c.camera_id, c.location, c.latitude, c.longitude,
                   cv.view_id, cv.url, cv.description
            FROM cameras c
            JOIN camera_views cv ON c.camera_id = cv.camera_id
            ORDER BY c.camera_id, cv.view_id
        ''')
        all_cameras = [dict(row) for row in source_cursor.fetchall()]
        source_conn.close()
        
        # Filter out already assessed cameras
        pending = []
        for camera in all_cameras:
            existing = self.get_assessment(camera['camera_id'], camera['view_id'])
            if not existing:
                pending.append(camera)
        
        return pending
    
    def close(self):
        """Close database connection"""
        self.conn.close()

