"""
License validation with remote API support.
"""

import hashlib
import hmac
import json
import time
from typing import Optional, Tuple
from pathlib import Path

# License validation endpoint (you'll deploy this)
VALIDATION_ENDPOINT = "https://api.jupyters.fun/v1/validate"

# Validation cache (avoid hitting API too often)
CACHE_FILE = Path.home() / ".context-engine" / "license_cache.json"
CACHE_VALIDITY = 86400  # 24 hours


def validate_license_offline(key: str) -> Tuple[bool, str, str]:
    """
    Basic offline validation (format check).
    Returns: (is_valid, tier, message)
    """
    if not key or len(key) < 10:
        return False, "free", "Invalid license key format"

    # Check key format: CE-{TIER}-{CHECKSUM}-{UNIQUE}
    parts = key.split("-")
    if len(parts) != 4 or parts[0] != "CE":
        return False, "free", "Invalid license key format"

    tier_code = parts[1]
    tier_map = {
        "PRO": "pro",
        "TEAM": "team",
        "FREE": "free"
    }

    tier = tier_map.get(tier_code, "free")
    if tier == "free":
        return False, "free", "Invalid tier code"

    # Validate checksum (basic verification)
    checksum = parts[2]
    expected = generate_checksum(f"{parts[0]}-{parts[1]}-{parts[3]}")

    if checksum != expected:
        return False, "free", "Invalid license key (checksum mismatch)"

    return True, tier, "License validated (offline)"


def generate_checksum(data: str, secret: str = "jupyters-secret-key") -> str:
    """Generate HMAC checksum for license key."""
    h = hmac.new(secret.encode(), data.encode(), hashlib.sha256)
    return h.hexdigest()[:8].upper()


def validate_license_online(key: str) -> Tuple[bool, str, str]:
    """
    Validate license with remote API.
    Returns: (is_valid, tier, message)

    In production, this would:
    1. Hit your validation API
    2. Check if key is valid, not revoked, not expired
    3. Return tier info

    For now, falls back to offline validation.
    """
    # TODO: Implement actual API call
    # try:
    #     response = requests.post(VALIDATION_ENDPOINT, json={"key": key}, timeout=5)
    #     if response.status_code == 200:
    #         data = response.json()
    #         return data["valid"], data["tier"], data["message"]
    # except Exception as e:
    #     # Fall back to offline validation if API is unreachable
    #     pass

    return validate_license_offline(key)


def get_cached_validation(key: str) -> Optional[Tuple[bool, str, str]]:
    """Get cached validation result if still valid."""
    try:
        if not CACHE_FILE.exists():
            return None

        with open(CACHE_FILE) as f:
            cache = json.load(f)

        key_hash = hashlib.sha256(key.encode()).hexdigest()
        if key_hash in cache:
            entry = cache[key_hash]
            if time.time() - entry["timestamp"] < CACHE_VALIDITY:
                return entry["valid"], entry["tier"], entry["message"]
    except Exception:
        pass

    return None


def cache_validation(key: str, valid: bool, tier: str, message: str):
    """Cache validation result."""
    try:
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)

        cache = {}
        if CACHE_FILE.exists():
            with open(CACHE_FILE) as f:
                cache = json.load(f)

        key_hash = hashlib.sha256(key.encode()).hexdigest()
        cache[key_hash] = {
            "valid": valid,
            "tier": tier,
            "message": message,
            "timestamp": time.time()
        }

        with open(CACHE_FILE, 'w') as f:
            json.dump(cache, f)
    except Exception:
        pass


def validate_license(key: str, use_cache: bool = True) -> Tuple[bool, str, str]:
    """
    Validate a license key.

    Args:
        key: License key (e.g., CE-PRO-ABC12345-XYZ)
        use_cache: Whether to use cached validation results

    Returns:
        (is_valid, tier, message)
    """
    # Check cache first
    if use_cache:
        cached = get_cached_validation(key)
        if cached:
            return cached

    # Try online validation, fall back to offline
    valid, tier, message = validate_license_online(key)

    # Cache result
    if use_cache:
        cache_validation(key, valid, tier, message)

    return valid, tier, message


def generate_license_key(tier: str, unique_id: str, secret: str = "jupyters-secret-key") -> str:
    """
    Generate a license key.

    Args:
        tier: "PRO" or "TEAM"
        unique_id: Unique identifier (e.g., email hash, UUID)
        secret: Secret key for HMAC

    Returns:
        License key in format: CE-{TIER}-{CHECKSUM}-{UNIQUE}

    Example:
        >>> generate_license_key("PRO", "ABC123XYZ")
        'CE-PRO-F4A8B2C1-ABC123XYZ'
    """
    if tier not in ["PRO", "TEAM"]:
        raise ValueError("Tier must be PRO or TEAM")

    # Ensure unique_id is uppercase alphanumeric
    unique_id = unique_id.upper().replace("-", "")[:9]

    # Generate base
    base = f"CE-{tier}-{unique_id}"

    # Calculate checksum
    checksum = generate_checksum(base, secret)

    # Final key
    return f"CE-{tier}-{checksum}-{unique_id}"


# Example usage
if __name__ == "__main__":
    # Test key generation
    test_key = generate_license_key("PRO", "TEST12345")
    print(f"Generated key: {test_key}")

    # Test validation
    valid, tier, msg = validate_license(test_key)
    print(f"Valid: {valid}, Tier: {tier}, Message: {msg}")

    # Test invalid key
    valid, tier, msg = validate_license("CE-PRO-INVALID-XXXXX")
    print(f"Valid: {valid}, Tier: {tier}, Message: {msg}")
