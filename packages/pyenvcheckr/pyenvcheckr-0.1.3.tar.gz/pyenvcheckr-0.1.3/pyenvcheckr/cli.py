import argparse
from pathlib import Path
from .checker import run_checks
from .version import __version__

def main():
    parser = argparse.ArgumentParser(
        description="Check Python environment and validate dependencies",
        prog="pyenvcheckr"
    )
    parser.add_argument(
        "-r", "--requirements",
        type=str,
        default="requirements.txt",
        help="Path to requirements.txt file (default: requirements.txt)"
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    
    args = parser.parse_args()
    req_path = Path(args.requirements)
    
    if not req_path.exists():
        print(f"❌ Error: {req_path} not found")
        exit(1)
    
    run_checks(str(req_path))

if __name__ == "__main__":
    main()
