"""
Database module for AI Camera Direction Assessment
Manages camera direction assessments from AI analysis
"""
import sqlite3
from typing import Dict, List, Optional
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from fastapi_backend.config import DIRECTION_DB_PATH, CAMERA_DB_PATH, BASE_DIR


class DirectionDatabase:
    """Database for storing AI camera direction assessments"""

    def __init__(self, db_path: str = None):
        """Initialize database connection"""
        self.db_path = db_path or DIRECTION_DB_PATH
        self.base_dir = Path(BASE_DIR)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.migrate_schema()

    def migrate_schema(self):
        """Migrate database schema to include new columns"""
        try:
            # Check if columns exist
            self.cursor.execute("PRAGMA table_info(ai_direction_assessments)")
            columns = [info[1] for info in self.cursor.fetchall()]
            
            new_columns = {
                'lanes_detected': 'TEXT',
                'road_features': 'TEXT',
                'lane_counts': 'TEXT'
            }
            
            for col_name, col_type in new_columns.items():
                if col_name not in columns:
                    print(f"Migrating database: Adding column {col_name}...")
                    self.cursor.execute(f"ALTER TABLE ai_direction_assessments ADD COLUMN {col_name} {col_type}")
            
            self.conn.commit()
        except Exception as e:
            print(f"Migration warning: {e}")

    def _to_relative_path(self, absolute_path: str) -> str:
        """Convert absolute path to relative path from BASE_DIR"""
        if not absolute_path:
            return absolute_path
        try:
            abs_path = Path(absolute_path).resolve()
            rel_path = abs_path.relative_to(self.base_dir)
            return str(rel_path).replace('\\', '/')  # Use forward slashes for portability
        except (ValueError, TypeError):
            # If path is not under BASE_DIR or already relative, return as-is
            return str(Path(absolute_path)).replace('\\', '/')

    def _to_absolute_path(self, relative_path: str) -> str:
        """Convert relative path to absolute path"""
        if not relative_path:
            return relative_path
        path = Path(relative_path)
        if path.is_absolute():
            return str(path)
        return str((self.base_dir / path).resolve())

    def _convert_paths_to_absolute(self, data: Dict, path_fields: List[str]) -> Dict:
        """Convert specified path fields in a dict from relative to absolute"""
        result = data.copy()
        for field in path_fields:
            if field in result and result[field]:
                result[field] = self._to_absolute_path(result[field])
        return result
    
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
                
                -- Enhanced AI Assessment
                lanes_detected TEXT,
                road_features TEXT,
                lane_counts TEXT,
                
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
    
    def create_run_table(self, table_name: str):
        """Create a new table for a specific analysis run"""
        # Sanitize table name to prevent SQL injection (basic check)
        if not table_name.isidentifier():
            raise ValueError(f"Invalid table name: {table_name}")

        self.cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {table_name} (
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
                
                -- Enhanced AI Assessment
                lanes_detected TEXT,
                road_features TEXT,
                lane_counts TEXT,
                
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
        self.conn.commit()

    def insert_assessment(self, assessment: Dict, table_name: str = 'ai_direction_assessments') -> int:
        """Insert or update AI direction assessment"""
        # Sanitize table name
        if not table_name.isidentifier():
            raise ValueError(f"Invalid table name: {table_name}")

        # Convert image paths to relative
        satellite_path = assessment.get('satellite_image_path')
        camera_path = assessment.get('camera_image_path')

        if satellite_path:
            satellite_path = self._to_relative_path(satellite_path)
        if camera_path:
            camera_path = self._to_relative_path(camera_path)

        try:
            self.cursor.execute(f'''
                INSERT OR REPLACE INTO {table_name} (
                    camera_id, view_id, location, latitude, longitude, camera_url,
                    satellite_image_path, camera_image_path,
                    direction, confidence_score, compass_direction_8, compass_direction_16, heading_degrees,
                    lanes_detected, road_features, lane_counts,
                    landmarks_identified, reasoning, satellite_analysis, camera_analysis, landmark_matches,
                    ai_model, processing_time_seconds, status, error_message
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                assessment['camera_id'],
                assessment['view_id'],
                assessment.get('location'),
                assessment.get('latitude'),
                assessment.get('longitude'),
                assessment.get('camera_url'),
                satellite_path,
                camera_path,
                assessment['direction'],
                assessment.get('confidence_score'),
                assessment.get('compass_direction_8'),
                assessment.get('compass_direction_16'),
                assessment.get('heading_degrees'),
                assessment.get('lanes_detected'),
                assessment.get('road_features'),
                assessment.get('lane_counts'),
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
        except sqlite3.OperationalError as e:
            if "locked" in str(e):
                # Retry once if locked
                import time
                time.sleep(0.1)
                self.conn.commit()
                return self.cursor.lastrowid
            raise e
    
    def get_assessment(self, camera_id: int, view_id: int) -> Optional[Dict]:
        """Get assessment for specific camera view with absolute paths"""
        self.cursor.execute('''
            SELECT * FROM ai_direction_assessments
            WHERE camera_id = ? AND view_id = ?
        ''', (camera_id, view_id))
        result = self.cursor.fetchone()
        if result:
            assessment = dict(result)
            return self._convert_paths_to_absolute(assessment, ['satellite_image_path', 'camera_image_path'])
        return None

    def get_all_assessments(self) -> List[Dict]:
        """Get all assessments with absolute paths"""
        self.cursor.execute('''
            SELECT * FROM ai_direction_assessments
            ORDER BY assessment_timestamp DESC
        ''')
        assessments = [dict(row) for row in self.cursor.fetchall()]
        return [self._convert_paths_to_absolute(a, ['satellite_image_path', 'camera_image_path']) for a in assessments]

    def get_assessments_by_direction(self, direction: str) -> List[Dict]:
        """Get all assessments for a specific direction with absolute paths"""
        self.cursor.execute('''
            SELECT * FROM ai_direction_assessments
            WHERE direction = ?
            ORDER BY camera_id, view_id
        ''', (direction,))
        assessments = [dict(row) for row in self.cursor.fetchall()]
        return [self._convert_paths_to_absolute(a, ['satellite_image_path', 'camera_image_path']) for a in assessments]
    
    def get_pending_cameras(self, source_db_path: str = None) -> List[Dict]:
        """Get cameras that haven't been assessed yet"""
        # Connect to source database
        if source_db_path is None:
            source_db_path = CAMERA_DB_PATH
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

