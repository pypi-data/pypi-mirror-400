# Production Domain

The Production domain manages units (individual physical products) throughout their manufacturing lifecycle. It tracks unit creation, phases, processes, verification status, assembly relationships, and change history. This domain is where you track ACTUAL units being manufactured, from creation to finalization.

> **⚠️ IMPORTANT: Server Feature Requirement**
>
> The Production module is an optional feature that **must be enabled on the WATS server by the WATS team**. If production tracking is not enabled on your server, this module will not work and API calls will fail.
>
> Contact your WATS administrator or the WATS support team to verify that production tracking is enabled for your server before using this module.

## Table of Contents

- [Quick Start](#quick-start)
- [Core Concepts](#core-concepts)
- [Unit Operations](#unit-operations)
- [Unit Verification](#unit-verification)
- [Phase Management](#phase-management)
- [Process Tracking](#process-tracking)
- [Assembly Management](#assembly-management)
- [Serial Number Allocation](#serial-number-allocation)
- [Unit Changes](#unit-changes)
- [Unit Phases (Internal)](#unit-phases-internal)
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

# Get a production unit
unit = api.production.get_unit(
    serial_number="WIDGET-12345",
    part_number="WIDGET-001"
)

print(f"Unit: {unit.serial_number}")
print(f"Part: {unit.part_number} Rev {unit.part_revision}")
print(f"Status: {unit.status}")
print(f"Current Phase: {unit.current_phase}")
print(f"Current Process: {unit.current_process}")

# Check if unit is passing all tests
if api.production.is_unit_passing("WIDGET-12345", "WIDGET-001"):
    print("✓ Unit is passing all tests")
    
    # Move to finalized phase
    api.production.set_unit_phase(
        serial_number="WIDGET-12345",
        part_number="WIDGET-001",
        phase="Finalized"
    )
else:
    print("✗ Unit has test failures")

# Create a new unit
from pywats.domains.production import Unit

new_unit = Unit(
    serial_number="WIDGET-12346",
    part_number="WIDGET-001",
    part_revision="B",
    status="In Production"
)

created = api.production.create_units([new_unit])
```

---

## Core Concepts

### Unit
A **Unit** represents a single physical product being manufactured. Each unit has a unique serial number and is associated with a product/revision.

**Key attributes:**
- `serial_number`: Unique identifier for this specific unit
- `part_number`: Product being manufactured
- `part_revision`: Product revision
- `status`: Current status (e.g., "In Production", "Tested", "Shipped")
- `current_phase`: Current workflow phase (e.g., "ICT", "FCT", "Finalized")
- `current_process`: Current operation type code (e.g., 10 for ICT, 50 for FCT)

### Unit Lifecycle
Units typically follow this lifecycle:

1. **Creation** - Unit is created in the system
2. **In Production** - Unit enters manufacturing
3. **Testing** - Unit goes through test operations (ICT, FCT, etc.)
4. **Verification** - Test results are verified (Pass/Fail)
5. **Repair** (if failed) - Failed units go to repair
6. **Assembly** (if applicable) - Subunits are attached
7. **Finalized** - Unit passes all requirements and is finalized
8. **Shipped** - Unit is shipped to customer

### Unit Phase
A **Unit Phase** represents a stage in the production workflow. Phases are configured in WATS and can include:

- **In Test** - Unit is currently being tested
- **Passed** - Unit passed the current test
- **Failed** - Unit failed the current test
- **In Repair** - Unit is being repaired
- **Finalized** - Unit completed all requirements
- **Scrapped** - Unit was scrapped

Phases can be referenced by:
- **ID**: Numeric identifier (e.g., 123)
- **Code**: Phase code string (e.g., "ICT_PASSED")
- **Name**: Display name (e.g., "ICT - Passed")

### Unit Verification
**UnitVerification** provides test result status:

**Grades:**
- `PASSED`: All tests passed
- `FAILED`: Some tests failed
- `NOT_TESTED`: Unit hasn't been tested yet
- `INCOMPLETE`: Testing in progress

### Assembly
Units can have **parent-child relationships** to represent product assemblies:

- A **Main Assembly** unit can have multiple **Subunit** children
- Each child is attached at a specific **position** or slot
- Children must be **finalized** before attachment
- Assembly structure must match the **Box Build Template** (defined in Product domain)

**Key distinction:**
- **Box Build Template** (Product domain): Defines WHAT subunits are REQUIRED (design)
- **Unit Assembly** (Production domain): Attaches ACTUAL units (production)

---

## Unit Operations

### Get Specific Unit

```python
# Get unit by serial number and part number
unit = api.production.get_unit(
    serial_number="WIDGET-12345",
    part_number="WIDGET-001"
)

if unit:
    print(f"Serial: {unit.serial_number}")
    print(f"Part: {unit.part_number} Rev {unit.part_revision}")
    print(f"Status: {unit.status}")
    print(f"Phase: {unit.current_phase}")
    print(f"Process: {unit.current_process}")
    print(f"Created: {unit.created}")
    print(f"Modified: {unit.modified}")
    
    # Check if unit has Product info attached
    if unit.product:
        print(f"Product Name: {unit.product.name}")
    
    if unit.product_revision:
        print(f"Revision Name: {unit.product_revision.name}")
```

### Create Units

```python
from pywats.domains.production import Unit
from datetime import datetime

# Create single unit
unit = Unit(
    serial_number="WIDGET-NEW-001",
    part_number="WIDGET-001",
    part_revision="C",
    status="Created"
)

created = api.production.create_units([unit])
print(f"Created: {created[0].serial_number}")

# Create multiple units in batch
units = [
    Unit(
        serial_number=f"BATCH-{i:04d}",
        part_number="WIDGET-001",
        part_revision="C",
        status="Created",
        created=datetime.now()
    )
    for i in range(1, 11)  # Create 10 units
]

created_units = api.production.create_units(units)
print(f"Created {len(created_units)} units")
```

### Update Unit

```python
# Get unit
unit = api.production.get_unit("WIDGET-12345", "WIDGET-001")

# Modify fields
unit.status = "Testing"
unit.location = "Test Station 3"

# Save changes
updated = api.production.update_unit(unit)
print(f"Updated: {updated.serial_number}")
```

---

## Unit Verification

Check if a unit is passing or failing tests.

### Verify Unit Status

```python
from pywats.domains.production import UnitVerificationGrade

# Get detailed verification
verification = api.production.verify_unit(
    serial_number="WIDGET-12345",
    part_number="WIDGET-001",
    revision="B"
)

if verification:
    print(f"Verification Grade: {verification.grade}")
    print(f"Is Passing: {verification.is_passing}")
    print(f"Failed Steps: {verification.failed_step_count}")
    print(f"Passed Steps: {verification.passed_step_count}")
    
    # Check specific grade
    if verification.grade == UnitVerificationGrade.PASSED:
        print("✓ All tests passed")
    elif verification.grade == UnitVerificationGrade.FAILED:
        print("✗ Some tests failed")
    elif verification.grade == UnitVerificationGrade.NOT_TESTED:
        print("⚠ Unit not yet tested")
    elif verification.grade == UnitVerificationGrade.INCOMPLETE:
        print("⏳ Testing in progress")
```

### Get Unit Grade

```python
# Get just the grade (simpler than full verification)
grade = api.production.get_unit_grade(
    serial_number="WIDGET-12345",
    part_number="WIDGET-001"
)

if grade == UnitVerificationGrade.PASSED:
    print("Ready for next phase")
```

### Simple Pass/Fail Check

```python
# Quick boolean check
if api.production.is_unit_passing("WIDGET-12345", "WIDGET-001"):
    print("✓ Unit is passing - can proceed")
    
    # Finalize the unit
    api.production.set_unit_phase(
        serial_number="WIDGET-12345",
        part_number="WIDGET-001",
        phase="Finalized"
    )
else:
    print("✗ Unit has failures - needs repair")
    
    # Send to repair
    api.production.set_unit_phase(
        serial_number="WIDGET-12345",
        part_number="WIDGET-001",
        phase="In Repair"
    )
```

---

## Phase Management

Manage unit workflow phases.

### Get All Phases

```python
# Get all available phases
phases = api.production.get_phases()

print("Available Phases:")
for phase in phases:
    print(f"  ID: {phase.unit_phase_id}")
    print(f"  Code: {phase.code}")
    print(f"  Name: {phase.name}")
    print(f"  Flag: {phase.phase_flags}")
    print()
```

### Get Specific Phase

```python
# By phase ID
phase = api.production.get_phase(123)

# By phase code
phase = api.production.get_phase("ICT_PASSED")

# By phase name
phase = api.production.get_phase("ICT - Passed")

if phase:
    print(f"Found phase: {phase.name} (ID: {phase.unit_phase_id})")
```

### Set Unit Phase

```python
# Set phase by name
api.production.set_unit_phase(
    serial_number="WIDGET-12345",
    part_number="WIDGET-001",
    phase="ICT",
    comment="Starting ICT test"
)

# Set phase by ID
api.production.set_unit_phase(
    serial_number="WIDGET-12345",
    part_number="WIDGET-001",
    phase=123,  # Phase ID
    comment="Moving to next phase"
)

# Set phase using enum
from pywats.domains.production import UnitPhaseFlag

api.production.set_unit_phase(
    serial_number="WIDGET-12345",
    part_number="WIDGET-001",
    phase=UnitPhaseFlag.FINALIZED,
    comment="Unit completed successfully"
)
```

---

## Process Tracking

Track which test operation a unit is currently at.

### Set Unit Process

```python
# Set process by operation type code
# (Operation types are defined in the Process domain)

# Set to ICT (operation type 10)
api.production.set_unit_process(
    serial_number="WIDGET-12345",
    part_number="WIDGET-001",
    process_code=10,  # ICT
    comment="Starting In-Circuit Test"
)

# Set to FCT (operation type 50)
api.production.set_unit_process(
    serial_number="WIDGET-12345",
    part_number="WIDGET-001",
    process_code=50,  # Final Function Test
    comment="Starting Final Test"
)

# Clear process (set to None)
api.production.set_unit_process(
    serial_number="WIDGET-12345",
    part_number="WIDGET-001",
    process_code=None,
    comment="Process completed"
)
```

---

## Assembly Management

Manage parent-child unit relationships for box builds.

### Add Child to Assembly

```python
# Prerequisites:
# 1. Box build template must define the child as valid (Product domain)
# 2. Child unit must be finalized
# 3. Child cannot already have a parent

# Add a child unit to parent assembly
success = api.production.add_child_to_assembly(
    parent_serial="MODULE-001",
    parent_part="MAIN-MODULE",
    child_serial="PCBA-12345",
    child_part="PCBA-BOARD"
)

if success:
    print("Child added to assembly")
```

### Remove Child from Assembly

```python
# Remove a child unit from parent
success = api.production.remove_child_from_assembly(
    parent_serial="MODULE-001",
    parent_part="MAIN-MODULE",
    child_serial="PCBA-12345",
    child_part="PCBA-BOARD"
)

if success:
    print("Child removed from assembly")
```

### Verify Assembly

```python
# Check if assembly is complete (all required children attached)
verification = api.production.verify_assembly(
    serial_number="MODULE-001",
    part_number="MAIN-MODULE",
    revision="A"
)

if verification:
    print(f"Assembly Complete: {verification.get('is_complete', False)}")
    
    if not verification.get('is_complete'):
        missing = verification.get('missing_children', [])
        print(f"Missing {len(missing)} required children:")
        for child in missing:
            print(f"  - {child.get('part_number')}")
```

### Complete Assembly Workflow

```python
# 1. Define what subunits are required (Product domain)
template = api.product_internal.get_box_build("MAIN-MODULE", "A")
template.add_subunit("PCBA-BOARD", "A", quantity=1)
template.add_subunit("POWER-SUPPLY", "B", quantity=1)
template.add_subunit("CABLE-ASSY", "A", quantity=2)
template.save()

# 2. Create parent unit
from pywats.domains.production import Unit

parent = Unit(
    serial_number="MODULE-001",
    part_number="MAIN-MODULE",
    part_revision="A"
)
api.production.create_units([parent])

# 3. Create and finalize child units
pcba = Unit(serial_number="PCBA-001", part_number="PCBA-BOARD", part_revision="A")
psu = Unit(serial_number="PSU-001", part_number="POWER-SUPPLY", part_revision="B")
cable1 = Unit(serial_number="CABLE-001", part_number="CABLE-ASSY", part_revision="A")
cable2 = Unit(serial_number="CABLE-002", part_number="CABLE-ASSY", part_revision="A")

api.production.create_units([pcba, psu, cable1, cable2])

# Test and finalize children (simplified - would actually run tests)
for child in [pcba, psu, cable1, cable2]:
    api.production.set_unit_phase(
        child.serial_number,
        child.part_number,
        phase="Finalized"
    )

# 4. Attach children to parent
api.production.add_child_to_assembly("MODULE-001", "MAIN-MODULE", "PCBA-001", "PCBA-BOARD")
api.production.add_child_to_assembly("MODULE-001", "MAIN-MODULE", "PSU-001", "POWER-SUPPLY")
api.production.add_child_to_assembly("MODULE-001", "MAIN-MODULE", "CABLE-001", "CABLE-ASSY")
api.production.add_child_to_assembly("MODULE-001", "MAIN-MODULE", "CABLE-002", "CABLE-ASSY")

# 5. Verify assembly is complete
verification = api.production.verify_assembly("MODULE-001", "MAIN-MODULE", "A")

if verification.get('is_complete'):
    print("✓ Assembly complete - all required children attached")
    
    # Finalize the parent
    api.production.set_unit_phase("MODULE-001", "MAIN-MODULE", phase="Finalized")
else:
    print("✗ Assembly incomplete")
```

---

## Serial Number Allocation

Allocate serial numbers from configured sequences.

### Get Serial Number Types

```python
# Get all serial number types
sn_types = api.production.get_serial_number_types()

print("Serial Number Types:")
for sn_type in sn_types:
    print(f"  {sn_type.name}")
    print(f"    Pattern: {sn_type.pattern}")
    print(f"    Next: {sn_type.next_number}")
```

### Allocate Serial Numbers

```python
# Allocate a single serial number
serial_numbers = api.production.allocate_serial_numbers(
    type_name="Production_SN",
    quantity=1
)

if serial_numbers:
    new_sn = serial_numbers[0]
    print(f"Allocated: {new_sn}")

# Allocate multiple serial numbers
batch_sns = api.production.allocate_serial_numbers(
    type_name="Production_SN",
    quantity=100
)

print(f"Allocated {len(batch_sns)} serial numbers:")
print(f"  First: {batch_sns[0]}")
print(f"  Last: {batch_sns[-1]}")

# Use allocated serial numbers to create units
from pywats.domains.production import Unit

units = [
    Unit(
        serial_number=sn,
        part_number="WIDGET-001",
        part_revision="B"
    )
    for sn in batch_sns
]

api.production.create_units(units)
```

---

## Unit Changes

Track changes to unit phase and status.

### Get Unit Changes

```python
# Get all changes for a specific unit
changes = api.production.get_unit_changes(
    serial_number="WIDGET-12345",
    part_number="WIDGET-001"
)

print(f"Unit change history ({len(changes)} changes):")
for change in changes:
    print(f"  {change.changed}: Phase {change.old_unit_phase_id} → {change.new_unit_phase_id}")
    print(f"    User: {change.user or 'System'}")
    print(f"    Comment: {change.comment or 'No comment'}")

# Get recent changes (all units, last 50)
recent_changes = api.production.get_unit_changes(top=50)

print(f"Recent changes across all units:")
for change in recent_changes[:10]:
    print(f"  {change.serial_number}: {change.comment or 'Phase change'}")
```

### Acknowledge Unit Change

```python
# Mark a change as acknowledged
change_id = "some-change-uuid"

success = api.production.acknowledge_unit_change(change_id)

if success:
    print("Change acknowledged")
```

---

## Unit Phases (Internal)

⚠️ **INTERNAL API - Subject to change**

Get unit phase definitions from internal API.

### Get Unit Phases

```python
# Get all unit phases from internal API
phases = api.production_internal.get_unit_phases()

print("Unit Phases (Internal API):")
for phase in phases:
    print(f"  {phase.name} (ID: {phase.unit_phase_id})")
    print(f"    Code: {phase.code}")
    print(f"    Flags: {phase.phase_flags}")
    print(f"    Description: {phase.description or 'N/A'}")
```

---

## Advanced Usage

### Complete Production Workflow

```python
def production_workflow(serial_number, part_number, revision):
    """Complete workflow from creation to finalization"""
    
    # 1. Create unit
    from pywats.domains.production import Unit
    
    unit = Unit(
        serial_number=serial_number,
        part_number=part_number,
        part_revision=revision,
        status="Created"
    )
    api.production.create_units([unit])
    print(f"1. Created unit: {serial_number}")
    
    # 2. Start production - Set to ICT
    api.production.set_unit_phase(
        serial_number, part_number,
        phase="Under Production"
    )
    
    api.production.set_unit_process(
        serial_number, part_number,
        process_code=10,  # ICT
        comment="Starting In-Circuit Test"
    )
    print("2. Set to ICT process")
    
    # 3. Run ICT test (this would create a UUT report)
    # ... test execution code ...
    # api.report.submit_report(ict_report)
    print("3. ICT test completed")
    
    # 4. Check if passed
    if api.production.is_unit_passing(serial_number, part_number):
        print("4. ICT PASSED")
        
        # Move to FCT
        api.production.set_unit_process(
            serial_number, part_number,
            process_code=50,  # FCT
            comment="Starting Final Function Test"
        )
        print("5. Set to FCT process")
        
        # Run FCT test
        # ... test execution code ...
        # api.report.submit_report(fct_report)
        print("6. FCT test completed")
        
        # Check final result
        if api.production.is_unit_passing(serial_number, part_number):
            print("7. FCT PASSED")
            
            # Finalize unit
            api.production.set_unit_phase(
                serial_number, part_number,
                phase="Finalized",
                comment="All tests passed successfully"
            )
            print("8. Unit FINALIZED ✓")
            return True
        else:
            print("7. FCT FAILED")
            # Send to repair
            api.production.set_unit_phase(
                serial_number, part_number,
                phase="In Repair"
            )
            return False
    else:
        print("4. ICT FAILED")
        # Send to repair
        api.production.set_unit_phase(
            serial_number, part_number,
            phase="In Repair"
        )
        return False

# Use it
production_workflow("WIDGET-12345", "WIDGET-001", "B")
```

### Repair Workflow

```python
def repair_workflow(serial_number, part_number):
    """Handle failed unit repair and retest"""
    
    # 1. Check current status
    verification = api.production.verify_unit(serial_number, part_number)
    
    if verification.is_passing:
        print("Unit is already passing - no repair needed")
        return True
    
    print(f"Unit has {verification.failed_step_count} failed steps")
    
    # 2. Set to repair phase
    api.production.set_unit_phase(
        serial_number, part_number,
        phase="In Repair",
        comment="Starting repair"
    )
    
    # 3. Create repair report (UUR - Unit Under Repair)
    # This would typically be done by creating a UUR report
    # See Report domain documentation for details
    
    # 4. Set back to test process
    unit = api.production.get_unit(serial_number, part_number)
    
    api.production.set_unit_process(
        serial_number, part_number,
        process_code=unit.current_process,  # Return to failed operation
        comment="Re-testing after repair"
    )
    
    # 5. Run test again
    # ... test execution code ...
    
    # 6. Check if now passing
    if api.production.is_unit_passing(serial_number, part_number):
        print("✓ Repair successful - unit now passing")
        
        # Move to next phase
        api.production.set_unit_phase(
            serial_number, part_number,
            phase="Passed",
            comment="Passed after repair"
        )
        return True
    else:
        print("✗ Still failing after repair - escalate")
        
        # Could scrap or send to advanced repair
        api.production.set_unit_phase(
            serial_number, part_number,
            phase="Failed",
            comment="Failed after repair attempt"
        )
        return False

# Use it
repair_workflow("WIDGET-12345", "WIDGET-001")
```

### Batch Production Tracking

```python
def batch_production(part_number, revision, lot_number, quantity=100):
    """Create and track a production batch"""
    from pywats.domains.production import Unit
    from datetime import datetime
    
    # 1. Allocate serial numbers
    serial_numbers = api.production.allocate_serial_numbers(
        type_name="Production_SN",
        quantity=quantity
    )
    
    print(f"Allocated {quantity} serial numbers")
    print(f"  Range: {serial_numbers[0]} to {serial_numbers[-1]}")
    
    # 2. Create units
    units = [
        Unit(
            serial_number=sn,
            part_number=part_number,
            part_revision=revision,
            status="Created",
            lot_number=lot_number  # If your Unit model has this field
        )
        for sn in serial_numbers
    ]
    
    created = api.production.create_units(units)
    print(f"Created {len(created)} units in lot {lot_number}")
    
    # 3. Track batch progress
    batch_stats = {
        'created': len(created),
        'tested': 0,
        'passed': 0,
        'failed': 0,
        'in_repair': 0,
        'finalized': 0
    }
    
    # After testing, update stats
    for sn in serial_numbers:
        unit = api.production.get_unit(sn, part_number)
        
        if unit.current_phase:
            if "Finalized" in unit.current_phase:
                batch_stats['finalized'] += 1
            elif "Repair" in unit.current_phase:
                batch_stats['in_repair'] += 1
            elif "Passed" in unit.current_phase:
                batch_stats['passed'] += 1
            elif "Failed" in unit.current_phase:
                batch_stats['failed'] += 1
    
    print("\nBatch Statistics:")
    print(f"  Created: {batch_stats['created']}")
    print(f"  Finalized: {batch_stats['finalized']}")
    print(f"  Passed: {batch_stats['passed']}")
    print(f"  Failed: {batch_stats['failed']}")
    print(f"  In Repair: {batch_stats['in_repair']}")
    
    yield_pct = (batch_stats['finalized'] / batch_stats['created']) * 100
    print(f"\nYield: {yield_pct:.1f}%")
    
    return batch_stats

# Use it
stats = batch_production("WIDGET-001", "C", "LOT-2025-W01", quantity=50)
```

### Phase Gate Checks

```python
def can_advance_to_next_phase(serial_number, part_number, target_phase):
    """Check if unit can advance to next phase"""
    
    # Get current unit state
    unit = api.production.get_unit(serial_number, part_number)
    
    if not unit:
        print("Unit not found")
        return False
    
    # Check verification
    verification = api.production.verify_unit(serial_number, part_number)
    
    if not verification:
        print("Cannot verify unit")
        return False
    
    # Define phase gate rules
    if target_phase == "Finalized":
        # Must be passing all tests
        if not verification.is_passing:
            print(f"✗ Cannot finalize - unit has {verification.failed_step_count} failures")
            return False
        
        # Must not be in repair
        if unit.current_phase and "Repair" in unit.current_phase:
            print("✗ Cannot finalize - unit is in repair")
            return False
        
        print("✓ Unit can be finalized")
        return True
    
    elif target_phase == "Shipped":
        # Must be finalized first
        if not unit.current_phase or "Finalized" not in unit.current_phase:
            print("✗ Cannot ship - unit not finalized")
            return False
        
        print("✓ Unit can be shipped")
        return True
    
    # Add more phase gate rules as needed
    return True

# Use it
if can_advance_to_next_phase("WIDGET-12345", "WIDGET-001", "Finalized"):
    api.production.set_unit_phase("WIDGET-12345", "WIDGET-001", "Finalized")
```

---

## API Reference

### ProductionService Methods

#### Unit Operations
- `get_unit(serial_number, part_number)` → `Optional[Unit]` - Get unit details
- `create_units(units)` → `List[Unit]` - Create one or more units
- `update_unit(unit)` → `Optional[Unit]` - Update existing unit

#### Unit Verification
- `verify_unit(serial_number, part_number, revision)` → `Optional[UnitVerification]` - Get verification details
- `get_unit_grade(serial_number, part_number, revision)` → `Optional[UnitVerificationGrade]` - Get grade only
- `is_unit_passing(serial_number, part_number)` → `bool` - Quick pass/fail check

#### Unit Phases
- `get_phases()` → `List[UnitPhase]` - Get all available phases
- `get_phase(identifier)` → `Optional[UnitPhase]` - Get specific phase by ID/code/name
- `get_phase_id(phase)` → `Optional[int]` - Get phase ID from identifier
- `set_unit_phase(serial_number, part_number, phase, comment)` → `bool` - Set unit phase
- `set_unit_process(serial_number, part_number, process_code, comment)` → `bool` - Set current process

#### Unit Changes
- `get_unit_changes(serial_number, part_number, top)` → `List[UnitChange]` - Get change history
- `acknowledge_unit_change(change_id)` → `bool` - Acknowledge a change

#### Assembly Operations
- `add_child_to_assembly(parent_serial, parent_part, child_serial, child_part)` → `bool` - Add child unit
- `remove_child_from_assembly(parent_serial, parent_part, child_serial, child_part)` → `bool` - Remove child unit
- `verify_assembly(serial_number, part_number, revision)` → `Optional[Dict]` - Verify assembly completeness

#### Serial Number Operations
- `get_serial_number_types()` → `List[SerialNumberType]` - Get SN types
- `allocate_serial_numbers(type_name, quantity)` → `List[str]` - Allocate serial numbers

### ProductionServiceInternal Methods (⚠️ Subject to change)

#### Unit Phase Operations
- `get_unit_phases()` → `List[UnitPhase]` - Get unit phases from internal API

### Models

#### Unit
- `serial_number`: str (required)
- `part_number`: str (required)
- `part_revision`: Optional[str]
- `status`: Optional[str]
- `current_phase`: Optional[str]
- `current_process`: Optional[int]
- `product`: Optional[Product] (attached)
- `product_revision`: Optional[ProductRevision] (attached)
- `created`: Optional[datetime]
- `modified`: Optional[datetime]

#### UnitVerification
- `grade`: UnitVerificationGrade
- `is_passing`: bool
- `failed_step_count`: int
- `passed_step_count`: int

#### UnitVerificationGrade (Enum)
- `PASSED`: All tests passed
- `FAILED`: Some tests failed
- `NOT_TESTED`: Not yet tested
- `INCOMPLETE`: Testing in progress

#### UnitPhase
- `unit_phase_id`: int
- `code`: str
- `name`: str
- `phase_flags`: Optional[int]
- `description`: Optional[str]

#### UnitPhaseFlag (Enum)
- Numeric values for common phases
- Example: `UnitPhaseFlag.FINALIZED`

#### UnitChange
- `unit_change_id`: UUID
- `serial_number`: str
- `part_number`: str
- `old_unit_phase_id`: Optional[int]
- `new_unit_phase_id`: Optional[int]
- `changed`: datetime
- `user`: Optional[str]
- `comment`: Optional[str]

#### SerialNumberType
- `name`: str
- `pattern`: str
- `next_number`: int

---

## Best Practices

1. **Always verify before finalizing** - Check `is_unit_passing()` before setting phase to "Finalized"

2. **Use meaningful comments** - Add comments when changing phases or processes

3. **Track batch context** - Use lot numbers or batch IDs to group related units

4. **Finalize children first** - Children must be finalized before assembly attachment

5. **Verify assemblies** - Always call `verify_assembly()` before finalizing box builds

6. **Handle repair workflow** - Set proper phase when sending units to repair

7. **Track changes** - Use `get_unit_changes()` to audit unit lifecycle

8. **Allocate SNs from sequences** - Use configured SN types instead of manual generation

9. **Phase gates** - Implement validation before phase transitions

10. **Don't skip phases** - Follow your defined production flow sequence

---

## Common Workflows

### Test Station Integration

```python
def run_test_at_station(serial_number, part_number, station, operation_type):
    """Execute test and update unit status"""
    
    # Set unit to current process
    api.production.set_unit_process(
        serial_number, part_number,
        process_code=operation_type,
        comment=f"Testing at {station}"
    )
    
    # Run test (creates UUT report)
    # This is typically done by test equipment/software
    # report = create_test_report(serial_number, operation_type)
    # api.report.submit_report(report)
    
    # After test, check result
    if api.production.is_unit_passing(serial_number, part_number):
        # Move to next phase
        api.production.set_unit_phase(
            serial_number, part_number,
            phase="Passed",
            comment=f"Passed at {station}"
        )
        return True
    else:
        # Send to repair
        api.production.set_unit_phase(
            serial_number, part_number,
            phase="Failed",
            comment=f"Failed at {station}"
        )
        return False
```

### Multi-Station Production Line

```python
def production_line(serial_number, part_number):
    """Move unit through multiple stations"""
    
    stations = [
        {"name": "ICT", "process": 10},
        {"name": "FCT", "process": 50},
        {"name": "Burn-In", "process": 60},
        {"name": "Final Inspection", "process": 100}
    ]
    
    for station in stations:
        print(f"\n=== {station['name']} ===")
        
        # Set process
        api.production.set_unit_process(
            serial_number, part_number,
            process_code=station['process'],
            comment=f"At {station['name']}"
        )
        
        # Simulate test execution
        # In real scenario, this calls test software
        time.sleep(1)  # Placeholder for actual test
        
        # Check result
        if api.production.is_unit_passing(serial_number, part_number):
            print(f"✓ PASS at {station['name']}")
        else:
            print(f"✗ FAIL at {station['name']}")
            return False
    
    # All stations passed - finalize
    api.production.set_unit_phase(
        serial_number, part_number,
        phase="Finalized",
        comment="Completed all production stages"
    )
    
    print("\n✓ Unit FINALIZED")
    return True
```

---

## Troubleshooting

### Unit not found
```python
unit = api.production.get_unit("WIDGET-12345", "WIDGET-001")
if not unit:
    print("Unit doesn't exist - create it first")
```

### Cannot finalize unit
```python
# Check if passing
if not api.production.is_unit_passing("WIDGET-12345", "WIDGET-001"):
    verification = api.production.verify_unit("WIDGET-12345", "WIDGET-001")
    print(f"Cannot finalize - {verification.failed_step_count} failures")
```

### Cannot add child to assembly
```python
# Common reasons:
# 1. Child not finalized
api.production.set_unit_phase(child_sn, child_pn, "Finalized")

# 2. Child not in box build template
template = api.product_internal.get_box_build(parent_pn, parent_rev)
template.add_subunit(child_pn, child_rev).save()

# 3. Child already has a parent
# Remove from old parent first
api.production.remove_child_from_assembly(old_parent_sn, old_parent_pn, child_sn, child_pn)
```

---

## See Also

- [Product Domain](PRODUCT.md) - Defining products and box build templates
- [Report Domain](REPORT.md) - Creating test reports for units
- [Process Domain](PROCESS.md) - Defining operation types and workflows
- [Analytics Domain](ANALYTICS.md) - Analyzing unit flow and yield
