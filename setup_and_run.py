"""
Setup script to install dependencies and run the BI Platform.
"""
import subprocess
import sys
from pathlib import Path

def run_command(cmd, description, optional=False):
    """Run a command and handle errors."""
    print(f"\n{description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        if optional:
            print(f"⚠️  {description} failed (optional dependency):")
            print(e.stderr[:500])  # Limit error output
            print("Continuing without this optional dependency...")
            return True  # Don't fail for optional dependencies
        else:
            print(f"✗ {description} failed:")
            print(e.stderr[:500])  # Limit error output
            return False

def main():
    """Main setup function."""
    print("=" * 60)
    print("BI Platform - Setup and Run Script")
    print("=" * 60)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"Python version: {sys.version}")
    
    # Upgrade pip first
    print("\nUpgrading pip...")
    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                   capture_output=True)
    
    # Install base requirements
    if not run_command(
        f"{sys.executable} -m pip install -r requirements/base.txt",
        "Installing base requirements"
    ):
        print("\nWarning: Some dependencies may not have installed correctly.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Install BI requirements
    if not run_command(
        f"{sys.executable} -m pip install -r requirements/bi.txt",
        "Installing BI Dashboard requirements"
    ):
        print("\nWarning: Some BI dependencies may not have installed correctly.")
    
    # Install optional database dependencies
    db_req_file = Path("requirements/database.txt")
    if db_req_file.exists():
        print("\n" + "=" * 60)
        print("Optional: Database Dependencies")
        print("=" * 60)
        print("The platform can work without database drivers if you only use")
        print("CSV/Excel files or REST APIs. Database drivers are optional.")
        response = input("\nInstall database drivers (PostgreSQL/MySQL)? (y/n): ")
        if response.lower() == 'y':
            run_command(
                f"{sys.executable} -m pip install -r requirements/database.txt",
                "Installing database drivers",
                optional=True
            )
        else:
            print("Skipping database drivers. You can install them later if needed.")
    
    # Create sample data
    if Path("scripts/create_sample_data.py").exists():
        print("\nCreating sample data files...")
        run_command(
            f"{sys.executable} scripts/create_sample_data.py",
            "Creating sample data"
        )
    
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)
    
    print("\n" + "=" * 60)
    print("Setup complete!")
    print("=" * 60)
    print("\nTo run the dashboard:")
    print("  python run_app.py")
    print("\nOr:")
    print("  python -m bi_dashboard.app")
    print("\nThe dashboard will be available at: http://127.0.0.1:8050")
    print("\n" + "=" * 60)
    
    # Ask if user wants to run now
    response = input("\nWould you like to start the dashboard now? (y/n): ")
    if response.lower() == 'y':
        print("\nStarting dashboard...")
        print("Open your browser to: http://127.0.0.1:8050")
        print("Press Ctrl+C to stop the server\n")
        try:
            from bi_dashboard.app import run_server
            run_server(debug=True)
        except KeyboardInterrupt:
            print("\n\nServer stopped.")
        except Exception as e:
            print(f"\n\nError: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()

