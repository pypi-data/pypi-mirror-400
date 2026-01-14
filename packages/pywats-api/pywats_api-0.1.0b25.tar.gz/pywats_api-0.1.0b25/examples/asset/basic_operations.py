"""
Asset Domain: Basic Operations

This example demonstrates basic asset CRUD operations.
"""
import os
from pywats import pyWATS

# =============================================================================
# Setup
# =============================================================================

api = pyWATS(
    base_url=os.environ.get("WATS_BASE_URL", "https://demo.wats.com"),
    token=os.environ.get("WATS_TOKEN", "")
)


# =============================================================================
# List Assets
# =============================================================================

# Get all assets
assets = api.asset.get_assets()
print(f"Found {len(assets)} assets")

for asset in assets[:5]:  # First 5
    print(f"  {asset.sn}: {asset.name} ({asset.type})")


# =============================================================================
# Get Single Asset
# =============================================================================

# Get asset by serial number
asset = api.asset.get_asset("DMM-001")

if asset:
    print(f"Asset: {asset.sn}")
    print(f"  Name: {asset.name}")
    print(f"  Type: {asset.type}")
    print(f"  Status: {asset.status}")
    print(f"  Location: {asset.location}")


# =============================================================================
# Create Asset
# =============================================================================

from pywats.domains.asset import Asset

# Create a new asset
new_asset = Asset(
    sn="NEW-METER-001",
    name="Digital Multimeter",
    type="Test Equipment",
    manufacturer="Keysight",
    model="34461A",
    location="Lab A"
)

result = api.asset.create_asset(new_asset)
print(f"Created asset: {result.sn}")


# =============================================================================
# Update Asset
# =============================================================================

# Get existing asset
asset = api.asset.get_asset("NEW-METER-001")

if asset:
    # Modify fields
    asset.location = "Lab B"
    asset.status = "Active"
    
    # Save changes
    api.asset.update_asset(asset)
    print(f"Updated asset: {asset.sn}")


# =============================================================================
# Delete Asset
# =============================================================================

# Delete by serial number (use with caution!)
# api.asset.delete_asset("NEW-METER-001")
# print("Asset deleted")


# =============================================================================
# Search Assets
# =============================================================================

# Get assets by type
test_equipment = [a for a in api.asset.get_assets() if a.type == "Test Equipment"]
print(f"Found {len(test_equipment)} test equipment assets")

# Get assets by location
lab_a_assets = [a for a in api.asset.get_assets() if a.location == "Lab A"]
print(f"Found {len(lab_a_assets)} assets in Lab A")
