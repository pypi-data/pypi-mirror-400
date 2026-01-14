#!/usr/bin/env python3
"""
License key generation tool for Jupyters.

Usage:
    python generate_license.py PRO user@example.com
    python generate_license.py TEAM company-id-123
"""

import sys
import hashlib
from context_engine.license_validator import generate_license_key


def generate_unique_id(identifier: str) -> str:
    """
    Generate unique ID from email or company ID.

    Args:
        identifier: Email address or company identifier

    Returns:
        9-character uppercase alphanumeric ID
    """
    # Hash the identifier
    hash_obj = hashlib.sha256(identifier.lower().encode())
    hash_hex = hash_obj.hexdigest()

    # Take first 9 characters and uppercase
    return hash_hex[:9].upper()


def main():
    if len(sys.argv) != 3:
        print("Usage: python generate_license.py <TIER> <identifier>")
        print()
        print("Examples:")
        print("  python generate_license.py PRO user@example.com")
        print("  python generate_license.py TEAM company-xyz")
        print()
        print("TIER: PRO or TEAM")
        print("identifier: Email address or company ID")
        sys.exit(1)

    tier = sys.argv[1].upper()
    identifier = sys.argv[2]

    if tier not in ["PRO", "TEAM"]:
        print(f"Error: Invalid tier '{tier}'. Must be PRO or TEAM.")
        sys.exit(1)

    # Generate unique ID
    unique_id = generate_unique_id(identifier)

    # Generate license key
    license_key = generate_license_key(tier, unique_id)

    print("=" * 60)
    print("LICENSE KEY GENERATED")
    print("=" * 60)
    print(f"Tier:       {tier}")
    print(f"Identifier: {identifier}")
    print(f"Unique ID:  {unique_id}")
    print()
    print(f"LICENSE KEY: {license_key}")
    print("=" * 60)
    print()
    print("Send this key to the customer:")
    print(f"  {license_key}")
    print()
    print("Customer activation:")
    print(f"  Ask AI: \"Activate my Jupyters license: {license_key}\"")
    print()


if __name__ == "__main__":
    main()
