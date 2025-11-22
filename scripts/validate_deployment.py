"""
Validation script to check BI Platform deployment.
"""
import sys
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.8+."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required. Current version:", sys.version)
        return False
    print(f"✓ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def check_imports():
    """Check if all required modules can be imported."""
    modules = [
        ("pandas", "pandas"),
        ("plotly", "plotly"),
        ("dash", "dash"),
        ("dash_bootstrap_components", "dash-bootstrap-components"),
        ("dash_table", "dash-table"),
        ("sqlalchemy", "sqlalchemy"),
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
    ]
    
    failed = []
    for module_name, package_name in modules:
        try:
            __import__(module_name)
            print(f"✓ {package_name}")
        except ImportError:
            print(f"❌ {package_name} not installed")
            failed.append(package_name)
    
    return len(failed) == 0

def check_project_structure():
    """Check if project structure is correct."""
    required_dirs = [
        "api_engine",
        "bi_dashboard",
        "configs",
        "scripts",
    ]
    
    required_files = [
        "setup.py",
        "run_app.py",
        "requirements/base.txt",
    ]
    
    all_ok = True
    
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            print(f"✓ Directory: {dir_name}/")
        else:
            print(f"❌ Missing directory: {dir_name}/")
            all_ok = False
    
    for file_name in required_files:
        if Path(file_name).exists():
            print(f"✓ File: {file_name}")
        else:
            print(f"❌ Missing file: {file_name}")
            all_ok = False
    
    return all_ok

def check_config_files():
    """Check if configuration files exist."""
    config_files = [
        "configs/shared_config.yaml",
        "configs/dev/api_config.yaml",
        "configs/dev/bi_config.yaml",
    ]
    
    all_ok = True
    for config_file in config_files:
        if Path(config_file).exists():
            print(f"✓ Config: {config_file}")
        else:
            print(f"⚠️  Config file not found: {config_file} (optional)")
    
    return True

def check_directories():
    """Check if required directories exist, create if missing."""
    directories = ["logs", "data"]
    
    for dir_name in directories:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"✓ Directory exists: {dir_name}/")
        else:
            dir_path.mkdir(exist_ok=True)
            print(f"✓ Created directory: {dir_name}/")
    
    return True

def check_sample_data():
    """Check if sample data files exist."""
    data_files = [
        "data/sales_data.csv",
        "data/employee_data.csv",
        "data/time_series_data.csv",
    ]
    
    found = 0
    for data_file in data_files:
        if Path(data_file).exists():
            print(f"✓ Sample data: {data_file}")
            found += 1
        else:
            print(f"⚠️  Sample data not found: {data_file}")
    
    if found == 0:
        print("⚠️  No sample data found. Run: python scripts/create_sample_data.py")
    
    return True

def test_imports():
    """Test importing main modules."""
    try:
        from bi_dashboard import app
        print("✓ BI Dashboard module imports successfully")
    except Exception as e:
        print(f"❌ BI Dashboard import failed: {e}")
        return False
    
    try:
        from api_engine.core.api_engine import APIEngine
        print("✓ API Engine module imports successfully")
    except Exception as e:
        print(f"❌ API Engine import failed: {e}")
        return False
    
    return True

def main():
    """Run all validation checks."""
    print("=" * 60)
    print("BI Platform - Deployment Validation")
    print("=" * 60)
    print()
    
    checks = [
        ("Python Version", check_python_version),
        ("Project Structure", check_project_structure),
        ("Required Imports", check_imports),
        ("Configuration Files", check_config_files),
        ("Directories", check_directories),
        ("Sample Data", check_sample_data),
        ("Module Imports", test_imports),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n{name}:")
        print("-" * 40)
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Error during {name} check: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("Validation Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n✅ All checks passed! Deployment is ready.")
        return 0
    else:
        print("\n⚠️  Some checks failed. Please review the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

