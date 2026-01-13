#!/usr/bin/env python3
"""aidrac-send - Send commands via AIdrac transports"""
import sys
from .main import main as aidrac_main

def main():
    # Inject 'send' command
    sys.argv = ["aidrac", "send"] + sys.argv[1:]
    return aidrac_main()

if __name__ == "__main__":
    sys.exit(main())
