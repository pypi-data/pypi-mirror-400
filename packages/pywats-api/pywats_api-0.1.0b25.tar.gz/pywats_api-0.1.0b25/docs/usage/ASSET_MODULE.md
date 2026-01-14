# Asset Module Usage Guide

## Overview

The Asset module manages test equipment, stations, fixtures, and other manufacturing assets in WATS. Assets can be hierarchical (e.g., stations containing instruments) and track calibration, maintenance, and usage history.

## Quick Start

```python
from pywats import pyWATS

api = pyWATS(base_url="https://wats.example.com", token="credentials")

# Get all assets
assets = api.asset.get_assets()

# Get specific asset
asset = api.asset.get_asset(asset_id)

# Get assets by type
stations = api.asset.get_assets_by_type("Station")
```

## Asset Types

Assets are categorized by type. Common types include:

| Type | Description | Examples |
|------|-------------|----------|
| **Station** | Test station or workstation | ICT-01, FVT-STATION-01 |
| **Instrument** | Measurement equipment | DMM, Oscilloscope, Power Supply |
| **Fixture** | Test fixtures | Bed-of-nails, Custom fixture |
| **Software** | Software tools | LabVIEW RT, TestStand |
| **Tool** | Hand tools or equipment | Soldering iron, Torque wrench |

## Basic Operations

### 1. Get Assets

```python
# Get all assets (summary view)
assets = api.asset.get_assets()

for asset in assets:
    print(f"{asset.name}: {asset.asset_type}")
    print(f"  ID: {asset.asset_id}")
    print(f"  Serial: {asset.serial_number}")
    print(f"  State: {asset.state}")

# Get full asset details (with nested data)
asset = api.asset.get_asset_full(asset_id)
print(f"Children: {len(asset.children) if asset.children else 0}")
```

### 2. Get Asset by ID

```python
# Get specific asset
asset = api.asset.get_asset(asset_id)

if asset:
    print(f"Name: {asset.name}")
    print(f"Type: {asset.asset_type}")
    print(f"Serial Number: {asset.serial_number}")
    print(f"State: {asset.state}")
    print(f"Location: {asset.location}")
```

### 3. Get Assets by Type

```python
# Get all assets of a specific type
stations = api.asset.get_assets_by_type("Station")
instruments = api.asset.get_assets_by_type("Instrument")
fixtures = api.asset.get_assets_by_type("Fixture")

print(f"Found {len(stations)} stations")
for station in stations:
    print(f"  - {station.name} ({station.serial_number})")
```

### 4. Create Asset

```python
from pywats.domains.asset import AssetState

# Create new asset
asset = api.asset.create_asset(
    name="DMM-001",
    asset_type="Instrument",
    serial_number="DMM2024-12345",
    state=AssetState.ACTIVE,
    description="Keithley 2000 Digital Multimeter",
    location="Lab A"
)

print(f"Created asset: {asset.name} (ID: {asset.asset_id})")
```

### 5. Update Asset

```python
# Get asset, modify, update
asset = api.asset.get_asset(asset_id)
asset.description = "Updated description"
asset.location = "Lab B"
asset.state = AssetState.IN_CALIBRATION

updated = api.asset.update_asset(asset)
print(f"Updated: {updated.name}")
```

### 6. Delete Asset

```python
# Delete an asset (use with caution)
success = api.asset.delete_asset(asset_id)
if success:
    print("Asset deleted")
```

## Asset Hierarchy

Assets can have parent-child relationships (e.g., instruments inside a station).

### 1. Get Child Assets

```python
# Get children of an asset
children = api.asset.get_child_assets(parent_asset_id)

print(f"Station has {len(children)} instruments:")
for child in children:
    print(f"  - {child.name} ({child.asset_type})")
```

### 2. Create Child Asset

```python
# Create asset as child of another
instrument = api.asset.create_asset(
    name="DMM-Internal",
    asset_type="Instrument",
    serial_number="DMM-INT-001",
    state=AssetState.ACTIVE,
    parent_id=station_asset_id  # Parent asset
)
```

### 3. Move Asset (Change Parent)

```python
# Move asset to new parent
asset = api.asset.get_asset(asset_id)
asset.parent_id = new_parent_id
api.asset.update_asset(asset)
```

## Asset States

```python
from pywats.domains.asset import AssetState

# Available states
AssetState.ACTIVE           # In use, operational
AssetState.INACTIVE         # Not in use
AssetState.IN_CALIBRATION   # Being calibrated
AssetState.IN_REPAIR        # Being repaired
AssetState.RETIRED          # End of life
```

### State Transitions

```python
# Example: Send asset for calibration
asset = api.asset.get_asset(asset_id)
asset.state = AssetState.IN_CALIBRATION
api.asset.update_asset(asset)

# After calibration complete
asset.state = AssetState.ACTIVE
asset.calibration_date = datetime.now()
asset.next_calibration_date = datetime.now() + timedelta(days=365)
api.asset.update_asset(asset)
```

## Asset Tags

Assets can have tags (key-value metadata):

### 1. Get Asset Tags

```python
# Get tags for an asset
tags = api.asset.get_asset_tags(asset_id)
for tag in tags:
    print(f"{tag.key}: {tag.value}")
```

### 2. Set Asset Tags

```python
from pywats.shared import Setting

# Set tags (replaces all existing)
api.asset.set_asset_tags(asset_id, [
    Setting(key="Manufacturer", value="Keithley"),
    Setting(key="Model", value="2000"),
    Setting(key="CalibrationInterval", value="365")
])
```

### 3. Add Single Tag

```python
# Add/update single tag
api.asset.add_asset_tag(asset_id, "Location", "Lab A")
```

## Calibration Tracking

### 1. Track Calibration Dates

```python
from datetime import datetime, timedelta

# Update calibration info
asset = api.asset.get_asset(asset_id)
asset.calibration_date = datetime.now()
asset.next_calibration_date = datetime.now() + timedelta(days=365)
api.asset.update_asset(asset)
```

### 2. Find Assets Due for Calibration

```python
from datetime import datetime

# Get all instruments
instruments = api.asset.get_assets_by_type("Instrument")

# Find those due for calibration
due_soon = []
for instr in instruments:
    if instr.next_calibration_date:
        days_until = (instr.next_calibration_date - datetime.now()).days
        if days_until <= 30:
            due_soon.append({
                "asset": instr,
                "days_until": days_until
            })

print("Assets due for calibration within 30 days:")
for item in due_soon:
    print(f"  {item['asset'].name}: {item['days_until']} days")
```

## Common Patterns

### Pattern 1: Station Setup

```python
from pywats.domains.asset import AssetState

# 1. Create station
station = api.asset.create_asset(
    name="ICT-STATION-01",
    asset_type="Station",
    serial_number="ICT-2024-001",
    state=AssetState.ACTIVE,
    description="In-Circuit Test Station 1",
    location="Production Floor"
)

# 2. Add instruments to station
dmm = api.asset.create_asset(
    name="ICT-01-DMM",
    asset_type="Instrument",
    serial_number="DMM-001",
    state=AssetState.ACTIVE,
    description="Station DMM",
    parent_id=station.asset_id
)

power_supply = api.asset.create_asset(
    name="ICT-01-PSU",
    asset_type="Instrument",
    serial_number="PSU-001",
    state=AssetState.ACTIVE,
    description="Station Power Supply",
    parent_id=station.asset_id
)

# 3. Tag the station
api.asset.set_asset_tags(station.asset_id, [
    Setting(key="Line", value="Production Line 1"),
    Setting(key="Process", value="ICT"),
    Setting(key="Shift", value="All")
])
```

### Pattern 2: Asset Inventory Report

```python
def generate_inventory_report():
    """Generate asset inventory by type"""
    assets = api.asset.get_assets()
    
    # Group by type
    by_type = {}
    for asset in assets:
        asset_type = asset.asset_type or "Unknown"
        if asset_type not in by_type:
            by_type[asset_type] = []
        by_type[asset_type].append(asset)
    
    # Print report
    print("=" * 50)
    print("ASSET INVENTORY REPORT")
    print("=" * 50)
    
    for asset_type, items in sorted(by_type.items()):
        print(f"\n{asset_type}: {len(items)} items")
        for item in items:
            state = item.state.name if item.state else "Unknown"
            print(f"  - {item.name} ({item.serial_number}) [{state}]")
    
    print(f"\nTotal: {len(assets)} assets")
```

### Pattern 3: Calibration Management

```python
from datetime import datetime, timedelta
from pywats.domains.asset import AssetState

def send_for_calibration(asset_id: str):
    """Mark asset as in calibration"""
    asset = api.asset.get_asset(asset_id)
    asset.state = AssetState.IN_CALIBRATION
    api.asset.update_asset(asset)
    print(f"{asset.name} sent for calibration")

def complete_calibration(asset_id: str, interval_days: int = 365):
    """Complete calibration and update dates"""
    asset = api.asset.get_asset(asset_id)
    asset.state = AssetState.ACTIVE
    asset.calibration_date = datetime.now()
    asset.next_calibration_date = datetime.now() + timedelta(days=interval_days)
    api.asset.update_asset(asset)
    print(f"{asset.name} calibration complete, next due: {asset.next_calibration_date}")

def get_calibration_schedule():
    """Get upcoming calibration schedule"""
    instruments = api.asset.get_assets_by_type("Instrument")
    
    schedule = []
    for instr in instruments:
        if instr.next_calibration_date and instr.state == AssetState.ACTIVE:
            schedule.append({
                "name": instr.name,
                "serial": instr.serial_number,
                "due_date": instr.next_calibration_date,
                "days_remaining": (instr.next_calibration_date - datetime.now()).days
            })
    
    # Sort by due date
    schedule.sort(key=lambda x: x["due_date"])
    return schedule
```

### Pattern 4: Asset Search

```python
def find_assets(
    name_contains: str = None,
    asset_type: str = None,
    state: AssetState = None,
    location: str = None
):
    """Search assets with filters"""
    assets = api.asset.get_assets()
    
    results = []
    for asset in assets:
        # Apply filters
        if name_contains and name_contains.lower() not in (asset.name or "").lower():
            continue
        if asset_type and asset.asset_type != asset_type:
            continue
        if state and asset.state != state:
            continue
        if location and location.lower() not in (asset.location or "").lower():
            continue
        
        results.append(asset)
    
    return results

# Usage
dmms = find_assets(name_contains="DMM", asset_type="Instrument")
active_stations = find_assets(asset_type="Station", state=AssetState.ACTIVE)
lab_equipment = find_assets(location="Lab")
```

## Asset Model Reference

### Asset Fields

| Field | Type | Description |
|-------|------|-------------|
| `asset_id` | UUID | Unique identifier |
| `name` | str | Asset name |
| `asset_type` | str | Type (Station, Instrument, etc.) |
| `serial_number` | str | Serial number |
| `description` | str | Description |
| `state` | AssetState | Current state |
| `location` | str | Physical location |
| `parent_id` | UUID | Parent asset ID (for hierarchy) |
| `calibration_date` | datetime | Last calibration date |
| `next_calibration_date` | datetime | Next calibration due |
| `children` | List[Asset] | Child assets (when loaded) |
| `tags` | List[Setting] | Key-value tags |

### AssetState Enum

| Value | Description |
|-------|-------------|
| `ACTIVE` | In use, operational |
| `INACTIVE` | Not currently in use |
| `IN_CALIBRATION` | Being calibrated |
| `IN_REPAIR` | Under repair |
| `RETIRED` | End of life |

## Best Practices

### 1. Use Meaningful Names

```python
# Good - descriptive names
"ICT-STATION-01"
"FVT-DMM-KEITHLEY"
"FIXTURE-PCBA-V2"

# Avoid - unclear names
"ASSET1"
"INST"
```

### 2. Track Serial Numbers

```python
# Always include serial numbers for traceability
asset = api.asset.create_asset(
    name="DMM-001",
    serial_number="KTH-2000-12345",  # Include manufacturer serial
    ...
)
```

### 3. Use Tags for Custom Data

```python
# Tags for flexible metadata
api.asset.set_asset_tags(asset_id, [
    Setting(key="Manufacturer", value="Keithley"),
    Setting(key="Model", value="2000"),
    Setting(key="PurchaseDate", value="2024-01-15"),
    Setting(key="WarrantyExpires", value="2027-01-15"),
    Setting(key="CostCenter", value="PROD-001")
])
```

### 4. Maintain Hierarchy

```python
# Organize assets hierarchically
# Station -> Instruments -> Components

station = api.asset.create_asset(name="FVT-01", asset_type="Station", ...)
dmm = api.asset.create_asset(name="FVT-01-DMM", parent_id=station.asset_id, ...)
scope = api.asset.create_asset(name="FVT-01-SCOPE", parent_id=station.asset_id, ...)
```

### 5. Track Calibration

```python
# Set calibration dates when creating instruments
from datetime import datetime, timedelta

instrument = api.asset.create_asset(
    name="DMM-001",
    asset_type="Instrument",
    calibration_date=datetime.now(),
    next_calibration_date=datetime.now() + timedelta(days=365),
    ...
)
```

## Troubleshooting

### Asset Not Found

```python
asset = api.asset.get_asset(asset_id)
if not asset:
    print(f"Asset {asset_id} not found")
    # Try searching by name
    assets = api.asset.get_assets()
    matches = [a for a in assets if "DMM" in a.name]
```

### Parent-Child Issues

```python
# Verify parent exists before creating child
parent = api.asset.get_asset(parent_id)
if not parent:
    print("Parent asset not found, create it first")
```

### State Transitions

```python
# Some state transitions may be restricted
# Always check current state before changing
asset = api.asset.get_asset(asset_id)
if asset.state == AssetState.RETIRED:
    print("Cannot modify retired asset")
```

## Related Documentation

- [Product Module](PRODUCT_MODULE.md) - Managing products tested by assets
- [Production Module](PRODUCTION_MODULE.md) - Manufacturing units at stations
- [Report Module](REPORT_MODULE.md) - Test reports from stations
