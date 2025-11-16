"""
SQLite database module for QEW camera image collection
Manages camera metadata and image records with short filenames
"""
import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import hashlib


class CameraDatabase:
    """Database manager for camera images and metadata"""
    
    def __init__(self, db_path: str = "camera_data.db"):
        """Initialize database connection"""
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self._connect()
        self._create_tables()
    
    def _connect(self):
        """Connect to SQLite database"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Enable column access by name
        self.cursor = self.conn.cursor()
    
    def _create_tables(self):
        """Create database tables if they don't exist"""
        # Cameras table - stores camera metadata
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS cameras (
                camera_id INTEGER PRIMARY KEY,
                source TEXT,
                source_id TEXT,
                roadway TEXT,
                direction TEXT,
                latitude REAL,
                longitude REAL,
                location TEXT,
                sort_order INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Camera views table - stores view information
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS camera_views (
                view_id INTEGER PRIMARY KEY,
                camera_id INTEGER,
                url TEXT,
                status TEXT,
                description TEXT,
                FOREIGN KEY (camera_id) REFERENCES cameras(camera_id)
            )
        ''')
        
        # Images table - stores image records with short filenames
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                camera_id INTEGER,
                view_id INTEGER,
                location TEXT,
                latitude REAL,
                longitude REAL,
                view_description TEXT,
                capture_round INTEGER,
                timestamp TEXT,
                url TEXT,
                collection_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (camera_id) REFERENCES cameras(camera_id),
                FOREIGN KEY (view_id) REFERENCES camera_views(view_id)
            )
        ''')
        
        # Collections table - stores collection session metadata
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS collections (
                collection_id TEXT PRIMARY KEY,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                total_images INTEGER,
                output_directory TEXT,
                status TEXT
            )
        ''')

        # Camera details table - stores detailed camera orientation and coverage info
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS camera_details (
                detail_id INTEGER PRIMARY KEY AUTOINCREMENT,
                camera_id INTEGER,
                view_id INTEGER,

                -- Compass Direction (16-point)
                compass_direction_16 TEXT,
                compass_direction_8 TEXT,

                -- Exact Heading
                heading_degrees REAL,
                heading_description TEXT,

                -- Vertical Angle (Tilt)
                vertical_angle_degrees REAL,
                vertical_angle_label TEXT,
                vertical_angle_description TEXT,

                -- Altitude Information
                height_above_ground_meters REAL,
                height_above_ground_feet REAL,
                altitude_above_sea_level_meters REAL,
                altitude_above_sea_level_feet REAL,
                ground_altitude_meters REAL,
                ground_altitude_feet REAL,
                mount_type TEXT,
                mount_description TEXT,

                -- Coverage Details
                view_distance_meters REAL,
                view_distance_feet REAL,
                effective_range_meters REAL,
                effective_range_feet REAL,
                field_of_view_degrees REAL,
                field_of_view_horizontal REAL,
                field_of_view_vertical REAL,
                coverage_area_polygon TEXT,

                -- Metadata
                data_source TEXT,
                confidence_level TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,

                FOREIGN KEY (camera_id) REFERENCES cameras(camera_id),
                FOREIGN KEY (view_id) REFERENCES camera_views(view_id),
                UNIQUE(camera_id, view_id)
            )
        ''')

        # Create indexes for faster queries
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_images_camera_id
            ON images(camera_id)
        ''')
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_images_collection_id
            ON images(collection_id)
        ''')
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_camera_details_camera_id
            ON camera_details(camera_id)
        ''')
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_camera_details_view_id
            ON camera_details(view_id)
        ''')
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_images_timestamp 
            ON images(timestamp)
        ''')
        
        self.conn.commit()
    
    def insert_camera(self, camera_data: Dict) -> int:
        """Insert or update camera metadata"""
        self.cursor.execute('''
            INSERT OR REPLACE INTO cameras 
            (camera_id, source, source_id, roadway, direction, latitude, longitude, location, sort_order)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            camera_data.get('Id'),
            camera_data.get('Source'),
            camera_data.get('SourceId'),
            camera_data.get('Roadway'),
            camera_data.get('Direction'),
            camera_data.get('Latitude'),
            camera_data.get('Longitude'),
            camera_data.get('Location'),
            camera_data.get('SortOrder')
        ))
        self.conn.commit()
        return camera_data.get('Id')
    
    def insert_camera_view(self, camera_id: int, view_data: Dict):
        """Insert or update camera view"""
        self.cursor.execute('''
            INSERT OR REPLACE INTO camera_views 
            (view_id, camera_id, url, status, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            view_data.get('Id'),
            camera_id,
            view_data.get('Url'),
            view_data.get('Status'),
            view_data.get('Description')
        ))
        self.conn.commit()
    
    def insert_image(self, image_data: Dict) -> int:
        """Insert image record and return the image ID"""
        self.cursor.execute('''
            INSERT INTO images 
            (filename, camera_id, view_id, location, latitude, longitude, 
             view_description, capture_round, timestamp, url, collection_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            image_data.get('filename'),
            image_data.get('camera_id'),
            image_data.get('view_id'),
            image_data.get('location'),
            image_data.get('latitude'),
            image_data.get('longitude'),
            image_data.get('view_description'),
            image_data.get('capture_round'),
            image_data.get('timestamp'),
            image_data.get('url'),
            image_data.get('collection_id')
        ))
        self.conn.commit()
        return self.cursor.lastrowid

    def create_collection(self, collection_id: str, output_directory: str) -> str:
        """Create a new collection record"""
        self.cursor.execute('''
            INSERT INTO collections
            (collection_id, start_time, output_directory, status)
            VALUES (?, ?, ?, ?)
        ''', (collection_id, datetime.now(), output_directory, 'in_progress'))
        self.conn.commit()
        return collection_id

    def complete_collection(self, collection_id: str, total_images: int):
        """Mark collection as complete"""
        self.cursor.execute('''
            UPDATE collections
            SET end_time = ?, total_images = ?, status = ?
            WHERE collection_id = ?
        ''', (datetime.now(), total_images, 'completed', collection_id))
        self.conn.commit()

    def get_camera_by_id(self, camera_id: int) -> Optional[Dict]:
        """Get camera metadata by ID"""
        self.cursor.execute('SELECT * FROM cameras WHERE camera_id = ?', (camera_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def get_all_cameras(self) -> List[Dict]:
        """Get all cameras"""
        self.cursor.execute('SELECT * FROM cameras ORDER BY camera_id')
        return [dict(row) for row in self.cursor.fetchall()]

    def get_camera_views(self, camera_id: int) -> List[Dict]:
        """Get all views for a camera"""
        self.cursor.execute('SELECT * FROM camera_views WHERE camera_id = ?', (camera_id,))
        return [dict(row) for row in self.cursor.fetchall()]

    def get_images_by_collection(self, collection_id: str) -> List[Dict]:
        """Get all images for a collection"""
        self.cursor.execute('SELECT * FROM images WHERE collection_id = ?', (collection_id,))
        return [dict(row) for row in self.cursor.fetchall()]

    def get_images_by_camera(self, camera_id: int) -> List[Dict]:
        """Get all images for a camera"""
        self.cursor.execute('SELECT * FROM images WHERE camera_id = ?', (camera_id,))
        return [dict(row) for row in self.cursor.fetchall()]

    def get_collection_stats(self, collection_id: str) -> Optional[Dict]:
        """Get statistics for a collection"""
        self.cursor.execute('SELECT * FROM collections WHERE collection_id = ?', (collection_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def get_all_collections(self) -> List[Dict]:
        """Get all collections"""
        self.cursor.execute('SELECT * FROM collections ORDER BY start_time DESC')
        return [dict(row) for row in self.cursor.fetchall()]

    def generate_short_filename(self, camera_id: int, view_id: int,
                               capture_round: int, timestamp: str) -> str:
        """
        Generate a short filename to avoid path length issues
        Format: c{camera_id}_v{view_id}_r{round}_{timestamp}.jpg
        Example: c4_v10_r1_20251115_150317.jpg
        """
        return f"c{camera_id}_v{view_id}_r{capture_round}_{timestamp}.jpg"

    def load_cameras_from_json(self, cameras: List[Dict]):
        """Load camera data from JSON into database"""
        for camera in cameras:
            camera_id = self.insert_camera(camera)
            for view in camera.get('Views', []):
                self.insert_camera_view(camera_id, view)
        self.conn.commit()

    def insert_camera_details(self, details: Dict) -> int:
        """Insert or update camera details"""
        self.cursor.execute('''
            INSERT OR REPLACE INTO camera_details (
                camera_id, view_id,
                compass_direction_16, compass_direction_8,
                heading_degrees, heading_description,
                vertical_angle_degrees, vertical_angle_label, vertical_angle_description,
                height_above_ground_meters, height_above_ground_feet,
                altitude_above_sea_level_meters, altitude_above_sea_level_feet,
                ground_altitude_meters, ground_altitude_feet,
                mount_type, mount_description,
                view_distance_meters, view_distance_feet,
                effective_range_meters, effective_range_feet,
                field_of_view_degrees, field_of_view_horizontal, field_of_view_vertical,
                coverage_area_polygon,
                data_source, confidence_level, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            details.get('camera_id'),
            details.get('view_id'),
            details.get('compass_direction_16'),
            details.get('compass_direction_8'),
            details.get('heading_degrees'),
            details.get('heading_description'),
            details.get('vertical_angle_degrees'),
            details.get('vertical_angle_label'),
            details.get('vertical_angle_description'),
            details.get('height_above_ground_meters'),
            details.get('height_above_ground_feet'),
            details.get('altitude_above_sea_level_meters'),
            details.get('altitude_above_sea_level_feet'),
            details.get('ground_altitude_meters'),
            details.get('ground_altitude_feet'),
            details.get('mount_type'),
            details.get('mount_description'),
            details.get('view_distance_meters'),
            details.get('view_distance_feet'),
            details.get('effective_range_meters'),
            details.get('effective_range_feet'),
            details.get('field_of_view_degrees'),
            details.get('field_of_view_horizontal'),
            details.get('field_of_view_vertical'),
            details.get('coverage_area_polygon'),
            details.get('data_source'),
            details.get('confidence_level'),
            details.get('notes')
        ))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_camera_details(self, camera_id: int, view_id: int = None) -> Optional[Dict]:
        """Get camera details by camera_id and optionally view_id"""
        if view_id:
            self.cursor.execute('''
                SELECT * FROM camera_details
                WHERE camera_id = ? AND view_id = ?
            ''', (camera_id, view_id))
        else:
            self.cursor.execute('''
                SELECT * FROM camera_details
                WHERE camera_id = ?
            ''', (camera_id,))

        result = self.cursor.fetchone()
        return dict(result) if result else None

    def get_all_camera_details(self) -> List[Dict]:
        """Get all camera details"""
        self.cursor.execute('SELECT * FROM camera_details ORDER BY camera_id, view_id')
        return [dict(row) for row in self.cursor.fetchall()]

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

