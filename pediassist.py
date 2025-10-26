#!/usr/bin/env python3
"""
PediAssist - Main entry point for the application
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pediassist.cli import cli

if __name__ == "__main__":
    cli()