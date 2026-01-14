# Box Build Guide

## Overview

Box build functionality in pyWATS manages multi-level product assemblies where a parent product contains one or more child products (subunits). This guide explains how to:

1. Define what subunits a product requires (Box Build Template)
2. Actually build assemblies during production (Unit Assembly)

## Key Concept: Templates vs. Units

Understanding the distinction between these two concepts is crucial:

### Box Build Template (Product Domain)

**What it is:** A DESIGN-TIME definition of what subunits are required to build a product.

**Where it lives:** Product domain (`api.product_internal`)

**Example use case:** "A Controller Module (CTRL-100) requires 1x Power Supply and 2x Sensor Board"

```python
# This defines the REQUIREMENTS (what's needed)
template = api.product_internal.get_box_build("CTRL-100", "A")
template.add_subunit("PSU-200", "A", quantity=1)
template.add_subunit("SENSOR-300", "A", quantity=2)
template.save()
```

### Unit Assembly (Production Domain)

**What it is:** RUNTIME attachment of actual production units (with serial numbers) to a parent unit.

**Where it lives:** Production domain (`api.production`)

**Example use case:** "Unit CTRL-SN-001 now contains PSU-SN-456, SENSOR-SN-789, and SENSOR-SN-790"

```python
# This BUILDS the assembly (attaches actual units)
api.production.add_child_to_assembly(
    parent_serial="CTRL-SN-001", parent_part="CTRL-100",
    child_serial="PSU-SN-456", child_part="PSU-200"
)
```

## Complete Workflow

### Step 1: Create Products

First, create the parent and child products with revisions:

```python
from pywats import pyWATS
from pywats.domains.product.enums import ProductState

api = pyWATS(base_url="https://wats.example.com", token="your-token")

# Create child product (Power Supply)
api.product.create_product(
    part_number="PSU-200",
    name="Power Supply Unit",
    description="24V DC Power Supply",
    state=ProductState.ACTIVE
)
api.product.create_revision(
    part_number="PSU-200",
    revision="A",
    state=ProductState.ACTIVE
)

# Create parent product (Controller Module)
api.product.create_product(
    part_number="CTRL-100",
    name="Controller Module",
    description="Main Controller with Power Supply",
    state=ProductState.ACTIVE
)
api.product.create_revision(
    part_number="CTRL-100",
    revision="A",
    state=ProductState.ACTIVE
)
```

### Step 2: Define Box Build Template

Define what subunits the parent product requires:

```python
# Get or create box build template
template = api.product_internal.get_box_build("CTRL-100", "A")

# Add required subunits
template.add_subunit(
    part_number="PSU-200",
    revision="A",
    quantity=1
)

# Save to server
template.save()

# Or use context manager (auto-saves)
with api.product_internal.get_box_build("CTRL-100", "A") as bb:
    bb.add_subunit("PSU-200", "A", quantity=1)
    bb.add_subunit("SENSOR-300", "A", quantity=2)
# Automatically saved when exiting context
```

### Step 3: Create Production Units

Create actual units with serial numbers:

```python
from pywats.domains.production import Unit

# Create parent unit
parent_unit = Unit(
    serial_number="CTRL-SN-001",
    part_number="CTRL-100",
    revision="A"
)

# Create child unit
child_unit = Unit(
    serial_number="PSU-SN-456",
    part_number="PSU-200",
    revision="A"
)

# Save to WATS
api.production.create_units([parent_unit, child_unit])
```

### Step 4: Test and Finalize Child Units

**Important:** Child units MUST be finalized before they can be added to an assembly.

```python
# Run tests on child unit (creates test reports)
# ... your test code here ...

# Set child unit to "Finalized" phase
api.production.set_unit_phase(
    serial_number="PSU-SN-456",
    part_number="PSU-200",
    phase="Finalized"  # or phase=16 (the phase ID)
)
```

### Step 5: Build the Assembly

Attach child units to the parent:

```python
# Add child to parent assembly
result = api.production.add_child_to_assembly(
    parent_serial="CTRL-SN-001",
    parent_part="CTRL-100",
    child_serial="PSU-SN-456",
    child_part="PSU-200"
)

if result:
    print("Child successfully added to assembly!")
```

### Step 6: Verify Assembly

Check if all required subunits are attached:

```python
# Verify assembly matches box build template
verification = api.production.verify_assembly(
    serial_number="CTRL-SN-001",
    part_number="CTRL-100",
    revision="A"
)

print(f"Verification result: {verification}")
```

## API Reference

### Product Domain (Templates)

#### `api.product_internal.get_box_build(part_number, revision)`

Get or create a box build template.

```python
template = api.product_internal.get_box_build("CTRL-100", "A")
```

#### `BoxBuildTemplate.add_subunit(part_number, revision, quantity=1)`

Add a subunit requirement to the template.

```python
template.add_subunit("PSU-200", "A", quantity=1)
template.add_subunit("SENSOR-300", "A", quantity=2, revision_mask="A,B")
```

**Parameters:**
- `part_number`: Child product part number
- `revision`: Default revision for the child
- `quantity`: How many are required (default: 1)
- `revision_mask`: Acceptable revisions pattern (optional)

#### `BoxBuildTemplate.remove_subunit(part_number, revision)`

Remove a subunit from the template.

```python
template.remove_subunit("OLD-PART", "A")
```

#### `BoxBuildTemplate.save()`

Persist all changes to the server.

```python
template.save()
```

#### `BoxBuildTemplate.subunits`

Get current subunits (including pending changes).

```python
for subunit in template.subunits:
    print(f"{subunit.child_part_number} rev {subunit.child_revision}: qty {subunit.quantity}")
```

### Production Domain (Unit Assembly)

#### `api.production.add_child_to_assembly(parent_serial, parent_part, child_serial, child_part)`

Attach a child unit to a parent assembly.

**Requirements:**
- Parent's box build template must define this child product
- Child unit must be in "Finalized" phase
- Child must not already have a parent

```python
api.production.add_child_to_assembly(
    parent_serial="CTRL-SN-001",
    parent_part="CTRL-100",
    child_serial="PSU-SN-456",
    child_part="PSU-200"
)
```

#### `api.production.remove_child_from_assembly(parent_serial, parent_part, child_serial, child_part)`

Detach a child unit from a parent.

```python
api.production.remove_child_from_assembly(
    parent_serial="CTRL-SN-001",
    parent_part="CTRL-100",
    child_serial="PSU-SN-456",
    child_part="PSU-200"
)
```

#### `api.production.verify_assembly(serial_number, part_number, revision)`

Check if assembly matches box build template.

```python
result = api.production.verify_assembly("CTRL-SN-001", "CTRL-100", "A")
```

#### `api.production.set_unit_phase(serial_number, part_number, phase)`

Set a unit's phase. Use "Finalized" (or phase ID 16) before adding to assembly.

```python
# By name
api.production.set_unit_phase("PSU-SN-456", "PSU-200", "Finalized")

# By ID
api.production.set_unit_phase("PSU-SN-456", "PSU-200", 16)
```

## Revision Masks

Revision masks control which child revisions are acceptable in a box build:

```python
# Accept only revision A
template.add_subunit("PART", "A", revision_mask="A")

# Accept any revision starting with "1."
template.add_subunit("PART", "1.0", revision_mask="1.%")

# Accept multiple specific revisions
template.add_subunit("PART", "A", revision_mask="A,B,C")

# Accept revision range
template.add_subunit("PART", "1.0", revision_mask="1.0,1.1,1.2")
```

## Error Handling

### Common Errors

**Child not finalized:**
```
Error: Child unit must be in phase Finalized
Solution: Call api.production.set_unit_phase(child_sn, child_pn, "Finalized")
```

**Child not in template:**
```
Error: Parent's box build must define the child unit as valid
Solution: Add the child product to the box build template first
```

**Child already has parent:**
```
Error: The child unit must not already have a parent
Solution: Remove child from existing parent first
```

## BOM vs Box Build

**Bill of Materials (BOM):** Lists electronic components (resistors, capacitors, ICs) - typically for PCB assembly. Uses WSBF XML format.

**Box Build Template:** Lists subassemblies/subunits (PCBAs, power supplies, modules) - for mechanical/final assembly. Uses ProductRevisionRelation.

```python
# BOM: Electronic components for PCB
bom_items = [
    BomItem(component_ref="R1", part_number="RES-10K", quantity=1),
    BomItem(component_ref="C1", part_number="CAP-100NF", quantity=1),
]
api.product.update_bom("PCBA-100", "A", bom_items)

# Box Build: Subassemblies for final product
template = api.product_internal.get_box_build("MODULE-100", "A")
template.add_subunit("PCBA-100", "A", quantity=1)  # The assembled PCB
template.add_subunit("PSU-200", "A", quantity=1)   # Power supply
template.save()
```

## Best Practices

1. **Define templates before production:** Set up box build templates before creating production units.

2. **Finalize children first:** Always finalize child units before adding to assembly.

3. **Use revision masks wisely:** Allow flexibility where appropriate (e.g., `"1.%"` for minor revisions).

4. **Verify after assembly:** Always call `verify_assembly()` to confirm completeness.

5. **Handle errors gracefully:** Wrap assembly operations in try/except blocks.

```python
try:
    api.production.add_child_to_assembly(
        parent_serial, parent_part, child_serial, child_part
    )
except Exception as e:
    print(f"Assembly failed: {e}")
    # Handle error (retry, log, alert, etc.)
```
