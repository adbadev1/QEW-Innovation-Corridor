"""
Start the FastAPI backend server
"""
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi_backend.main import start_server

if __name__ == "__main__":
    print("=" * 80)
    print("QEW Innovation Corridor - FastAPI Backend")
    print("=" * 80)
    print("\nStarting server...")
    print("API will be available at: http://localhost:8000")
    print("API documentation at: http://localhost:8000/docs")
    print("\nPress CTRL+C to stop the server\n")
    print("=" * 80)
    
    start_server()

