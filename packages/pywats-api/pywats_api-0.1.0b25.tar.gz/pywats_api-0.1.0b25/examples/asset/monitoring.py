"""
Asset Domain: Status Monitoring

This example demonstrates asset status monitoring.
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
# Get Asset Status
# =============================================================================

asset = api.asset.get_asset("DMM-001")

if asset:
    print(f"Asset: {asset.sn}")
    print(f"  Status: {asset.status}")
    print(f"  Location: {asset.location}")


# =============================================================================
# List Assets by Status
# =============================================================================

assets = api.asset.get_assets()

# Group by status
by_status = {}
for asset in assets:
    status = asset.status or "Unknown"
    if status not in by_status:
        by_status[status] = []
    by_status[status].append(asset)

print("\nAssets by Status:")
for status, items in by_status.items():
    print(f"  {status}: {len(items)}")


# =============================================================================
# Update Asset Status
# =============================================================================

asset = api.asset.get_asset("DMM-001")

if asset:
    # Update status
    asset.status = "In Calibration"
    api.asset.update_asset(asset)
    print(f"Updated {asset.sn} status to: In Calibration")


# =============================================================================
# Asset Dashboard
# =============================================================================

def print_asset_dashboard():
    """Print asset status dashboard."""
    assets = api.asset.get_assets()
    
    print("\n" + "=" * 60)
    print("ASSET STATUS DASHBOARD")
    print("=" * 60)
    
    # Count by status
    status_counts = {}
    for asset in assets:
        status = asset.status or "Unknown"
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print(f"\nTotal Assets: {len(assets)}")
    print("\nBy Status:")
    for status, count in sorted(status_counts.items()):
        bar = "█" * (count * 2)
        print(f"  {status:20} {count:3} {bar}")
    
    # Count by location
    location_counts = {}
    for asset in assets:
        location = asset.location or "Unknown"
        location_counts[location] = location_counts.get(location, 0) + 1
    
    print("\nBy Location:")
    for location, count in sorted(location_counts.items()):
        print(f"  {location:20} {count:3}")
    
    # Count by type
    type_counts = {}
    for asset in assets:
        atype = asset.type or "Unknown"
        type_counts[atype] = type_counts.get(atype, 0) + 1
    
    print("\nBy Type:")
    for atype, count in sorted(type_counts.items()):
        print(f"  {atype:20} {count:3}")
    
    print("=" * 60)


# print_asset_dashboard()
