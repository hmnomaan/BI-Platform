"""
Script to run the BI Platform API Engine.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from api_engine.http_service import main

if __name__ == "__main__":
    print("=" * 60)
    print("BI Platform API Engine")
    print("=" * 60)
    print("\nStarting API server...")
    print("API will be available at: http://localhost:8000")
    print("API docs: http://localhost:8000/docs")
    print("Health check: http://localhost:8000/health")
    print("\nPress Ctrl+C to stop the server\n")
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nServer stopped by user.")
    except Exception as e:
        print(f"\n\nError starting server: {e}")
        sys.exit(1)

