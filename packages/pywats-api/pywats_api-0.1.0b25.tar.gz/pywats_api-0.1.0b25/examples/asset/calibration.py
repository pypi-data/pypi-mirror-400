"""
Asset Domain: Calibration Management

This example demonstrates asset calibration tracking.
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
# Get Asset Calibration Status
# =============================================================================

# Get asset with calibration info
asset = api.asset.get_asset("DMM-001")

if asset:
    print(f"Asset: {asset.sn} - {asset.name}")
    print(f"  Last Calibration: {asset.lastCalibration}")
    print(f"  Next Calibration: {asset.nextCalibration}")
    print(f"  Calibration Interval: {asset.calibrationInterval} days")


# =============================================================================
# Find Assets Due for Calibration
# =============================================================================

# Get all assets
assets = api.asset.get_assets()

# Find assets due within 30 days
due_date = datetime.now() + timedelta(days=30)
due_soon = []

for asset in assets:
    if asset.nextCalibration:
        next_cal = asset.nextCalibration
        if isinstance(next_cal, str):
            next_cal = datetime.fromisoformat(next_cal.replace("Z", "+00:00"))
        if next_cal <= due_date:
            due_soon.append(asset)

print(f"\nAssets due for calibration within 30 days: {len(due_soon)}")
for asset in due_soon:
    print(f"  {asset.sn}: {asset.name} - Due: {asset.nextCalibration}")


# =============================================================================
# Find Overdue Assets
# =============================================================================

now = datetime.now()
overdue = []

for asset in assets:
    if asset.nextCalibration:
        next_cal = asset.nextCalibration
        if isinstance(next_cal, str):
            next_cal = datetime.fromisoformat(next_cal.replace("Z", "+00:00"))
        if next_cal < now:
            overdue.append(asset)

print(f"\nOverdue calibrations: {len(overdue)}")
for asset in overdue:
    print(f"  ⚠️ {asset.sn}: {asset.name} - Was due: {asset.nextCalibration}")


# =============================================================================
# Record Calibration
# =============================================================================

# Update calibration date
asset = api.asset.get_asset("DMM-001")

if asset:
    # Record new calibration
    asset.lastCalibration = datetime.now()
    asset.nextCalibration = datetime.now() + timedelta(days=365)  # Annual
    
    api.asset.update_asset(asset)
    print(f"Recorded calibration for {asset.sn}")


# =============================================================================
# Calibration Report
# =============================================================================

def print_calibration_report():
    """Print calibration status report."""
    assets = api.asset.get_assets()
    now = datetime.now()
    
    print("\n" + "=" * 60)
    print("CALIBRATION STATUS REPORT")
    print(f"Generated: {now}")
    print("=" * 60)
    
    overdue = []
    due_30 = []
    due_90 = []
    current = []
    no_cal = []
    
    for asset in assets:
        if not asset.nextCalibration:
            no_cal.append(asset)
            continue
            
        next_cal = asset.nextCalibration
        if isinstance(next_cal, str):
            next_cal = datetime.fromisoformat(next_cal.replace("Z", "+00:00"))
        
        days_until = (next_cal - now).days
        
        if days_until < 0:
            overdue.append((asset, days_until))
        elif days_until <= 30:
            due_30.append((asset, days_until))
        elif days_until <= 90:
            due_90.append((asset, days_until))
        else:
            current.append((asset, days_until))
    
    print(f"\n❌ OVERDUE ({len(overdue)}):")
    for asset, days in overdue:
        print(f"   {asset.sn}: {abs(days)} days overdue")
    
    print(f"\n⚠️  DUE WITHIN 30 DAYS ({len(due_30)}):")
    for asset, days in due_30:
        print(f"   {asset.sn}: {days} days remaining")
    
    print(f"\n📅 DUE WITHIN 90 DAYS ({len(due_90)}):")
    for asset, days in due_90:
        print(f"   {asset.sn}: {days} days remaining")
    
    print(f"\n✅ CURRENT ({len(current)})")
    print(f"\n❓ NO CALIBRATION SET ({len(no_cal)})")
    
    print("=" * 60)


# print_calibration_report()
