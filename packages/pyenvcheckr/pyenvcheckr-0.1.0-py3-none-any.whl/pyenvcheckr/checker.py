import platform
import sys
from importlib.metadata import version, PackageNotFoundError

def read_requirements(path):
    """Read requirements from a file, ignoring comments and blank lines.
    
    Args:
        path: Path to requirements file (string or Path object)
    
    Returns:
        List of requirement strings
    """
    reqs = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                reqs.append(line)
    return reqs

def check_python():
    """Display Python version information."""
    print("🐍 Python Version:")
    print(f"  {sys.version.split()[0]}")

def check_os():
    """Display operating system information."""
    print("\n💻 Operating System:")
    print(f"  {platform.system()} {platform.release()}")

def check_dependencies(requirements):
    """Check if all dependencies are installed.
    
    Args:
        requirements: List of requirement strings
    """
    print("\n📦 Dependencies:")
    for req in requirements:
        pkg = req.split("==")[0].split(">=")[0].split("<=")[0].split("!=")[0].split(">")[0].split("<")[0].strip()
        try:
            installed_version = version(pkg)
            print(f"  ✅ {pkg} ({installed_version})")
        except PackageNotFoundError:
            print(f"  ❌ {pkg} (NOT INSTALLED)")

def run_checks(requirements_path):
    """Run all environment checks.
    
    Args:
        requirements_path: Path to requirements.txt file
    """
    print("\n🔍 Environment Check\n" + "-" * 30)
    check_python()
    check_os()

    try:
        requirements = read_requirements(requirements_path)
        if requirements:
            check_dependencies(requirements)
        else:
            print("\n📦 Dependencies:")
            print("  (No dependencies found)")
    except FileNotFoundError:
        print("\n❌ requirements.txt not found")
        print("Please provide a valid path to requirements.txt")