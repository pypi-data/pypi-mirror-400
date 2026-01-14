# Production Module Usage Guide

## Overview

The Production module manages serial numbers, unit tracking, production phases, and assembly operations in WATS.

## Quick Start

```python
from pywats import pyWATS

api = pyWATS(base_url="https://wats.example.com", token="credentials")

# Get unit information
unit = api.production.get_unit("SN-12345")

# Verify unit status
verification = api.production.verify_unit("SN-12345")
print(f"Passing: {verification.is_passing}")

# Check if unit is passing
is_passing = api.production.is_unit_passing("SN-12345")
```

## Serial Number Management

### 1. Allocate Serial Numbers

```python
# Get available serial number types for a product
sn_types = api.production.get_serial_number_types("PART-001", "A")

for sn_type in sn_types:
    print(f"{sn_type.name}: {sn_type.pattern}")

# Allocate serial numbers (if using WATS allocation)
serial_numbers = api.production.allocate_serial_numbers(
    part_number="PART-001",
    revision="A",
    quantity=10,
    serial_type_id=1  # From get_serial_number_types
)

for sn in serial_numbers:
    print(f"Allocated: {sn}")
```

### 2. Manual Serial Numbers

```python
# For customer-provided or pre-existing serials
serial_number = "CUSTOMER-SN-001"

# Create unit with this serial (happens automatically on first test/operation)
# No explicit allocation needed
```

## Unit Operations

### 1. Get Unit Information

```python
# Get full unit details
unit = api.production.get_unit("SN-12345")

if unit:
    print(f"Serial: {unit.serial_number}")
    print(f"Part: {unit.part_number} Rev {unit.revision}")
    print(f"State: {unit.state}")
    print(f"Phase: {unit.phase}")
    print(f"Current Process: {unit.current_process}")
    print(f"Last Test: {unit.last_test_date}")
```

### 2. Create/Update Units

```python
from pywats.domains.production import Unit

# Units are typically created automatically when first tested
# But you can create them explicitly:

unit = Unit(
    serial_number="SN-NEW-001",
    part_number="PART-001",
    revision="A"
)

created_unit = api.production.create_unit(unit)
```

### 3. Set Unit Phase

```python
# Common phases:
# - "Undefined"
# - "Under Production - Queued"
# - "Under Production"
# - "Finalized"
# - "Scrapped"

# Set unit to production queue
api.production.set_unit_phase("SN-12345", "Under Production - Queued")

# Start production
api.production.set_unit_phase("SN-12345", "Under Production")

# Finalize after passing all tests
api.production.set_unit_phase("SN-12345", "Finalized")
```

### 4. Set Unit Process

```python
# Set current operation/process
# Process codes come from app.get_processes()

api.production.set_unit_process(
    serial_number="SN-12345",
    operation_type=100  # ICT, Final Test, etc.
)
```

### 5. Update Unit Tags

```python
# Add or update tags (metadata) on units
api.production.set_unit_tags("SN-12345", [
    {"key": "LotNumber", "value": "LOT-2025-W01"},
    {"key": "WorkOrder", "value": "WO-12345"},
    {"key": "Station", "value": "ICT-3"}
])
```

## Unit Verification

### 1. Verify Unit Status

```python
from pywats.domains.production.enums import UnitVerificationGrade

# Get verification with grade
verification = api.production.verify_unit("SN-12345")

print(f"Grade: {verification.grade}")
print(f"Passing: {verification.is_passing}")
print(f"Failed Steps: {verification.failed_step_count}")

# Check specific grades
if verification.grade == UnitVerificationGrade.PASSED:
    print("All tests passed")
elif verification.grade == UnitVerificationGrade.FAILED:
    print("Some tests failed")
elif verification.grade == UnitVerificationGrade.NOT_TESTED:
    print("Not yet tested")
```

### 2. Simple Pass/Fail Check

```python
# Quick check - returns boolean
if api.production.is_unit_passing("SN-12345"):
    print("Unit is passing")
    api.production.set_unit_phase("SN-12345", "Finalized")
else:
    print("Unit has failures")
    # Send to repair or scrap
```

### 3. Verification Grades

```python
from pywats.domains.production.enums import UnitVerificationGrade

# Available grades:
UnitVerificationGrade.PASSED          # All tests passed
UnitVerificationGrade.FAILED          # Has failures
UnitVerificationGrade.NOT_TESTED      # No test data
UnitVerificationGrade.PENDING         # Tests in progress
```

## Unit Changes (History)

### 1. Get Change History

```python
# Get all changes for a unit
changes = api.production.get_unit_changes("SN-12345")

for change in changes:
    print(f"{change.timestamp}: {change.change_type}")
    print(f"  Process: {change.process_name}")
    print(f"  Operator: {change.operator}")
    print(f"  Phase: {change.new_phase}")
```

### 2. Track Unit Lifecycle

```python
def print_unit_lifecycle(serial_number: str):
    """Print complete unit lifecycle"""
    changes = api.production.get_unit_changes(serial_number)
    
    print(f"\nLifecycle for {serial_number}:")
    print("=" * 60)
    
    for change in sorted(changes, key=lambda c: c.timestamp):
        print(f"{change.timestamp:%Y-%m-%d %H:%M:%S}")
        print(f"  Type: {change.change_type}")
        print(f"  Process: {change.process_name or 'N/A'}")
        print(f"  Phase: {change.old_phase} → {change.new_phase}")
        print()
```

## Assembly Operations

### 1. Verify Assembly (Box Build)

```python
# Check if all required subunits are present
verification = api.production.verify_assembly(
    parent_serial="MODULE-SN-001",
    parent_part="MODULE-100",
    parent_revision="A"
)

print(f"Complete: {verification.is_complete}")
print(f"Missing parts: {verification.missing_count}")

for missing in verification.missing_parts:
    print(f"  - {missing.part_number} at index {missing.index}")
```

### 2. Build Assembly

```python
# Add subunit to assembly (using production service)
api.production.add_child_to_assembly(
    parent_serial="MODULE-SN-001",
    child_serial="PCBA-SN-123",
    index=0  # Position in assembly (from box build template)
)

# Add another subunit
api.production.add_child_to_assembly(
    parent_serial="MODULE-SN-001",
    child_serial="PCBA-SN-124",
    index=1
)

# Verify assembly is complete
verification = api.production.verify_assembly("MODULE-SN-001", "MODULE-100", "A")
if verification.is_complete:
    print("Assembly complete!")
```

### 3. Disassemble

```python
# Remove subunit from assembly
api.production.remove_child_from_assembly(
    parent_serial="MODULE-SN-001",
    index=0  # Position to remove
)
```

## Production Batches

### 1. Track Batch/Lot

```python
# Group units by batch using tags
batch_number = "BATCH-2025-W01"

# Set batch on units as they're created
for serial in serial_numbers:
    api.production.set_unit_tags(serial, [
        {"key": "LotNumber", "value": batch_number},
        {"key": "ManufactureDate", "value": "2025-01-15"}
    ])
```

### 2. Query Batch Units

```python
# Get all units in batch (via report query)
from pywats.domains.report import WATSFilter

filter = WATSFilter(tags=[
    {"key": "LotNumber", "value": "BATCH-2025-W01"}
])

reports = api.report.query_uut_headers(filter)
batch_serials = [r.serial_number for r in reports]

print(f"Batch has {len(batch_serials)} units")
```

## Common Patterns

### Pattern 1: Complete Production Workflow

```python
def production_workflow(serial_number: str, part_number: str, revision: str):
    """Complete workflow from creation to finalization"""
    
    # 1. Set to production queue
    api.production.set_unit_phase(serial_number, "Under Production - Queued")
    api.production.set_unit_tags(serial_number, [
        {"key": "LotNumber", "value": "LOT-2025-W01"},
        {"key": "StartDate", "value": datetime.now().isoformat()}
    ])
    
    # 2. Start production - ICT
    api.production.set_unit_phase(serial_number, "Under Production")
    api.production.set_unit_process(serial_number, operation_type=10)  # ICT
    
    # Run ICT test (creates UUT report)
    # ... test code ...
    
    # 3. Move to next operation - Final Test
    api.production.set_unit_process(serial_number, operation_type=50)
    
    # Run final test
    # ... test code ...
    
    # 4. Verify and finalize
    if api.production.is_unit_passing(serial_number):
        api.production.set_unit_phase(serial_number, "Finalized")
        print(f"{serial_number}: Production complete")
    else:
        print(f"{serial_number}: Failed - send to repair")
```

### Pattern 2: Assembly Build Workflow

```python
def build_module(module_sn: str, pcba_serials: list):
    """Build module from PCBAs"""
    
    MODULE_PART = "MODULE-100"
    MODULE_REV = "A"
    
    # 1. Create module unit
    api.production.set_unit_phase(module_sn, "Under Production - Queued")
    
    # 2. Verify all PCBAs are passing
    for pcba_sn in pcba_serials:
        if not api.production.is_unit_passing(pcba_sn):
            raise ValueError(f"PCBA {pcba_sn} is not passing")
    
    # 3. Build assembly
    for index, pcba_sn in enumerate(pcba_serials):
        api.production.add_child_to_assembly(
            parent_serial=module_sn,
            child_serial=pcba_sn,
            index=index
        )
    
    # 4. Verify assembly complete
    verification = api.production.verify_assembly(module_sn, MODULE_PART, MODULE_REV)
    if not verification.is_complete:
        raise ValueError(f"Assembly incomplete: {verification.missing_parts}")
    
    # 5. Test module
    api.production.set_unit_phase(module_sn, "Under Production")
    api.production.set_unit_process(module_sn, operation_type=100)
    
    # ... run module tests ...
    
    # 6. Finalize if passing
    if api.production.is_unit_passing(module_sn):
        api.production.set_unit_phase(module_sn, "Finalized")
```

### Pattern 3: Repair Workflow

```python
def repair_workflow(serial_number: str):
    """Handle failed unit repair"""
    
    # 1. Check current status
    verification = api.production.verify_unit(serial_number)
    
    if verification.is_passing:
        print("Unit is already passing")
        return
    
    # 2. Create UUR (repair) report
    from pywats.models import UURReport
    
    # Get last test to determine failure
    unit = api.production.get_unit(serial_number)
    
    # Create repair report
    uur = api.report.create_uur_from_part_and_process(
        part_number=unit.part_number,
        serial_number=serial_number,
        revision=unit.revision,
        process_code=unit.current_process,
        failure_category=500,  # Your failure category
        failure_code=501,      # Specific failure
        description="Repair performed",
        operator="Repair Tech"
    )
    
    api.report.send_uur_report(uur)
    
    # 3. Retest
    api.production.set_unit_process(serial_number, operation_type=unit.current_process)
    
    # ... run test again ...
    
    # 4. Check if now passing
    if api.production.is_unit_passing(serial_number):
        print(f"{serial_number}: Repair successful")
    else:
        print(f"{serial_number}: Still failing - escalate")
```

### Pattern 4: Production Dashboard

```python
def production_dashboard(part_number: str):
    """Show production status for a product"""
    
    # Get all reports for product
    from pywats.domains.report import WATSFilter
    from datetime import datetime, timedelta
    
    filter = WATSFilter(
        part_number=part_number,
        date_from=datetime.now() - timedelta(days=7)
    )
    
    headers = api.report.query_uut_headers(filter)
    
    # Analyze
    total = len(headers)
    passed = len([h for h in headers if h.passed])
    failed = total - passed
    
    print(f"\n{part_number} Production Status (Last 7 Days)")
    print("=" * 60)
    print(f"Total Tested: {total}")
    print(f"Passed: {passed} ({passed/total*100:.1f}%)")
    print(f"Failed: {failed} ({failed/total*100:.1f}%)")
    
    # Show units in production
    in_production = []
    for header in headers:
        unit = api.production.get_unit(header.serial_number)
        if unit and unit.phase == "Under Production":
            in_production.append(unit.serial_number)
    
    print(f"\nCurrently in production: {len(in_production)}")
    for sn in in_production[:10]:  # Show first 10
        print(f"  - {sn}")
```

## Best Practices

### 1. Use Phases Consistently

```python
# ✓ Good - proper flow
api.production.set_unit_phase(sn, "Under Production - Queued")  # 1. Queued
api.production.set_unit_phase(sn, "Under Production")           # 2. Testing
api.production.set_unit_phase(sn, "Finalized")                  # 3. Done

# ✗ Avoid - skipping phases
api.production.set_unit_phase(sn, "Finalized")  # Directly (missing history)
```

### 2. Verify Before Finalizing

```python
# ✓ Good - always check
if api.production.is_unit_passing(sn):
    api.production.set_unit_phase(sn, "Finalized")
else:
    # Handle failure

# ✗ Avoid - finalizing without checking
api.production.set_unit_phase(sn, "Finalized")  # What if it failed?
```

### 3. Track with Tags

```python
# ✓ Good - comprehensive tracking
api.production.set_unit_tags(sn, [
    {"key": "LotNumber", "value": "LOT-001"},
    {"key": "WorkOrder", "value": "WO-12345"},
    {"key": "Station", "value": "ICT-3"},
    {"key": "Operator", "value": "John Doe"}
])

# ✗ Avoid - minimal tracking
# (Hard to trace issues later)
```

### 4. Validate Assembly Order

```python
# ✓ Good - build in order
for index, pcba_sn in enumerate(pcba_serials):
    api.production.add_child_to_assembly(module_sn, pcba_sn, index)

# ✗ Avoid - wrong indices
api.production.add_child_to_assembly(module_sn, pcba1, 1)  # Should be 0
api.production.add_child_to_assembly(module_sn, pcba2, 0)  # Should be 1
```

## Troubleshooting

### Unit Not Found

```python
# Units are created on first test or explicit creation
unit = api.production.get_unit("NEW-SN-001")
if not unit:
    print("Unit will be created on first test")
```

### Assembly Verification Failing

```python
# Check template definition
template = api.product_internal.get_box_build_template("MODULE-100", "A")
print(f"Required subunits: {len(template.subunits)}")

# Verify each subunit
verification = api.production.verify_assembly("MODULE-SN-001", "MODULE-100", "A")
for missing in verification.missing_parts:
    print(f"Missing: {missing.part_number} at index {missing.index}")
```

### Process Code Not Found

```python
# Get available process codes
processes = api.app.get_processes()
for proc in processes:
    print(f"{proc.code}: {proc.name}")
```

## Related Documentation

- [Report Module](REPORT_MODULE.md) - For creating test reports
- [Product Module](PRODUCT_MODULE.md) - For product/BOM setup
- [Architecture](../ARCHITECTURE.md) - Overall system design
