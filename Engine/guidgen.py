#!/usr/bin/env python3
"""
guidgen.py — Generate short GUIDs for the Story Engine v3.

Usage:
    python3 guidgen.py              # Generate 1 GUID
    python3 guidgen.py 5            # Generate 5 GUIDs
    python3 guidgen.py 3 ch         # Generate 3 GUIDs with ch- prefix
    python3 guidgen.py 1 bk         # Generate 1 GUID with bk- prefix
    python3 guidgen.py 2 br         # Generate 2 GUIDs with br- prefix

Output: One prefixed GUID per line, e.g.:
    ch-a3f7c1b2
    ch-9e4d0f8a
    ch-b2c5e7d1
"""

import secrets
import sys


def main():
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    prefix = sys.argv[2] if len(sys.argv) > 2 else ""

    for _ in range(count):
        guid = secrets.token_hex(4)
        if prefix:
            print(f"{prefix}-{guid}")
        else:
            print(guid)


if __name__ == "__main__":
    main()
