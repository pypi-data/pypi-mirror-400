
import sys
import os
import shutil
from pathlib import Path
from unittest.mock import MagicMock

# Mock FastMCP before importing server
sys.modules["mcp.server.fastmcp"] = MagicMock()
mcp_mock = MagicMock()
def tool_decorator():
    def wrapper(func):
        return func
    return wrapper
mcp_mock.tool = tool_decorator
sys.modules["mcp.server.fastmcp"].FastMCP = MagicMock(return_value=mcp_mock)

# Import server and license
# We need to make sure we are importing from src
sys.path.append(os.path.join(os.getcwd(), "src"))

# Clean up license file
CONFIG_DIR = Path.home() / ".context-engine"
LICENSE_FILE = CONFIG_DIR / "license.json"
if LICENSE_FILE.exists():
    os.remove(LICENSE_FILE)
    
from context_engine import server
from context_engine.license import LicenseManager, TIER_FREE, TIER_PRO, TIER_TEAM

def test_license_flow():
    print("--- Starting License Flow Verification ---")
    
    # 1. Check Initial State (Free)
    print(f"\n[1] Initial Tier: {LicenseManager.instance().get_tier()}")
    assert LicenseManager.instance().get_tier() == TIER_FREE
    
    # 2. Test Pro Feature (inspect_variable)
    print("\n[2] Testing Pro Feature (inspect_variable)...")
    res = server.inspect_variable("test_nb.ipynb", "df")
    print(f"Result: {res}")
    assert "Pro feature" in res
    
    # 3. Test Team Feature (set_profile)
    print("\n[3] Testing Team Feature (set_profile)...")
    res = server.set_profile("ml")
    print(f"Result: {res}")
    assert "Team feature" in res
    
    # 4. Activate Pro
    print("\n[4] Activating Pro License...")
    res = server.activate_license("CE-PRO-TEST-KEY")
    print(f"Result: {res}")
    assert "PRO tier" in res
    assert LicenseManager.instance().get_tier() == TIER_PRO
    
    # 5. Retest Pro Feature
    print("\n[5] Retesting Pro Feature (inspect_variable)...")
    # This should now FAIL with a different error (execution error) because we don't have a real kernel
    # But it should pass the LICENSE check
    res = server.inspect_variable("test_nb.ipynb", "df")
    print(f"Result: {res}")
    assert "Pro feature" not in res
    # It might return "Variable not found" or "Error inspecting variable"
    assert "Variable 'df' not found" in res or "Error inspecting variable" in res
    
    # 6. Retest Team Feature (should still fail)
    print("\n[6] Retesting Team Feature (set_profile)...")
    res = server.set_profile("ml")
    print(f"Result: {res}")
    assert "Team feature" in res
    
    # 7. Activate Team
    print("\n[7] Activating Team License...")
    res = server.activate_license("CE-TEAM-TEST-KEY")
    print(f"Result: {res}")
    assert "TEAM tier" in res
    assert LicenseManager.instance().get_tier() == TIER_TEAM
    
    # 8. Retest Team Feature
    print("\n[8] Retesting Team Feature (set_profile)...")
    res = server.set_profile("ml")
    print(f"Result: {res}")
    assert "Active profiles set to" in res
    
    print("\n--- Verification Successful! ---")
    
    # Cleanup
    if LICENSE_FILE.exists():
        os.remove(LICENSE_FILE)

if __name__ == "__main__":
    test_license_flow()
