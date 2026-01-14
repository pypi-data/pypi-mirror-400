"""
Command-line interface for DanceIR.
"""
import sys
import argparse


def get_version():
    """Get the package version."""
    try:
        from . import __version__
        return __version__
    except ImportError:
        return "unknown"


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="danceir",
        description="Dance Information Retrieval (DanceIR) Toolbox - A modular toolbox for dance motion analysis, feature extraction, and tempo estimation."
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"danceir {get_version()}"
    )
    
    # For now, just handle --version
    # Can add more commands later
    args = parser.parse_args()
    
    # If no arguments provided, show help
    if len(sys.argv) == 1:
        parser.print_help()


if __name__ == "__main__":
    main()
