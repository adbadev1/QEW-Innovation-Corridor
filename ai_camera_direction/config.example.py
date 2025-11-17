"""
Configuration file template
Copy this to config.py and fill in your API keys
"""

# Claude API Key (Required)
# Get from: https://console.anthropic.com/
CLAUDE_API_KEY = "your-claude-api-key-here"

# Google Maps API Key (Optional - for better satellite images)
# Get from: https://console.cloud.google.com/
GOOGLE_MAPS_API_KEY = ""

# Source Database Path
SOURCE_DB_PATH = "../camera_scraper/camera_data.db"

# Satellite Image Settings
SATELLITE_ZOOM = 18  # Higher = more detail (max 21)
SATELLITE_SIZE = "640x640"

# Processing Settings
MAX_RETRIES = 3
TIMEOUT_SECONDS = 30

