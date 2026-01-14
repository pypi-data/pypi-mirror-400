"""
Asset Domain: Maintenance Tracking

This example demonstrates asset maintenance scheduling and tracking.
"""
import os
from datetime import datetime, timedelta
from pywats import pyWATS

# =============================================================================
# Setup
# =============================================================================

api = pyWATS(
    base_url=os.environ.get("WATS_BASE_URL", "https://demo.wats.com"),
    token=os.environ.get("WATS_TOKEN", "")
)


# =============================================================================
# Get Asset Maintenance Status
# =============================================================================

asset = api.asset.get_asset("FIXTURE-001")

if asset:
    print(f"Asset: {asset.sn}")
    print(f"  Usage Count: {asset.usageCount}")
    print(f"  Usage Limit: {asset.usageLimit}")
    print(f"  Last Maintenance: {asset.lastMaintenance}")


# =============================================================================
# Check Usage-Based Maintenance
# =============================================================================

assets = api.asset.get_assets()

# Find assets approaching usage limit
approaching_limit = []
for asset in assets:
    if asset.usageLimit and asset.usageCount:
        remaining = asset.usageLimit - asset.usageCount
        if remaining <= 100:  # Within 100 uses of limit
            approaching_limit.append((asset, remaining))

print(f"\nAssets approaching usage limit:")
for asset, remaining in approaching_limit:
    print(f"  {asset.sn}: {remaining} uses remaining")


# =============================================================================
# Record Maintenance
# =============================================================================

asset = api.asset.get_asset("FIXTURE-001")

if asset:
    # Record maintenance - reset usage counter
    asset.lastMaintenance = datetime.now()
    asset.usageCount = 0
    
    api.asset.update_asset(asset)
    print(f"Recorded maintenance for {asset.sn}")


# =============================================================================
# Maintenance Schedule Report
# =============================================================================

def print_maintenance_schedule():
    """Print maintenance schedule based on usage."""
    assets = api.asset.get_assets()
    
    print("\n" + "=" * 60)
    print("MAINTENANCE SCHEDULE")
    print("=" * 60)
    
    # Group by urgency
    critical = []  # < 10% remaining
    warning = []   # 10-25% remaining
    normal = []    # > 25% remaining
    
    for asset in assets:
        if not asset.usageLimit or not asset.usageCount:
            continue
        
        pct_remaining = (asset.usageLimit - asset.usageCount) / asset.usageLimit * 100
        
        if pct_remaining < 10:
            critical.append((asset, pct_remaining))
        elif pct_remaining < 25:
            warning.append((asset, pct_remaining))
        else:
            normal.append((asset, pct_remaining))
    
    print(f"\n🔴 CRITICAL - Maintenance Required ({len(critical)}):")
    for asset, pct in critical:
        print(f"   {asset.sn}: {pct:.0f}% remaining ({asset.usageCount}/{asset.usageLimit})")
    
    print(f"\n🟡 WARNING - Schedule Soon ({len(warning)}):")
    for asset, pct in warning:
        print(f"   {asset.sn}: {pct:.0f}% remaining")
    
    print(f"\n🟢 NORMAL ({len(normal)})")
    
    print("=" * 60)


# print_maintenance_schedule()
