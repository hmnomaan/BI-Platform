"""
Script to run both BI Dashboard and API Engine servers simultaneously.
"""
import subprocess
import sys
import time
import os
from pathlib import Path

def run_command_in_background(cmd, name):
    """Run a command in the background."""
    try:
        if sys.platform == "win32":
            # Windows
            process = subprocess.Popen(
                cmd,
                shell=True,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            # Linux/Mac
            process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        print(f"✓ Started {name} (PID: {process.pid})")
        return process
    except Exception as e:
        print(f"✗ Failed to start {name}: {e}")
        return None

def main():
    """Run both servers."""
    print("=" * 60)
    print("BI Platform - Starting Both Servers")
    print("=" * 60)
    print()
    
    # Get the project root
    project_root = Path(__file__).parent
    
    # Start API server
    print("Starting API Engine server...")
    api_cmd = f'cd "{project_root}" && python run_api.py'
    api_process = run_command_in_background(api_cmd, "API Engine")
    
    if api_process:
        print("  → API will be available at: http://localhost:8000")
        print("  → API docs: http://localhost:8000/docs")
    else:
        print("  ⚠ Warning: API server failed to start")
    
    print()
    
    # Wait a moment for API to start
    time.sleep(2)
    
    # Start Dashboard server
    print("Starting BI Dashboard server...")
    dashboard_cmd = f'cd "{project_root}" && python run_app.py'
    dashboard_process = run_command_in_background(dashboard_cmd, "BI Dashboard")
    
    if dashboard_process:
        print("  → Dashboard will be available at: http://127.0.0.1:8050")
    else:
        print("  ⚠ Warning: Dashboard server failed to start")
    
    print()
    print("=" * 60)
    print("Both servers are starting...")
    print("=" * 60)
    print()
    print("Access Points:")
    print("  - BI Dashboard: http://127.0.0.1:8050")
    print("  - API Engine:   http://localhost:8000")
    print("  - API Docs:     http://localhost:8000/docs")
    print()
    print("Press Ctrl+C to stop both servers")
    print()
    
    try:
        # Wait for processes
        if api_process:
            api_process.wait()
        if dashboard_process:
            dashboard_process.wait()
    except KeyboardInterrupt:
        print()
        print("Stopping servers...")
        if api_process:
            api_process.terminate()
        if dashboard_process:
            dashboard_process.terminate()
        print("Servers stopped.")
        sys.exit(0)

if __name__ == "__main__":
    main()

