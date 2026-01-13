#!/usr/bin/env python3
"""aidrac-listen - Listen for AIdrac commands"""
import sys
from .main import main as aidrac_main

def main():
    sys.argv = ["aidrac", "listen"] + sys.argv[1:]
    return aidrac_main()

if __name__ == "__main__":
    sys.exit(main())
