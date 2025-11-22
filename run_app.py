"""
Script to run the BI Platform Dashboard.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from bi_dashboard.app import run_server

if __name__ == "__main__":
    print("=" * 60)
    print("BI Platform Dashboard")
    print("=" * 60)
    print("\nStarting server...")
    print("Open your browser and navigate to: http://127.0.0.1:8050")
    print("\nPress Ctrl+C to stop the server\n")
    
    try:
        run_server(host="127.0.0.1", port=8050, debug=True)
    except KeyboardInterrupt:
        print("\n\nServer stopped by user.")
    except Exception as e:
        print(f"\n\nError starting server: {e}")
        sys.exit(1)

