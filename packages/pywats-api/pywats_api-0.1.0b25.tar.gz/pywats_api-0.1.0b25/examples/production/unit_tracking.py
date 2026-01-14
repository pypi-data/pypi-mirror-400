"""
Production Domain: Unit Tracking

This example demonstrates production unit tracking and management.
"""
import os
from datetime import datetime
from pywats import pyWATS

# =============================================================================
# Setup
# =============================================================================

api = pyWATS(
    base_url=os.environ.get("WATS_BASE_URL", "https://demo.wats.com"),
    token=os.environ.get("WATS_TOKEN", "")
)


# =============================================================================
# Get Unit Information
# =============================================================================

# Get unit by serial number
unit = api.production.get_unit("SN-2024-001234")

if unit:
    print(f"Unit: {unit.serialNumber}")
    print(f"  Part Number: {unit.partNumber}")
    print(f"  Part Revision: {unit.partRevision}")
    print(f"  Status: {unit.status}")
    print(f"  Current Phase: {unit.currentPhase}")
    print(f"  Created: {unit.created}")


# =============================================================================
# Create Unit
# =============================================================================

from pywats.domains.production import Unit

# Create a new production unit
new_unit = Unit(
    serialNumber="SN-2024-NEW-001",
    partNumber="WIDGET-001",
    partRevision="A",
    created=datetime.now(),
    status="Created"
)

result = api.production.create_unit(new_unit)
print(f"Created unit: {result.serialNumber}")


# =============================================================================
# Create Multiple Units (Batch)
# =============================================================================

# Generate serial numbers and create units
timestamp = datetime.now().strftime("%Y%m%d%H%M")
units = []

for i in range(10):
    serial = f"BATCH-{timestamp}-{i:04d}"
    unit = Unit(
        serialNumber=serial,
        partNumber="WIDGET-001",
        partRevision="A",
        created=datetime.now(),
        status="Created"
    )
    units.append(unit)

result = api.production.create_units(units)
print(f"Created {len(units)} units")


# =============================================================================
# Verify Unit
# =============================================================================

def verify_unit(serial_number: str, expected_part: str = None):
    """Verify a unit exists and matches expected configuration."""
    unit = api.production.get_unit(serial_number)
    
    if not unit:
        print(f"✗ Unit '{serial_number}' not found")
        return False
    
    print(f"✓ Unit found: {serial_number}")
    
    if expected_part and unit.partNumber != expected_part:
        print(f"✗ Part mismatch: expected {expected_part}, got {unit.partNumber}")
        return False
    
    print(f"✓ Part number: {unit.partNumber}")
    return True


# verify_unit("SN-2024-001234", "WIDGET-001")


# =============================================================================
# Update Unit Status
# =============================================================================

# Update status
api.production.update_unit_status("SN-2024-001234", "Testing")
print("Updated unit status to: Testing")


# =============================================================================
# Get Unit History
# =============================================================================

history = api.production.get_unit_history("SN-2024-001234")

print(f"\nHistory for SN-2024-001234:")
for entry in history:
    print(f"  {entry.timestamp}: {entry.event}")


# =============================================================================
# Search Units
# =============================================================================

from pywats.domains.report import WATSFilter

filter_data = WATSFilter(
    partNumber="WIDGET-001",
    status="Created"
)

units = api.production.search_units(filter_data)

print(f"\nFound {len(units)} created WIDGET-001 units:")
for unit in units[:5]:
    print(f"  {unit.serialNumber}")


# =============================================================================
# Unit Lifecycle Workflow
# =============================================================================

def unit_lifecycle_example():
    """Demonstrate complete unit lifecycle."""
    print("=" * 50)
    print("Unit Lifecycle Workflow")
    print("=" * 50)
    
    serial = f"DEMO-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    part_number = "WIDGET-001"
    
    # 1. Create unit
    print("\n1. Creating unit...")
    unit = Unit(
        serialNumber=serial,
        partNumber=part_number,
        partRevision="A",
        created=datetime.now(),
        status="Created"
    )
    api.production.create_unit(unit)
    print(f"   Created: {serial}")
    
    # 2. Start testing
    print("\n2. Starting test...")
    api.production.update_unit_status(serial, "Testing")
    
    # 3. Test complete
    print("\n3. Test complete...")
    api.production.update_unit_status(serial, "Tested")
    
    # 4. Check history
    print("\n4. Unit history:")
    history = api.production.get_unit_history(serial)
    for entry in history:
        print(f"   {entry.timestamp}: {entry.event}")
    
    print("\n" + "=" * 50)


# unit_lifecycle_example()
