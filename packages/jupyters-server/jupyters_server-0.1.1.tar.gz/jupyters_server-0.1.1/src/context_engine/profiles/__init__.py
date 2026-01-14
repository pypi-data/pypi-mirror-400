# Domain Profiles for ContextEngine
# Modular inspection handlers that run inside the user's kernel

from typing import Dict

# Active profile (default: base)
_active_profiles = ["base"]

def get_active_profiles():
    return _active_profiles

def set_profiles(profiles: list):
    global _active_profiles
    _active_profiles = profiles
