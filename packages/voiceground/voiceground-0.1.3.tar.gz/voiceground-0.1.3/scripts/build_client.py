#!/usr/bin/env python3
"""Build the React client and copy it to the Python package."""

import shutil
import subprocess
import sys
from pathlib import Path


def main():
    # Get paths
    project_root = Path(__file__).parent.parent
    client_dir = project_root / "client"
    static_dir = project_root / "src" / "voiceground" / "_static"

    print("📦 Building Voiceground client...")

    # Check if npm is available
    try:
        subprocess.run(["npm", "--version"], check=True, capture_output=True)
    except FileNotFoundError:
        print("❌ Error: npm not found. Please install Node.js.")
        sys.exit(1)

    # Install dependencies if node_modules doesn't exist
    node_modules = client_dir / "node_modules"
    if not node_modules.exists():
        print("📥 Installing npm dependencies...")
        subprocess.run(["npm", "install"], cwd=client_dir, check=True)

    # Build the client
    print("🔨 Building React client...")
    subprocess.run(["npm", "run", "build"], cwd=client_dir, check=True)

    # Copy the bundled HTML to the static directory
    dist_html = client_dir / "dist" / "index.html"
    static_html = static_dir / "index.html"

    if not dist_html.exists():
        print("❌ Error: Build output not found at", dist_html)
        sys.exit(1)

    # Ensure static directory exists
    static_dir.mkdir(parents=True, exist_ok=True)

    # Copy the file
    shutil.copy(dist_html, static_html)
    print(f"✅ Copied bundled client to {static_html}")

    # Get file size
    size_kb = static_html.stat().st_size / 1024
    print(f"📊 Bundle size: {size_kb:.1f} KB")

    print("✨ Build complete!")


if __name__ == "__main__":
    main()
