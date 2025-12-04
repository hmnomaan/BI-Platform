"""
Build script for creating the delivery package.
"""
import subprocess
import sys
from pathlib import Path
import shutil


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n{description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed:")
        print(e.stderr)
        return False


def main():
    """Build the delivery package."""
    print("=" * 60)
    print("BI Platform - Package Build Script")
    print("=" * 60)
    
    # Clean previous builds
    print("\nCleaning previous builds...")
    dist_dir = Path("dist")
    build_dir = Path("build")
    
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    if build_dir.exists():
        shutil.rmtree(build_dir)
    
    # Build source distribution
    if not run_command(
        f"{sys.executable} setup.py sdist",
        "Building source distribution"
    ):
        print("Failed to build source distribution")
        sys.exit(1)
    
    # Build wheel
    if not run_command(
        f"{sys.executable} setup.py bdist_wheel",
        "Building wheel distribution"
    ):
        print("Failed to build wheel")
        sys.exit(1)
    
    # List created files
    print("\n" + "=" * 60)
    print("Package Files Created:")
    print("=" * 60)
    
    if dist_dir.exists():
        for file in dist_dir.iterdir():
            size = file.stat().st_size / 1024  # KB
            print(f"  {file.name} ({size:.2f} KB)")
    
    print("\n" + "=" * 60)
    print("Build Complete!")
    print("=" * 60)
    print("\nPackage files are in the 'dist/' directory.")
    # Attempt to read the version from setup.py to make the install hint accurate
    version_hint = "<package-version>"
    try:
        import re
        setup_py = Path(__file__).parent / "setup.py"
        txt = setup_py.read_text(encoding="utf-8")
        m = re.search(r"version\s*=\s*\"([0-9a-zA-Z.\-_]+)\"", txt)
        if m:
            version_hint = m.group(1)
    except Exception:
        pass

    print("\nTo install:")
    print(f"  pip install dist/bi-platform-{version_hint}.tar.gz")
    print("\nOr for development:")
    print("  pip install -e .")


if __name__ == "__main__":
    main()

