"""
License Verification System for TCS Engine PRO

Commercial license required for PRO modules.
"""

import os
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class LicenseError(Exception):
    """Raised when PRO license is missing or invalid."""
    pass


# License tiers
LICENSE_TIERS = {
    "trial": {"max_agents": 10, "max_steps": 100, "features": ["dashboard"]},
    "pro_individual": {"max_agents": 100, "max_steps": 10000, "features": "all"},
    "pro_lab": {"max_agents": 1000, "max_steps": 100000, "features": "all"},
    "enterprise": {"max_agents": None, "max_steps": None, "features": "all"},
}

# License file locations
LICENSE_PATHS = [
    Path.home() / ".tcs_engine" / "license.json",
    Path.cwd() / ".tcs_license.json",
    Path(os.environ.get("TCS_LICENSE_FILE", "")),
]

_cached_license: Optional[Dict[str, Any]] = None


def _load_license() -> Optional[Dict[str, Any]]:
    """Load license from file."""
    global _cached_license

    if _cached_license is not None:
        return _cached_license

    for path in LICENSE_PATHS:
        if path and path.exists():
            try:
                with open(path) as f:
                    license_data = json.load(f)
                    if _validate_license_data(license_data):
                        _cached_license = license_data
                        return license_data
            except Exception as e:
                logger.debug(f"Failed to load license from {path}: {e}")

    # Check environment variable for license key
    env_key = os.environ.get("TCS_LICENSE_KEY")
    if env_key:
        license_data = _decode_license_key(env_key)
        if license_data:
            _cached_license = license_data
            return license_data

    return None


def _validate_license_data(data: Dict[str, Any]) -> bool:
    """Validate license data structure and expiration."""
    required_fields = ["key", "tier", "email", "expires"]

    if not all(field in data for field in required_fields):
        return False

    # Check expiration
    try:
        expires = datetime.fromisoformat(data["expires"])
        if expires < datetime.now():
            logger.warning("License has expired")
            return False
    except:
        return False

    # Verify key hash
    expected_hash = _compute_license_hash(data["email"], data["tier"], data["expires"])
    if not data["key"].startswith(expected_hash[:16]):
        return False

    return True


def _compute_license_hash(email: str, tier: str, expires: str) -> str:
    """Compute license key hash."""
    # Simple hash for demonstration - production would use proper crypto
    payload = f"{email}:{tier}:{expires}:TCS_SECRET_2024"
    return hashlib.sha256(payload.encode()).hexdigest()


def _decode_license_key(key: str) -> Optional[Dict[str, Any]]:
    """Decode a license key string."""
    try:
        # Format: TCS-{tier}-{hash}-{expiry}
        parts = key.split("-")
        if len(parts) != 4 or parts[0] != "TCS":
            return None

        tier = parts[1].lower()
        if tier not in LICENSE_TIERS:
            return None

        return {
            "key": key,
            "tier": tier,
            "email": "license@tcs-engine.dev",
            "expires": "2099-12-31",  # Demo key
            "features": LICENSE_TIERS[tier]["features"]
        }
    except:
        return None


def verify_license(required_tier: str = None) -> bool:
    """
    Verify that a valid PRO license is present.

    Args:
        required_tier: Optional minimum tier required

    Returns:
        True if valid license found, False otherwise
    """
    license_data = _load_license()

    if license_data is None:
        # Allow trial mode with limited features
        trial_key = os.environ.get("TCS_TRIAL_MODE")
        if trial_key == "enabled":
            logger.info("Running in trial mode (limited features)")
            return True
        return False

    if required_tier:
        tier_order = ["trial", "pro_individual", "pro_lab", "enterprise"]
        license_tier = license_data.get("tier", "trial")

        if tier_order.index(license_tier) < tier_order.index(required_tier):
            return False

    return True


def get_license_info() -> Dict[str, Any]:
    """Get current license information."""
    license_data = _load_license()

    if license_data is None:
        return {
            "status": "unlicensed",
            "tier": None,
            "features": [],
            "message": "No valid license found. Visit https://tcs-engine.dev/pricing"
        }

    tier = license_data.get("tier", "trial")
    tier_info = LICENSE_TIERS.get(tier, LICENSE_TIERS["trial"])

    return {
        "status": "active",
        "tier": tier,
        "email": license_data.get("email"),
        "expires": license_data.get("expires"),
        "features": tier_info["features"],
        "max_agents": tier_info["max_agents"],
        "max_steps": tier_info["max_steps"]
    }


def require_license(tier: str = None):
    """Decorator to require PRO license for a function."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not verify_license(tier):
                raise LicenseError(
                    f"PRO license required for {func.__name__}. "
                    "Visit https://tcs-engine.dev/pricing to purchase."
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator


def activate_license(key: str, save: bool = True) -> bool:
    """
    Activate a license key.

    Args:
        key: License key string
        save: Whether to save to file

    Returns:
        True if activation successful
    """
    global _cached_license

    license_data = _decode_license_key(key)
    if license_data is None:
        raise LicenseError("Invalid license key format")

    if not _validate_license_data(license_data):
        raise LicenseError("License validation failed")

    _cached_license = license_data

    if save:
        license_path = Path.home() / ".tcs_engine" / "license.json"
        license_path.parent.mkdir(parents=True, exist_ok=True)
        with open(license_path, "w") as f:
            json.dump(license_data, f, indent=2)
        logger.info(f"License saved to {license_path}")

    return True
