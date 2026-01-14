#!/usr/bin/env python3
"""Development script for Voiceground.

Commands:
    build   - Build the React client and copy to Python package
    watch   - Run Vite dev server for client development
    example - Run the example pipeline with HTMLReporter
"""

import argparse
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
CLIENT_DIR = PROJECT_ROOT / "client"
EXAMPLES_DIR = PROJECT_ROOT / "examples"


def cmd_build():
    """Build the React client and copy to Python package."""
    from build_client import main as build_main

    build_main()


def cmd_watch():
    """Run Vite dev server for client development."""
    print("🚀 Starting Vite dev server...")
    print("   Open http://localhost:5173 in your browser")
    print("   Press Ctrl+C to stop\n")

    try:
        subprocess.run(["npm", "run", "dev"], cwd=CLIENT_DIR, check=True)
    except KeyboardInterrupt:
        print("\n👋 Dev server stopped")


def cmd_example():
    """Run the example pipeline with HTMLReporter."""
    example_file = EXAMPLES_DIR / "basic_pipeline.py"

    if not example_file.exists():
        print(f"❌ Example file not found: {example_file}")
        sys.exit(1)

    print("🎙️ Running example pipeline...")
    subprocess.run([sys.executable, str(example_file)], check=True)


def main():
    parser = argparse.ArgumentParser(
        description="Voiceground development tools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("build", help="Build the React client")
    subparsers.add_parser("watch", help="Run Vite dev server")
    subparsers.add_parser("example", help="Run example pipeline")

    args = parser.parse_args()

    if args.command == "build":
        cmd_build()
    elif args.command == "watch":
        cmd_watch()
    elif args.command == "example":
        cmd_example()


if __name__ == "__main__":
    main()
