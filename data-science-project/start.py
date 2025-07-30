#!/usr/bin/env python3
"""
Startup script for the Data Science Analytics Platform
Orchestrates the entire system including ETL pipeline, backend API, and frontend
"""

import os
import sys
import subprocess
import time
import threading
import signal
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataSciencePlatform:
    def __init__(self):
        self.processes = []
        self.running = True
        
        # Get the project root directory
        self.project_root = Path(__file__).parent
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root / "frontend"
        self.etl_dir = self.project_root / "etl"
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info("Received shutdown signal. Stopping all processes...")
        self.running = False
        self.stop_all_processes()
        sys.exit(0)
    
    def run_etl_pipeline(self):
        """Run the ETL pipeline to collect and process data"""
        logger.info("Starting ETL pipeline...")
        
        try:
            # Change to ETL directory and run the pipeline
            os.chdir(self.etl_dir)
            
            # Run the ETL pipeline
            result = subprocess.run([
                sys.executable, "main.py", "--mode", "full"
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info("ETL pipeline completed successfully")
                logger.info(result.stdout)
            else:
                logger.error("ETL pipeline failed")
                logger.error(result.stderr)
                
        except subprocess.TimeoutExpired:
            logger.error("ETL pipeline timed out")
        except Exception as e:
            logger.error(f"Error running ETL pipeline: {e}")
    
    def start_backend(self):
        """Start the FastAPI backend server"""
        logger.info("Starting FastAPI backend...")
        
        try:
            os.chdir(self.backend_dir)
            
            # Install backend dependencies if needed
            if not os.path.exists("venv"):
                logger.info("Creating virtual environment for backend...")
                subprocess.run([sys.executable, "-m", "venv", "venv"])
            
            # Activate virtual environment and install dependencies
            if os.name == 'nt':  # Windows
                pip_path = self.backend_dir / "venv" / "Scripts" / "pip"
                python_path = self.backend_dir / "venv" / "Scripts" / "python"
            else:  # Unix/Linux/Mac
                pip_path = self.backend_dir / "venv" / "bin" / "pip"
                python_path = self.backend_dir / "venv" / "bin" / "python"
            
            # Install requirements
            logger.info("Installing backend dependencies...")
            subprocess.run([str(pip_path), "install", "-r", "requirements.txt"])
            
            # Start the FastAPI server
            logger.info("Starting FastAPI server on http://localhost:8000")
            process = subprocess.Popen([
                str(python_path), "-m", "uvicorn", "main:app", 
                "--host", "0.0.0.0", "--port", "8000", "--reload"
            ])
            
            self.processes.append(("Backend", process))
            
        except Exception as e:
            logger.error(f"Error starting backend: {e}")
    
    def start_frontend(self):
        """Start the React frontend development server"""
        logger.info("Starting React frontend...")
        
        try:
            os.chdir(self.frontend_dir)
            
            # Install frontend dependencies if needed
            if not os.path.exists("node_modules"):
                logger.info("Installing frontend dependencies...")
                subprocess.run(["npm", "install"])
            
            # Start the React development server
            logger.info("Starting React development server on http://localhost:3000")
            process = subprocess.Popen(["npm", "start"])
            
            self.processes.append(("Frontend", process))
            
        except Exception as e:
            logger.error(f"Error starting frontend: {e}")
    
    def wait_for_backend(self):
        """Wait for the backend to be ready"""
        import requests
        
        max_attempts = 30
        attempt = 0
        
        while attempt < max_attempts and self.running:
            try:
                response = requests.get("http://localhost:8000/health", timeout=5)
                if response.status_code == 200:
                    logger.info("Backend is ready!")
                    return True
            except:
                pass
            
            attempt += 1
            time.sleep(2)
            logger.info(f"Waiting for backend... ({attempt}/{max_attempts})")
        
        return False
    
    def stop_all_processes(self):
        """Stop all running processes"""
        for name, process in self.processes:
            try:
                logger.info(f"Stopping {name}...")
                process.terminate()
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                logger.warning(f"Force killing {name}...")
                process.kill()
            except Exception as e:
                logger.error(f"Error stopping {name}: {e}")
    
    def start_platform(self):
        """Start the entire data science platform"""
        logger.info("Starting Data Science Analytics Platform...")
        
        # Step 1: Run ETL pipeline
        self.run_etl_pipeline()
        
        # Step 2: Start backend
        backend_thread = threading.Thread(target=self.start_backend)
        backend_thread.daemon = True
        backend_thread.start()
        
        # Step 3: Wait for backend to be ready
        if not self.wait_for_backend():
            logger.error("Backend failed to start. Stopping platform.")
            self.stop_all_processes()
            return
        
        # Step 4: Start frontend
        frontend_thread = threading.Thread(target=self.start_frontend)
        frontend_thread.daemon = True
        frontend_thread.start()
        
        # Step 5: Keep the main thread alive
        logger.info("Platform is running!")
        logger.info("Backend API: http://localhost:8000")
        logger.info("Frontend: http://localhost:3000")
        logger.info("API Documentation: http://localhost:8000/docs")
        logger.info("Press Ctrl+C to stop the platform")
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        finally:
            self.stop_all_processes()

def main():
    """Main function"""
    platform = DataSciencePlatform()
    platform.start_platform()

if __name__ == "__main__":
    main() 