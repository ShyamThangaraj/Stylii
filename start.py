#!/usr/bin/env python3
"""
Start script for Nano Banana Hackathon
This script starts both the FastAPI backend and Next.js frontend
"""

import subprocess
import sys
import time
import signal
import os
from pathlib import Path

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n🛑 Stopping servers...")
    for process in processes:
        if process.poll() is None:  # Process is still running
            process.terminate()
    sys.exit(0)

def main():
    """Main function to start both servers"""
    print("🚀 Starting Nano Banana Hackathon servers...")
    
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    processes = []
    
    try:
        # Start FastAPI backend
        print("📡 Starting FastAPI backend on http://localhost:8000")
        backend_cmd = [
            sys.executable, "main.py"
        ]
        backend_process = subprocess.Popen(
            backend_cmd,
            cwd=Path(__file__).parent / "backend",
            env={**os.environ, "PATH": str(Path(__file__).parent / "backend" / "venv" / "bin") + ":" + os.environ.get("PATH", "")}
        )
        processes.append(backend_process)
        
        # Wait a moment for backend to start
        time.sleep(2)
        
        # Start Next.js frontend
        print("🎨 Starting Next.js frontend on http://localhost:3000")
        frontend_cmd = ["npm", "run", "dev"]
        frontend_process = subprocess.Popen(
            frontend_cmd,
            cwd=Path(__file__).parent / "frontend"
        )
        processes.append(frontend_process)
        
        print("✅ Both servers are starting up!")
        print("   Backend:  http://localhost:8000")
        print("   Frontend: http://localhost:3000")
        print("   API Docs: http://localhost:8000/docs")
        print("")
        print("Press Ctrl+C to stop both servers")
        
        # Wait for processes
        for process in processes:
            process.wait()
            
    except KeyboardInterrupt:
        signal_handler(None, None)
    except Exception as e:
        print(f"❌ Error starting servers: {e}")
        signal_handler(None, None)

if __name__ == "__main__":
    main()

