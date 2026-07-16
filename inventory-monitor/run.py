#!/usr/bin/env python3
"""Convenience launcher so you can `python run.py` from this folder."""

import sys

from monitor.cli import main

if __name__ == "__main__":
    sys.exit(main())
