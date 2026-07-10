#!/usr/bin/env python3
"""Obsidian Pilot - Entry point for `python -m obsidian_pilot`."""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from main import main

if __name__ == "__main__":
    main()
