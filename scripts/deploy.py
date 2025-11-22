# scripts/deploy.py
import subprocess
import sys
from pathlib import Path

def run_command(cmd, check=True):
    """Run shell command and handle errors"""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0 and check:
        print(f"Error: {result.stderr}")
        sys.exit(1)
    
    return result

def deploy_bi_platform():
    """Deploy BI platform"""
    print("Deploying BI Platform...")
    
    # Install dependencies
    run_command("pip install -r requirements/base.txt")
    
    # Run tests
    print("Running tests...")
    run_command("python -m pytest tests/ -v")
    
    # Start dashboard
    print("Starting BI Dashboard...")
    run_command("python bi_dashboard/app.py &")
    
    print("BI Platform deployed successfully!")

if __name__ == "__main__":
    deploy_bi_platform()