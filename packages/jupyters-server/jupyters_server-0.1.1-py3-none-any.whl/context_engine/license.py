# License Module for ContextEngine
# Handles tier-based feature gating

import os
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict

# Tier constants
TIER_FREE = "free"
TIER_PRO = "pro"
TIER_TEAM = "team"

# Feature limits per tier
TIER_LIMITS = {
    TIER_FREE: {
        "daily_executions": 10,
        "inspect_variable": False,
        "vision": False,
        "domain_profiles": False,
        "safety_override": False,
    },
    TIER_PRO: {
        "daily_executions": -1,  # Unlimited
        "inspect_variable": True,
        "vision": True,
        "domain_profiles": False,
        "safety_override": False,
    },
    TIER_TEAM: {
        "daily_executions": -1,
        "inspect_variable": True,
        "vision": True,
        "domain_profiles": True,
        "safety_override": True,
    },
}

CONFIG_DIR = Path.home() / ".context-engine"
LICENSE_FILE = CONFIG_DIR / "license.json"
USAGE_FILE = CONFIG_DIR / "usage.json"

class LicenseManager:
    """Manages license validation and feature gating."""
    
    _instance = None
    _tier = TIER_FREE
    _last_mtime = 0
    
    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
            cls._instance._load_license()
        return cls._instance
    
    def _load_license(self):
        """Loads license from disk."""
        try:
            if LICENSE_FILE.exists():
                mtime = LICENSE_FILE.stat().st_mtime
                if mtime > self._last_mtime:
                    with open(LICENSE_FILE) as f:
                        data = json.load(f)
                        self._license_key = data.get("key")
                        self._tier = data.get("tier", TIER_FREE)
                        self._last_mtime = mtime
        except Exception:
            self._tier = TIER_FREE
            
    def get_tier(self) -> str:
        self._load_license() # Check for updates
        return self._tier
    
    def can_use_feature(self, feature: str) -> bool:
        """Checks if the current tier allows a feature."""
        limits = TIER_LIMITS.get(self._tier, TIER_LIMITS[TIER_FREE])
        return limits.get(feature, False)
    
    def check_execution_limit(self) -> tuple[bool, str]:
        """Checks if user has exceeded daily execution limit."""
        limits = TIER_LIMITS.get(self._tier, TIER_LIMITS[TIER_FREE])
        daily_limit = limits.get("daily_executions", 5)
        
        if daily_limit == -1:
            return True, ""
            
        # Load usage
        usage = self._load_usage()
        today = datetime.now().strftime("%Y-%m-%d")
        today_count = usage.get(today, 0)
        
        if today_count >= daily_limit:
            return False, f"⚠️ Free tier limit reached ({daily_limit} executions/day). Upgrade at contextengine.dev/pricing"
            
        return True, ""
    
    def record_execution(self):
        """Records an execution for usage tracking."""
        usage = self._load_usage()
        today = datetime.now().strftime("%Y-%m-%d")
        usage[today] = usage.get(today, 0) + 1
        self._save_usage(usage)
        
    def _load_usage(self) -> Dict:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        try:
            if USAGE_FILE.exists():
                with open(USAGE_FILE) as f:
                    return json.load(f)
        except Exception:
            pass
        return {}
    
    def _save_usage(self, usage: Dict):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(USAGE_FILE, 'w') as f:
            json.dump(usage, f)
            
    def activate_license(self, key: str) -> tuple[bool, str]:
        """Activates a license key."""
        from context_engine.license_validator import validate_license

        # Validate the key
        valid, tier, message = validate_license(key, use_cache=False)

        if not valid:
            return False, f"License activation failed: {message}"

        # Save to config
        self._tier = tier
        self._license_key = key
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(LICENSE_FILE, 'w') as f:
            json.dump({"key": key, "tier": self._tier}, f)

        self._last_mtime = LICENSE_FILE.stat().st_mtime

        return True, f"✅ License activated: {self._tier.upper()} tier - {message}"


# Convenience functions
def check_license() -> str:
    return LicenseManager.instance().get_tier()

def can_use_feature(feature: str) -> bool:
    return LicenseManager.instance().can_use_feature(feature)

def check_execution_limit() -> tuple[bool, str]:
    return LicenseManager.instance().check_execution_limit()

def record_execution():
    LicenseManager.instance().record_execution()
