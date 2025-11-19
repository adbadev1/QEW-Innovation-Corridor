"""
Backend Manager
Handles auto-starting and monitoring the FastAPI backend server
"""
import subprocess
import time
import requests
import sys
from pathlib import Path
from typing import Optional


class BackendManager:
    """Manages the FastAPI backend server lifecycle"""
    
    def __init__(self, host: str = "localhost", port: int = 8000):
        """
        Initialize backend manager
        
        Args:
            host: Backend host
            port: Backend port
        """
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.process: Optional[subprocess.Popen] = None
        self.project_root = Path(__file__).parent.parent
    
    def is_backend_running(self) -> bool:
        """
        Check if backend is already running
        
        Returns:
            True if backend is responding, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/health", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def start_backend(self, wait_time: int = 5) -> bool:
        """
        Start the FastAPI backend server
        
        Args:
            wait_time: Seconds to wait for backend to start
            
        Returns:
            True if backend started successfully, False otherwise
        """
        # Check if already running
        if self.is_backend_running():
            print(f"✓ Backend already running at {self.base_url}")
            return True
        
        print(f"Starting FastAPI backend at {self.base_url}...")
        
        # Get path to venv python
        if sys.platform == "win32":
            python_exe = self.project_root / "venv" / "Scripts" / "python.exe"
        else:
            python_exe = self.project_root / "venv" / "bin" / "python"
        
        # Get path to start script
        start_script = self.project_root / "start_backend.py"
        
        if not python_exe.exists():
            print(f"❌ Virtual environment not found at {python_exe}")
            print("Please run: python -m venv venv")
            return False
        
        if not start_script.exists():
            print(f"❌ Start script not found at {start_script}")
            return False
        
        try:
            # Start backend process (hidden window on Windows)
            if sys.platform == "win32":
                # CREATE_NO_WINDOW = 0x08000000 - prevents console window from appearing
                creationflags = 0x08000000
            else:
                creationflags = 0

            self.process = subprocess.Popen(
                [str(python_exe), str(start_script)],
                cwd=str(self.project_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=creationflags
            )
            
            # Wait for backend to start
            print(f"Waiting {wait_time} seconds for backend to start...")
            for i in range(wait_time * 2):  # Check every 0.5 seconds
                time.sleep(0.5)
                if self.is_backend_running():
                    print(f"✓ Backend started successfully at {self.base_url}")
                    return True
            
            print(f"⚠ Backend may still be starting. Check {self.base_url}/docs")
            return True  # Return True anyway, it might just need more time
            
        except Exception as e:
            print(f"❌ Failed to start backend: {e}")
            return False
    
    def stop_backend(self):
        """Stop the backend server"""
        if self.process:
            print("Stopping backend server...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
                print("✓ Backend stopped")
            except subprocess.TimeoutExpired:
                print("⚠ Backend did not stop gracefully, killing...")
                self.process.kill()
            self.process = None
    
    def get_api_url(self, endpoint: str) -> str:
        """
        Get full URL for an API endpoint
        
        Args:
            endpoint: API endpoint path (e.g., '/api/cameras/latest')
            
        Returns:
            Full URL
        """
        if not endpoint.startswith('/'):
            endpoint = '/' + endpoint
        return f"{self.base_url}{endpoint}"
    
    def __del__(self):
        """Cleanup on deletion"""
        # Don't stop backend on deletion - let it keep running
        # User can manually stop it or it will stop when terminal closes
        pass

