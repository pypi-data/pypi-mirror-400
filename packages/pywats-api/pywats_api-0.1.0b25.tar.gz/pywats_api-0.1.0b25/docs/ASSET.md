# Asset Domain

The Asset domain manages test equipment, stations, fixtures, instruments, and tools used in manufacturing operations. It provides comprehensive tracking for calibration schedules, maintenance history, usage counts, hierarchical relationships (stations containing instruments), and alarm states. Assets are the physical resources that execute tests and assemblies defined in other domains.

## Table of Contents

- [Quick Start](#quick-start)
- [Core Concepts](#core-concepts)
- [Asset Operations](#asset-operations)
- [Asset Types](#asset-types)
- [Asset Hierarchy](#asset-hierarchy)
- [Status and State Management](#status-and-state-management)
- [Count Tracking](#count-tracking)
- [Calibration Management](#calibration-management)
- [Maintenance Management](#maintenance-management)
- [Asset Logs](#asset-logs)
- [File Operations](#file-operations)
- [Advanced Usage](#advanced-usage)
- [API Reference](#api-reference)

---

## Quick Start

```python
from pywats import pyWATS

# Initialize the API
api = pyWATS(
    base_url="https://your-wats-server.com",
    token="your-api-token"
)

# List all assets
assets = api.asset.get_assets()
for asset in assets:
    print(f"{asset.asset_name} ({asset.serial_number})")

# Get specific asset by serial number
dmm = api.asset.get_asset_by_serial("DMM-001")
print(f"Asset: {dmm.asset_name}")
print(f"State: {dmm.state}")
print(f"Last Calibration: {dmm.last_calibration_date}")

# Create a new test instrument
from pywats.domains.asset import AssetState

# First, get an asset type
asset_types = api.asset.get_asset_types()
instrument_type = next(t for t in asset_types if "Instrument" in t.type_name)

new_asset = api.asset.create_asset(
    serial_number="SCOPE-12345",
    type_id=instrument_type.type_id,
    asset_name="Oscilloscope Rigol DS1054Z",
    description="4-channel 50MHz oscilloscope",
    location="Lab A",
    state=AssetState.OK
)

# Record calibration
api.asset.record_calibration(
    serial_number="SCOPE-12345",
    comment="Annual calibration completed"
)
```

---

## Core Concepts

### Asset
An **Asset** represents a piece of equipment, station, fixture, or tool used in manufacturing. Each asset is identified by a unique serial number.

**Key attributes:**
- `serial_number`: Unique identifier (e.g., "DMM-001", "ICT-STATION-05")
- `asset_name`: Human-readable name
- `type_id`: Links to AssetType (defines category and limits)
- `state`: Current condition (OK, WARNING, ALARM, ERROR)
- `location`: Physical location
- `parent_asset_id`: For hierarchical structures (e.g., instrument belongs to station)

### Asset Type
An **AssetType** defines a category of assets with shared characteristics and limits. It specifies calibration intervals, maintenance schedules, and usage limits.

**Key attributes:**
- `type_name`: Category name (e.g., "Station", "Instrument", "Fixture")
- `calibration_interval`: Days between calibrations
- `maintenance_interval`: Days between maintenance
- `running_count_limit`: Max uses before maintenance
- `total_count_limit`: Lifetime usage limit

**Common asset types:**
- **Station**: Test station or workstation (ICT, FVT, Assembly)
- **Instrument**: Measurement equipment (DMM, Oscilloscope, Power Supply)
- **Fixture**: Test fixtures and adapters (bed-of-nails, custom jigs)
- **Software**: Software tools and licenses (LabVIEW, TestStand)
- **Tool**: Hand tools and equipment (soldering iron, torque wrench)

### Asset State
Assets can be in different states based on calibration, maintenance, and usage:

- **OK**: Operating normally, within all limits
- **WARNING**: Approaching limits (calibration due soon, count near limit)
- **ALARM**: Exceeded limits (calibration overdue, count limit reached)
- **ERROR**: Hardware fault or communication failure

### Asset Hierarchy
Assets can have parent-child relationships:
- A **Station** can contain multiple **Instruments** and **Fixtures**
- This models physical reality (e.g., ICT-01 station uses DMM-123 and PSU-456)
- Children increment counts when parents are used
- Helps track which equipment was used for each test

---

## Asset Operations

### List All Assets

```python
# Get all assets
assets = api.asset.get_assets()
print(f"Total assets: {len(assets)}")

for asset in assets:
    print(f"{asset.asset_name}")
    print(f"  S/N: {asset.serial_number}")
    print(f"  State: {asset.state}")
    print(f"  Location: {asset.location or 'Not set'}")

# Filter with OData query
active_assets = api.asset.get_assets(
    filter_str="state eq 'OK'",
    top=50
)

# Get assets by location
lab_assets = api.asset.get_assets(
    filter_str="contains(location,'Lab A')"
)
```

### Get Specific Asset

```python
# By serial number (preferred)
asset = api.asset.get_asset_by_serial("DMM-001")

# By asset ID (UUID)
asset = api.asset.get_asset("550e8400-e29b-41d4-a716-446655440000")

# By identifier string (tries ID first, then serial)
asset = api.asset.get_asset("DMM-001")

if asset:
    print(f"Asset: {asset.asset_name}")
    print(f"Type: {asset.type_id}")
    print(f"State: {asset.state}")
    print(f"Total Count: {asset.total_count or 0}")
    print(f"Running Count: {asset.running_count or 0}")
else:
    print("Asset not found")
```

### Create New Asset

```python
from uuid import UUID
from pywats.domains.asset import AssetState

# Get asset type first
types = api.asset.get_asset_types()
dmm_type = next(t for t in types if "DMM" in t.type_name.upper())

# Create simple asset
asset = api.asset.create_asset(
    serial_number="DMM-NEW-001",
    type_id=dmm_type.type_id,
    asset_name="Keithley 2000 Multimeter",
    description="6.5 digit bench DMM",
    location="Lab A"
)

# Create with full details
asset = api.asset.create_asset(
    serial_number="SCOPE-001",
    type_id=dmm_type.type_id,
    asset_name="Rigol DS1054Z",
    description="4-channel 50MHz oscilloscope",
    location="Lab B",
    part_number="DS1054Z",
    revision="1.0",
    state=AssetState.OK,
    total_count=0,
    running_count=0
)

print(f"Created asset ID: {asset.asset_id}")
```

### Update Existing Asset

```python
# Get the asset
asset = api.asset.get_asset_by_serial("DMM-001")

# Modify fields
asset.asset_name = "Updated Name"
asset.location = "Lab C"
asset.description = "Moved to Lab C for project XYZ"

# Save changes
updated = api.asset.update_asset(asset)
print(f"Updated: {updated.asset_name}")
```

### Delete Asset

```python
# Delete by serial number
success = api.asset.delete_asset(serial_number="OLD-DMM-001")

# Delete by asset ID
success = api.asset.delete_asset(asset_id="550e8400-e29b-41d4-a716-446655440000")

if success:
    print("Asset deleted")
else:
    print("Delete failed - asset may be in use")
```

---

## Asset Types

Asset types define categories of equipment with shared characteristics.

### List Asset Types

```python
# Get all asset types
types = api.asset.get_asset_types()

print("Asset Types:")
for asset_type in types:
    print(f"\n{asset_type.type_name} (ID: {asset_type.type_id})")
    print(f"  Calibration interval: {asset_type.calibration_interval or 'None'} days")
    print(f"  Maintenance interval: {asset_type.maintenance_interval or 'None'} days")
    print(f"  Running count limit: {asset_type.running_count_limit or 'None'}")
    print(f"  Total count limit: {asset_type.total_count_limit or 'None'}")
```

### Create Asset Type

```python
# Create a new asset type
new_type = api.asset.create_asset_type(
    type_name="Thermal Chamber",
    calibration_interval=180.0,  # 180 days = 6 months
    maintenance_interval=90.0,   # 90 days = quarterly
    running_count_limit=5000,    # Reset after 5000 cycles
    total_count_limit=50000,     # Replace after 50000 cycles
    warning_threshold=0.8,       # Warning at 80% of limit
    alarm_threshold=1.0          # Alarm at 100% of limit
)

print(f"Created type: {new_type.type_name} (ID: {new_type.type_id})")
```

### Get Assets by Type

```python
# Get all assets of a specific type
# First find the type
types = api.asset.get_asset_types()
station_type = next(t for t in types if t.type_name == "Station")

# Get all assets
all_assets = api.asset.get_assets()

# Filter by type
stations = [a for a in all_assets if a.type_id == station_type.type_id]

print(f"Found {len(stations)} stations:")
for station in stations:
    print(f"  - {station.asset_name} ({station.serial_number})")
```

---

## Asset Hierarchy

Assets can have parent-child relationships to model physical configurations.

### Create Asset with Parent

```python
# Get asset types
types = api.asset.get_asset_types()
station_type = next(t for t in types if "Station" in t.type_name)
instrument_type = next(t for t in types if "Instrument" in t.type_name)

# Create parent station
station = api.asset.create_asset(
    serial_number="ICT-STATION-01",
    type_id=station_type.type_id,
    asset_name="ICT Station 1",
    location="Production Floor"
)

# Create child instrument (attached to station)
dmm = api.asset.create_asset(
    serial_number="DMM-123",
    type_id=instrument_type.type_id,
    asset_name="Keithley DMM",
    parent_serial_number="ICT-STATION-01"  # Link to parent
)

print(f"Created DMM as child of {station.asset_name}")
```

### Add Child to Existing Asset

```python
# Add a child asset to existing parent
power_supply = api.asset.add_child_asset(
    parent_serial="ICT-STATION-01",
    child_serial="PSU-456",
    child_type_id=instrument_type.type_id,
    child_name="Agilent Power Supply",
    description="Triple output bench supply",
    part_number="E3631A"
)

print(f"Added {power_supply.asset_name} to station")
```

### Get Child Assets

```python
# Get all children of a parent asset
parent = api.asset.get_asset_by_serial("ICT-STATION-01")

children = api.asset.get_child_assets(parent_id=str(parent.asset_id))

print(f"Station {parent.asset_name} has {len(children)} child assets:")
for child in children:
    print(f"  - {child.asset_name} ({child.serial_number})")

# Get children by serial number
children = api.asset.get_child_assets(parent_serial="ICT-STATION-01")

# Get children at specific hierarchy level
level_1_children = api.asset.get_child_assets(
    parent_serial="ICT-STATION-01",
    level=1  # Only direct children
)
```

---

## Status and State Management

Assets track their operational status and can enter warning/alarm states.

### Get Asset Status

```python
# Get detailed status including alarm information
status = api.asset.get_status(serial_number="DMM-001")

if status:
    print(f"Asset Status:")
    print(f"  State: {status.get('state')}")
    print(f"  In Warning: {status.get('in_warning', False)}")
    print(f"  In Alarm: {status.get('in_alarm', False)}")
    print(f"  Calibration due: {status.get('calibration_due')}")
    print(f"  Maintenance due: {status.get('maintenance_due')}")
    print(f"  Count percentage: {status.get('count_percentage')}%")
```

### Get Asset State

```python
from pywats.domains.asset import AssetState

# Get current state
state = api.asset.get_asset_state(serial_number="DMM-001")

if state == AssetState.OK:
    print("Asset is operating normally")
elif state == AssetState.WARNING:
    print("Asset has warnings - check calibration/maintenance")
elif state == AssetState.ALARM:
    print("Asset in alarm state - immediate attention required")
```

### Set Asset State

```python
from pywats.domains.asset import AssetState

# Manually set asset state (e.g., after repair)
success = api.asset.set_asset_state(
    serial_number="DMM-001",
    state=AssetState.OK
)

# Set to maintenance mode
api.asset.set_asset_state(
    serial_number="SCOPE-001",
    state=AssetState.WARNING
)
```

### Check Warning/Alarm Conditions

```python
# Check if asset is in warning
if api.asset.is_in_warning(serial_number="DMM-001"):
    print("Asset has warnings")

# Check if asset is in alarm
if api.asset.is_in_alarm(serial_number="DMM-001"):
    print("Asset in alarm state!")

# Get all assets in warning
from pywats.domains.asset import AssetAlarmState

warned_assets = api.asset.get_assets_with_alarm_state(
    alarm_states=[AssetAlarmState.WARNING]
)

print(f"Found {len(warned_assets)} assets in warning:")
for asset in warned_assets:
    print(f"  - {asset.asset_name}: {asset.serial_number}")

# Get all assets in alarm
alarmed_assets = api.asset.get_assets_with_alarm_state(
    alarm_states=[AssetAlarmState.ALARM]
)
```

---

## Count Tracking

Assets track usage counts for maintenance scheduling.

### Increment Count

```python
# Increment usage count by 1
success = api.asset.increment_count(serial_number="DMM-001")

# Increment by specific amount
success = api.asset.increment_count(
    serial_number="ICT-STATION-01",
    amount=5
)

# Increment parent and all children
success = api.asset.increment_count(
    serial_number="ICT-STATION-01",
    amount=1,
    increment_children=True  # Also increments DMM, PSU, etc.
)

# Check updated counts
asset = api.asset.get_asset_by_serial("DMM-001")
print(f"Total count: {asset.total_count}")
print(f"Running count: {asset.running_count}")
```

### Reset Running Count

```python
# Reset running count after maintenance
success = api.asset.reset_running_count(
    serial_number="DMM-001",
    comment="Reset after scheduled maintenance"
)

# Verify reset
asset = api.asset.get_asset_by_serial("DMM-001")
print(f"Running count after reset: {asset.running_count}")  # Should be 0
print(f"Total count: {asset.total_count}")  # Unchanged
```

---

## Calibration Management

Track calibration schedules and history.

### Record Calibration

```python
from datetime import datetime

# Record calibration with current timestamp
success = api.asset.record_calibration(
    serial_number="DMM-001",
    comment="Annual calibration completed by Metrology Lab"
)

# Record calibration with specific date
calibration_date = datetime(2024, 6, 15, 10, 30)

success = api.asset.record_calibration(
    asset_id="550e8400-e29b-41d4-a716-446655440000",
    calibration_date=calibration_date,
    comment="Calibrated against NIST traceable standards"
)

# Check updated dates
asset = api.asset.get_asset_by_serial("DMM-001")
print(f"Last calibration: {asset.last_calibration_date}")
print(f"Next calibration: {asset.next_calibration_date}")
```

### Check Calibration Due

```python
from datetime import datetime, timedelta

# Get assets with calibration due within 30 days
all_assets = api.asset.get_assets()
now = datetime.now()
due_soon = []

for asset in all_assets:
    if asset.next_calibration_date:
        days_until_due = (asset.next_calibration_date - now).days
        if 0 <= days_until_due <= 30:
            due_soon.append((asset, days_until_due))

print(f"Assets needing calibration in next 30 days:")
for asset, days in sorted(due_soon, key=lambda x: x[1]):
    print(f"  {asset.asset_name} - Due in {days} days")
```

### Calibration Reminder Report

```python
def get_calibration_report(api, days_ahead=90):
    """Generate calibration schedule report"""
    from datetime import datetime, timedelta
    
    all_assets = api.asset.get_assets()
    now = datetime.now()
    cutoff = now + timedelta(days=days_ahead)
    
    # Categorize assets
    overdue = []
    due_soon = []
    upcoming = []
    
    for asset in all_assets:
        if not asset.next_calibration_date:
            continue
            
        cal_date = asset.next_calibration_date
        
        if cal_date < now:
            overdue.append(asset)
        elif cal_date <= cutoff:
            days_until = (cal_date - now).days
            if days_until <= 30:
                due_soon.append((asset, days_until))
            else:
                upcoming.append((asset, days_until))
    
    print(f"\n=== CALIBRATION REPORT ({days_ahead} days) ===\n")
    
    if overdue:
        print(f"⚠️ OVERDUE ({len(overdue)} assets):")
        for asset in overdue:
            days_overdue = (now - asset.next_calibration_date).days
            print(f"  {asset.asset_name}: {days_overdue} days overdue")
    
    if due_soon:
        print(f"\n⚡ DUE SOON ({len(due_soon)} assets):")
        for asset, days in sorted(due_soon, key=lambda x: x[1]):
            print(f"  {asset.asset_name}: {days} days")
    
    if upcoming:
        print(f"\n📅 UPCOMING ({len(upcoming)} assets):")
        for asset, days in sorted(upcoming, key=lambda x: x[1])[:10]:
            print(f"  {asset.asset_name}: {days} days")

# Use it
get_calibration_report(api, days_ahead=90)
```

---

## Maintenance Management

Similar to calibration, but for general maintenance.

### Record Maintenance

```python
from datetime import datetime

# Record maintenance
success = api.asset.record_maintenance(
    serial_number="ICT-STATION-01",
    comment="Replaced worn fixture pins, cleaned vacuum system"
)

# Record with specific date
maintenance_date = datetime(2024, 7, 1, 14, 0)

success = api.asset.record_maintenance(
    serial_number="THERMAL-CHAMBER-01",
    maintenance_date=maintenance_date,
    comment="Quarterly preventive maintenance performed"
)

# Check dates
asset = api.asset.get_asset_by_serial("ICT-STATION-01")
print(f"Last maintenance: {asset.last_maintenance_date}")
print(f"Next maintenance: {asset.next_maintenance_date}")
```

### Maintenance Schedule

```python
def get_maintenance_schedule(api, days_ahead=60):
    """Generate maintenance schedule"""
    from datetime import datetime, timedelta
    
    all_assets = api.asset.get_assets()
    now = datetime.now()
    cutoff = now + timedelta(days=days_ahead)
    
    schedule = []
    
    for asset in all_assets:
        if not asset.next_maintenance_date:
            continue
        
        maint_date = asset.next_maintenance_date
        
        if now <= maint_date <= cutoff:
            days_until = (maint_date - now).days
            schedule.append((asset, days_until))
    
    print(f"\n=== MAINTENANCE SCHEDULE ({days_ahead} days) ===\n")
    
    for asset, days in sorted(schedule, key=lambda x: x[1]):
        status = "⚠️ URGENT" if days <= 7 else "📅"
        print(f"{status} {asset.asset_name} ({asset.serial_number}): {days} days")

# Use it
get_maintenance_schedule(api, days_ahead=60)
```

---

## Asset Logs

Asset logs record events and activities.

### Get Asset Logs

```python
# Get all logs
logs = api.asset.get_asset_log()

print(f"Total log entries: {len(logs)}")

for log in logs[:10]:  # Show first 10
    print(f"{log.timestamp}: {log.message}")
    print(f"  Asset: {log.asset_name}")
    print(f"  User: {log.user or 'System'}")

# Filter logs with OData
recent_logs = api.asset.get_asset_log(
    filter_str="timestamp gt 2024-06-01",
    top=50
)

# Filter by asset
dmm_logs = api.asset.get_asset_log(
    filter_str="contains(asset_name,'DMM')"
)
```

### Add Log Message

```python
# Add a log entry
asset = api.asset.get_asset_by_serial("DMM-001")

success = api.asset.add_log_message(
    asset_id=str(asset.asset_id),
    message="Repaired faulty input connector",
    user="john.smith"
)

if success:
    print("Log entry added")
```

---

## File Operations

⚠️ **INTERNAL API - Subject to change**

Assets can store configuration files, calibration certificates, manuals, etc.

### Upload File to Asset

```python
# Read file content
with open("calibration_cert.pdf", "rb") as f:
    content = f.read()

# Upload to asset
asset = api.asset.get_asset_by_serial("DMM-001")

success = api.asset_internal.upload_file(
    asset_id=str(asset.asset_id),
    filename="Calibration_Certificate_2024-06-15.pdf",
    content=content
)

if success:
    print("File uploaded")
```

### List Asset Files

```python
# List all files for an asset
files = api.asset_internal.list_files(asset_id=str(asset.asset_id))

print(f"Files for {asset.asset_name}:")
for file_info in files:
    print(f"  - {file_info['filename']} ({file_info['size']} bytes)")
    print(f"    Uploaded: {file_info['uploaded']}")
```

### Download File from Asset

```python
# Download a file
content = api.asset_internal.download_file(
    asset_id=str(asset.asset_id),
    filename="Calibration_Certificate_2024-06-15.pdf"
)

if content:
    # Save to local file
    with open("downloaded_cert.pdf", "wb") as f:
        f.write(content)
    print("File downloaded")
```

### Delete Files

```python
# Delete one or more files
success = api.asset_internal.delete_files(
    asset_id=str(asset.asset_id),
    filenames=["old_manual.pdf", "outdated_config.json"]
)

if success:
    print("Files deleted")
```

---

## Advanced Usage

### Complete Station Setup

```python
from pywats.domains.asset import AssetState

# Get asset types
types = api.asset.get_asset_types()
station_type = next(t for t in types if "Station" in t.type_name)
instrument_type = next(t for t in types if "Instrument" in t.type_name)
fixture_type = next(t for t in types if "Fixture" in t.type_name)

# 1. Create station
station = api.asset.create_asset(
    serial_number="FVT-STATION-05",
    type_id=station_type.type_id,
    asset_name="Final Verification Test Station 5",
    location="Production Floor - Zone A",
    state=AssetState.OK
)

# 2. Add instruments
dmm = api.asset.create_asset(
    serial_number="DMM-FVT05-01",
    type_id=instrument_type.type_id,
    asset_name="Keithley 2000 DMM",
    parent_serial_number="FVT-STATION-05",
    part_number="2000",
    description="6.5 digit multimeter for voltage measurements"
)

scope = api.asset.create_asset(
    serial_number="SCOPE-FVT05-01",
    type_id=instrument_type.type_id,
    asset_name="Rigol DS1054Z Oscilloscope",
    parent_serial_number="FVT-STATION-05",
    part_number="DS1054Z",
    description="4-channel 50MHz scope for waveform analysis"
)

psu = api.asset.create_asset(
    serial_number="PSU-FVT05-01",
    type_id=instrument_type.type_id,
    asset_name="Agilent E3631A Power Supply",
    parent_serial_number="FVT-STATION-05",
    part_number="E3631A",
    description="Triple output bench supply"
)

# 3. Add fixture
fixture = api.asset.create_asset(
    serial_number="FIX-FVT05-WIDGET",
    type_id=fixture_type.type_id,
    asset_name="Widget Test Fixture",
    parent_serial_number="FVT-STATION-05",
    description="Custom fixture for Widget product family"
)

# 4. Record initial calibration for instruments
api.asset.record_calibration(
    serial_number="DMM-FVT05-01",
    comment="Initial calibration - factory certified"
)

api.asset.record_calibration(
    serial_number="SCOPE-FVT05-01",
    comment="Initial calibration - factory certified"
)

# 5. Add configuration file
fixture_config = {
    "product": "WIDGET-001",
    "pin_map": {"TP1": "V+", "TP2": "GND", "TP3": "SIGNAL"},
    "force_voltage": 5.0
}

import json
api.asset_internal.upload_file(
    asset_id=str(fixture.asset_id),
    filename="config.json",
    content=json.dumps(fixture_config, indent=2).encode()
)

print(f"Station {station.asset_name} set up with {len([dmm, scope, psu, fixture])} child assets")
```

### Asset Health Dashboard

```python
def asset_health_dashboard(api):
    """Generate comprehensive asset health report"""
    from datetime import datetime, timedelta
    from collections import defaultdict
    
    all_assets = api.asset.get_assets()
    now = datetime.now()
    
    # Categorize assets
    stats = defaultdict(int)
    issues = {
        'cal_overdue': [],
        'cal_due_soon': [],
        'maint_overdue': [],
        'maint_due_soon': [],
        'count_warning': [],
        'count_alarm': [],
        'in_alarm': []
    }
    
    for asset in all_assets:
        # State
        stats[asset.state.value] += 1
        if asset.state.value == 'ALARM':
            issues['in_alarm'].append(asset)
        
        # Calibration
        if asset.next_calibration_date:
            days_until = (asset.next_calibration_date - now).days
            if days_until < 0:
                issues['cal_overdue'].append(asset)
            elif days_until <= 30:
                issues['cal_due_soon'].append(asset)
        
        # Maintenance
        if asset.next_maintenance_date:
            days_until = (asset.next_maintenance_date - now).days
            if days_until < 0:
                issues['maint_overdue'].append(asset)
            elif days_until <= 30:
                issues['maint_due_soon'].append(asset)
        
        # Count limits (if asset has type with limits)
        # This would require checking AssetType limits
    
    print("=" * 60)
    print("ASSET HEALTH DASHBOARD")
    print("=" * 60)
    
    print(f"\nTotal Assets: {len(all_assets)}")
    print(f"\nState Distribution:")
    for state, count in stats.items():
        print(f"  {state}: {count}")
    
    print(f"\n⚠️  CRITICAL ISSUES:")
    print(f"  Assets in ALARM state: {len(issues['in_alarm'])}")
    print(f"  Calibration overdue: {len(issues['cal_overdue'])}")
    print(f"  Maintenance overdue: {len(issues['maint_overdue'])}")
    
    print(f"\n📋 UPCOMING:")
    print(f"  Calibration due (30 days): {len(issues['cal_due_soon'])}")
    print(f"  Maintenance due (30 days): {len(issues['maint_due_soon'])}")
    
    if issues['cal_overdue']:
        print(f"\n⚠️  OVERDUE CALIBRATIONS:")
        for asset in issues['cal_overdue'][:5]:
            days = (now - asset.next_calibration_date).days
            print(f"  {asset.asset_name}: {days} days overdue")
    
    print("=" * 60)

# Use it
asset_health_dashboard(api)
```

### Bulk Import Assets

```python
def import_assets_from_csv(api, csv_file_path):
    """Import assets from CSV file"""
    import csv
    
    # Get asset types once
    types = api.asset.get_asset_types()
    type_map = {t.type_name: t.type_id for t in types}
    
    created = []
    
    with open(csv_file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            type_name = row['type']
            if type_name not in type_map:
                print(f"Warning: Unknown type '{type_name}' for {row['serial_number']}")
                continue
            
            asset = api.asset.create_asset(
                serial_number=row['serial_number'],
                type_id=type_map[type_name],
                asset_name=row['name'],
                description=row.get('description', ''),
                location=row.get('location', ''),
                part_number=row.get('part_number'),
                revision=row.get('revision')
            )
            
            if asset:
                created.append(asset)
                print(f"Created: {asset.asset_name}")
    
    return created

# CSV format:
# serial_number,name,type,location,description,part_number,revision
# DMM-001,Keithley 2000,Instrument,Lab A,6.5 digit DMM,2000,1.0
# SCOPE-001,Rigol DS1054Z,Instrument,Lab A,4-ch 50MHz,DS1054Z,1.0

imported = import_assets_from_csv(api, 'assets.csv')
print(f"Imported {len(imported)} assets")
```

### Usage Tracking with Automatic Counts

```python
# In your test sequence, increment counts
def run_test_sequence(api, station_serial, uut_serial):
    """Example test sequence that tracks asset usage"""
    
    # Increment station count (and all child instruments)
    api.asset.increment_count(
        serial_number=station_serial,
        amount=1,
        increment_children=True  # Increments DMM, PSU, Scope, Fixture
    )
    
    # Run tests...
    # test_voltage()
    # test_current()
    # test_waveform()
    
    # Log test completion
    station = api.asset.get_asset_by_serial(station_serial)
    api.asset.add_log_message(
        asset_id=str(station.asset_id),
        message=f"Tested unit {uut_serial}",
        user="automated_test_system"
    )
    
    # Check if maintenance is due
    if api.asset.is_in_warning(serial_number=station_serial):
        print(f"⚠️  Station {station_serial} needs attention")
        status = api.asset.get_status(serial_number=station_serial)
        print(f"Details: {status}")

# Use it
run_test_sequence(api, "FVT-STATION-05", "WIDGET-001-SN12345")
```

---

## API Reference

### AssetService Methods

#### Asset Operations
- `get_assets(filter_str, top)` → `List[Asset]` - Get all assets with optional filtering
- `get_asset(identifier)` → `Optional[Asset]` - Get asset by ID or serial number
- `get_asset_by_serial(serial_number)` → `Optional[Asset]` - Get asset by serial number
- `create_asset(...)` → `Optional[Asset]` - Create new asset
- `update_asset(asset)` → `Optional[Asset]` - Update existing asset
- `delete_asset(asset_id, serial_number)` → `bool` - Delete asset

#### Status Operations
- `get_status(asset_id, serial_number)` → `Optional[Dict]` - Get detailed status
- `get_asset_state(asset_id, serial_number)` → `Optional[AssetState]` - Get current state
- `set_asset_state(asset_id, serial_number, state)` → `bool` - Set state
- `is_in_alarm(asset_id, serial_number)` → `bool` - Check if in alarm
- `is_in_warning(asset_id, serial_number)` → `bool` - Check if in warning
- `get_assets_with_alarm_state(alarm_states, top)` → `List[Asset]` - Get assets in specific states

#### Count Operations
- `increment_count(asset_id, serial_number, amount, increment_children)` → `bool` - Increment usage count
- `reset_running_count(asset_id, serial_number, comment)` → `bool` - Reset running count

#### Calibration & Maintenance
- `record_calibration(asset_id, serial_number, comment, calibration_date)` → `bool` - Record calibration
- `record_maintenance(asset_id, serial_number, comment, maintenance_date)` → `bool` - Record maintenance

#### Log Operations
- `get_asset_log(filter_str, top)` → `List[AssetLog]` - Get log entries
- `add_log_message(asset_id, message, user)` → `bool` - Add log entry

#### Asset Type Operations
- `get_asset_types()` → `List[AssetType]` - Get all asset types
- `create_asset_type(...)` → `Optional[AssetType]` - Create new asset type

#### Sub-Asset Operations
- `get_child_assets(parent_id, parent_serial, level)` → `List[Asset]` - Get child assets
- `add_child_asset(parent_serial, child_serial, child_type_id, ...)` → `Optional[Asset]` - Add child asset

### AssetServiceInternal Methods (⚠️ Subject to change)

#### File Operations
- `upload_file(asset_id, filename, content)` → `bool` - Upload file to asset
- `list_files(asset_id)` → `List[Dict]` - List files for asset
- `download_file(asset_id, filename)` → `Optional[bytes]` - Download file
- `delete_files(asset_id, filenames)` → `bool` - Delete files

### Models

#### Asset
- `asset_id`: UUID (auto-generated)
- `serial_number`: str (required, unique)
- `asset_name`: Optional[str]
- `type_id`: UUID (required, links to AssetType)
- `description`: Optional[str]
- `location`: Optional[str]
- `parent_asset_id`: Optional[UUID]
- `part_number`: Optional[str]
- `revision`: Optional[str]
- `state`: AssetState
- `first_seen_date`: Optional[datetime]
- `last_seen_date`: Optional[datetime]
- `last_calibration_date`: Optional[datetime]
- `next_calibration_date`: Optional[datetime]
- `last_maintenance_date`: Optional[datetime]
- `next_maintenance_date`: Optional[datetime]
- `total_count`: Optional[int]
- `running_count`: Optional[int]

#### AssetType
- `type_id`: UUID
- `type_name`: str
- `calibration_interval`: Optional[float] (days)
- `maintenance_interval`: Optional[float] (days)
- `running_count_limit`: Optional[int]
- `total_count_limit`: Optional[int]
- `warning_threshold`: Optional[float] (0.0 - 1.0)
- `alarm_threshold`: Optional[float] (0.0 - 1.0)

#### AssetState (Enum)
- `OK`: Normal operation
- `WARNING`: Approaching limits
- `ALARM`: Limits exceeded
- `ERROR`: Hardware fault

#### AssetAlarmState (Enum)
- `OK`: No issues
- `WARNING`: Warning conditions
- `ALARM`: Alarm conditions

#### AssetLog
- `log_id`: UUID
- `asset_id`: UUID
- `asset_name`: str
- `timestamp`: datetime
- `message`: str
- `user`: Optional[str]

---

## Best Practices

1. **Use serial numbers consistently** - They're the primary identifier, make them meaningful

2. **Define asset types first** - Create asset types before creating assets

3. **Set calibration/maintenance intervals** - Define intervals in AssetType to enable automatic scheduling

4. **Use hierarchies for accuracy** - Model physical relationships (station → instruments)

5. **Increment children when using parent** - Set `increment_children=True` when incrementing station counts

6. **Track usage in test sequences** - Automatically increment counts during tests

7. **Reset running count after maintenance** - Clear running count to restart interval

8. **Add meaningful log messages** - Document repairs, config changes, relocations

9. **Monitor warning states** - Check warnings before they become alarms

10. **Store calibration certificates** - Use file operations to attach cal certs and manuals

11. **Regular health checks** - Run dashboard reports to catch issues early

12. **Don't delete assets** - Set state to inactive instead, preserve history

---

## Common Workflows

### Monthly Calibration Planning

```python
from datetime import datetime, timedelta

# Get all assets needing calibration in next 60 days
all_assets = api.asset.get_assets()
now = datetime.now()
cutoff = now + timedelta(days=60)

cal_schedule = []

for asset in all_assets:
    if asset.next_calibration_date and asset.next_calibration_date <= cutoff:
        days = (asset.next_calibration_date - now).days
        cal_schedule.append((asset, days))

# Sort by urgency
cal_schedule.sort(key=lambda x: x[1])

print("=== CALIBRATION SCHEDULE (60 days) ===")
for asset, days in cal_schedule:
    urgency = "🔴 OVERDUE" if days < 0 else "⚠️  URGENT" if days <= 7 else "📅"
    print(f"{urgency} {asset.asset_name}: {abs(days)} days {'overdue' if days < 0 else 'remaining'}")
```

### Post-Maintenance Workflow

```python
# After completing maintenance
asset_serial = "ICT-STATION-01"

# 1. Record maintenance
api.asset.record_maintenance(
    serial_number=asset_serial,
    comment="Quarterly PM: cleaned, lubricated, replaced worn parts"
)

# 2. Reset running count
api.asset.reset_running_count(
    serial_number=asset_serial,
    comment="Count reset after quarterly maintenance"
)

# 3. Set state to OK
from pywats.domains.asset import AssetState
api.asset.set_asset_state(
    serial_number=asset_serial,
    state=AssetState.OK
)

# 4. Add log entry
asset = api.asset.get_asset_by_serial(asset_serial)
api.asset.add_log_message(
    asset_id=str(asset.asset_id),
    message="Station returned to service after quarterly maintenance",
    user="maintenance.team"
)

print(f"{asset_serial} maintenance complete and returned to service")
```

---

## Troubleshooting

### Asset not found
```python
asset = api.asset.get_asset_by_serial("DMM-001")
if not asset:
    print("Asset doesn't exist - check serial number or create it")
```

### Cannot create asset without type
```python
# Always get type_id first
types = api.asset.get_asset_types()
if not types:
    print("No asset types defined - create types first")
else:
    type_id = types[0].type_id
    asset = api.asset.create_asset(serial_number="...", type_id=type_id, ...)
```

### Calibration/maintenance dates not updating
```python
# Make sure you're calling the right method
api.asset.record_calibration(serial_number="...", comment="...")
# NOT: api.asset.post_calibration() (that's lower level)

# Verify update
asset = api.asset.get_asset_by_serial("...")
print(f"Last cal: {asset.last_calibration_date}")
```

---

## See Also

- [Production Domain](PRODUCTION.md) - Using assets in production tests
- [Report Domain](REPORT.md) - Including station info in test reports
- [Process Domain](PROCESS.md) - Defining test operations that use assets
