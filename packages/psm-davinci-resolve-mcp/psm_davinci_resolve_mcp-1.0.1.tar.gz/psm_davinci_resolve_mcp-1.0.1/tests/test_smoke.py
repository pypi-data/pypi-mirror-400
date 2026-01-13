#!/usr/bin/env python3
"""Smoke test - verifies the package can be imported."""

import sys


def test():
    print("Running smoke test...")

    # Test 1: Package can be imported
    try:
        import psm_davinci_resolve_mcp
        print(f"✓ Package imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import package: {e}")
        sys.exit(1)

    print("All smoke tests passed!")


if __name__ == "__main__":
    test()
