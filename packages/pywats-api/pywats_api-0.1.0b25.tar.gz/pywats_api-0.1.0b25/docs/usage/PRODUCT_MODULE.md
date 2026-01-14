# Product Module Usage Guide

## Overview

The Product module manages products (parts), revisions, BOMs (Bill of Materials), and box build templates in WATS.

## Quick Start

```python
from pywats import pyWATS

api = pyWATS(base_url="https://wats.example.com", token="credentials")

# Get all products
products = api.product.get_products()

# Get specific product
product = api.product.get_product("PART-001")

# Get revisions
revisions = api.product.get_revisions("PART-001")
```

## Basic Operations

### 1. Get Products

```python
# Get all products (summary view)
products = api.product.get_products()

for product in products:
    print(f"{product.part_number}: {product.description}")
    print(f"  State: {product.state}")

# Get product with full details
product = api.product.get_product_full("PART-001")
print(f"Created: {product.created_date}")
print(f"Revisions: {len(product.revisions)}")
```

### 2. Get Specific Product

```python
from pywats import ProductState

# Get by part number
product = api.product.get_product("MODULE-100")

if product:
    print(f"Part Number: {product.part_number}")
    print(f"Description: {product.description}")
    print(f"State: {product.state}")
    print(f"Active: {product.state == ProductState.ACTIVE}")
```

### 3. Create Product

```python
from pywats import ProductState

# Create new product
product = api.product.create_product(
    part_number="NEW-PART-001",
    description="New Product Description",
    state=ProductState.ACTIVE,
    product_group="Electronics"  # Optional
)

print(f"Created product: {product.part_number}")
```

### 4. Update Product

```python
# Get product, modify, update
product = api.product.get_product("PART-001")
product.description = "Updated Description"
product.state = ProductState.ACTIVE

updated = api.product.update_product(product)
```

## Product Revisions

### 1. Get Revisions

```python
# Get all revisions for a product
revisions = api.product.get_revisions("PART-001")

for rev in revisions:
    print(f"Revision {rev.revision}: {rev.state}")

# Get specific revision
revision = api.product.get_revision("PART-001", "B")
```

### 2. Create Revision

```python
from pywats import ProductState

# Create new revision
revision = api.product.create_revision(
    part_number="PART-001",
    revision="C",
    state=ProductState.ACTIVE,
    description="Revision C changes"
)
```

### 3. Revision States

```python
from pywats.domains.product.enums import ProductState

# Available states
ProductState.ACTIVE        # Active/in production
ProductState.OBSOLETE      # No longer used
ProductState.DEVELOPMENT   # In development
ProductState.PROTOTYPE     # Prototype phase
```

## Product Tags

Products and revisions can have tags (key-value metadata):

### 1. Product Tags

```python
# Get product tags
tags = api.product.get_product_tags("PART-001")
for tag in tags:
    print(f"{tag.key}: {tag.value}")

# Set product tags (replaces all)
api.product.set_product_tags("PART-001", [
    {"key": "Category", "value": "Power Supply"},
    {"key": "Voltage", "value": "12V"}
])

# Add single tag
api.product.add_product_tag("PART-001", "Manufacturer", "ACME Corp")
```

### 2. Revision Tags

```python
# Get revision tags
tags = api.product.get_revision_tags("PART-001", "A")

# Set revision tags
api.product.set_revision_tags("PART-001", "A", [
    {"key": "PCB_Version", "value": "1.2"},
    {"key": "Test_Program", "value": "v3.1"}
])
```

## Bill of Materials (BOM)

### 1. Get BOM

```python
# Get BOM for a revision
bom = api.product.get_bom("ASSEMBLY-001", "A")

for item in bom.items:
    print(f"{item.part_number} - Qty: {item.quantity}")
    print(f"  Designators: {item.designators}")
    print(f"  Revision Mask: {item.revision_mask}")
```

### 2. Upload BOM

```python
# Upload BOM from list
bom_items = [
    {
        "part_number": "RESISTOR-100",
        "quantity": 10,
        "designators": "R1,R2,R3,R4,R5,R6,R7,R8,R9,R10",
        "revision_mask": "*"  # Any revision
    },
    {
        "part_number": "CAPACITOR-10UF",
        "quantity": 5,
        "designators": "C1,C2,C3,C4,C5",
        "revision_mask": "A|B"  # Revision A or B only
    }
]

api.product.upload_bom(
    part_number="ASSEMBLY-001",
    revision="A",
    bom_items=bom_items
)
```

### 3. Revision Masks

Revision masks control which component revisions are acceptable:

```python
# Common patterns:
"*"        # Any revision
"A"        # Only revision A
"A|B"      # Revision A or B
"A|B|C"    # Revision A, B, or C
"[A-Z]"    # Any letter A through Z
```

### 4. Upload BOM from Dict

```python
# Alternative: Upload from dictionary
bom_dict = {
    "RESISTOR-100": {"quantity": 10, "designators": "R1-R10", "revision_mask": "*"},
    "CAPACITOR-10UF": {"quantity": 5, "designators": "C1-C5", "revision_mask": "*"}
}

api.product.upload_bom_from_dict("ASSEMBLY-001", "A", bom_dict)
```

## Box Build Templates (Internal API)

Box build templates define assemblies with sub-units (e.g., PCBAs in modules).

**⚠️ Note**: This uses internal WATS APIs that may change.

### 1. Get Box Build Template

```python
# Get template showing required subunits
template = api.product_internal.get_box_build_template("MODULE-100", "A")

print(f"Main part: {template.part_number}")
print("Required subunits:")
for subunit in template.subunits:
    print(f"  - {subunit.part_number} (Index: {subunit.index})")
    print(f"    Revision mask: {subunit.revision_mask}")
```

### 2. Get Required Parts

```python
# Get list of parts needed for assembly
parts = api.product_internal.get_required_parts("MODULE-100", "A")

for part in parts:
    print(f"{part.part_number} - {part.description}")
```

### 3. Add Subunit to Box Build

```python
# Define subunit in assembly
api.product_internal.add_subunit_to_box_build(
    parent_part="MODULE-100",
    parent_revision="A",
    child_part="PCBA-200",
    child_revision_mask="*",  # Accept any revision
    index=0  # Position in assembly
)
```

### 4. Remove Subunit

```python
# Remove subunit from template
api.product_internal.remove_subunit_from_box_build(
    parent_part="MODULE-100",
    parent_revision="A",
    index=0  # Position to remove
)
```

### 5. Box Build Context Manager

```python
# Convenient way to define box build
with api.product_internal.box_build_context("MODULE-100", "A") as builder:
    builder.add_subunit("PCBA-200", "*", index=0)
    builder.add_subunit("PCBA-201", "*", index=1)
    # Auto-saved when context exits
```

## Product Groups

### 1. Get Product Groups

```python
# Get all product groups
groups = api.product.get_product_groups()

for group in groups:
    print(group)
```

### 2. Filter by Group

```python
# Get all products in a group
products = api.product.get_products()
electronics = [p for p in products if p.product_group == "Electronics"]
```

## Common Patterns

### Pattern 1: Product Setup Workflow

```python
from pywats import ProductState

# 1. Create product
product = api.product.create_product(
    part_number="NEW-MODULE",
    description="New Power Module",
    state=ProductState.DEVELOPMENT
)

# 2. Create initial revision
revision = api.product.create_revision(
    part_number="NEW-MODULE",
    revision="A",
    state=ProductState.DEVELOPMENT
)

# 3. Add tags
api.product.set_product_tags("NEW-MODULE", [
    {"key": "Type", "value": "Power Supply"},
    {"key": "Voltage", "value": "12V"}
])

# 4. Upload BOM
bom = [...]  # Your BOM items
api.product.upload_bom("NEW-MODULE", "A", bom)

# 5. Activate when ready
revision.state = ProductState.ACTIVE
api.product.update_revision(revision)
```

### Pattern 2: Revision Upgrade

```python
# Copy settings from old to new revision
old_rev = api.product.get_revision("PART-001", "A")
old_bom = api.product.get_bom("PART-001", "A")
old_tags = api.product.get_revision_tags("PART-001", "A")

# Create new revision
new_rev = api.product.create_revision(
    part_number="PART-001",
    revision="B",
    state=ProductState.DEVELOPMENT,
    description=f"Based on Rev {old_rev.revision}"
)

# Copy BOM (modify as needed)
api.product.upload_bom("PART-001", "B", old_bom.items)

# Copy tags
api.product.set_revision_tags("PART-001", "B", old_tags)

# When tested, activate new and obsolete old
new_rev.state = ProductState.ACTIVE
old_rev.state = ProductState.OBSOLETE
api.product.update_revision(new_rev)
api.product.update_revision(old_rev)
```

### Pattern 3: Assembly Definition

```python
# Define a module with subassemblies
MAIN_MODULE = "MODULE-500W"
MAIN_REV = "A"

# Create main product
api.product.create_product(MAIN_MODULE, "500W Power Module", ProductState.ACTIVE)
api.product.create_revision(MAIN_MODULE, MAIN_REV, ProductState.ACTIVE)

# Define subunits
with api.product_internal.box_build_context(MAIN_MODULE, MAIN_REV) as builder:
    builder.add_subunit("PCBA-CONTROL", "*", index=0)
    builder.add_subunit("PCBA-POWER", "*", index=1)
    builder.add_subunit("FAN-ASSEMBLY", "*", index=2)

# Upload BOM for mechanical parts
mechanical_bom = [
    {"part_number": "SCREW-M3", "quantity": 8, "designators": "S1-S8", "revision_mask": "*"},
    {"part_number": "HEATSINK", "quantity": 1, "designators": "HS1", "revision_mask": "*"}
]
api.product.upload_bom(MAIN_MODULE, MAIN_REV, mechanical_bom)
```

### Pattern 4: BOM Validation

```python
def validate_bom(part_number: str, revision: str):
    """Validate BOM has all required parts"""
    bom = api.product.get_bom(part_number, revision)
    
    issues = []
    for item in bom.items:
        # Check if referenced part exists
        part = api.product.get_product(item.part_number)
        if not part:
            issues.append(f"Part not found: {item.part_number}")
            continue
        
        # Check if part has active revision matching mask
        revisions = api.product.get_revisions(item.part_number)
        active_revs = [r for r in revisions if r.state == ProductState.ACTIVE]
        
        if not active_revs:
            issues.append(f"No active revision for: {item.part_number}")
    
    return issues
```

## Best Practices

### 1. Use Meaningful Part Numbers

```python
# ✓ Good - descriptive
"MODULE-500W-12V"
"PCBA-CONTROLLER-V2"
"RESISTOR-10K-0603"

# ✗ Avoid - unclear
"PART001"
"ASM-1"
```

### 2. Manage States Properly

```python
# ✓ Good - proper lifecycle
product.state = ProductState.DEVELOPMENT  # During design
product.state = ProductState.ACTIVE       # In production
product.state = ProductState.OBSOLETE     # End of life

# ✗ Avoid - skipping states
product.state = ProductState.ACTIVE  # Directly from creation (risky)
```

### 3. Use Revision Masks

```python
# ✓ Good - flexible BOM
{"part_number": "RESISTOR", "revision_mask": "*"}  # Any revision OK

# ✓ Good - controlled BOM
{"part_number": "FIRMWARE", "revision_mask": "3.0|3.1"}  # Specific versions

# ✗ Avoid - too restrictive
{"part_number": "RESISTOR", "revision_mask": "A"}  # Must update for every revision
```

### 4. Tag Consistently

```python
# ✓ Good - consistent naming
api.product.add_product_tag("PART-001", "Category", "Electronics")
api.product.add_product_tag("PART-002", "Category", "Mechanical")

# ✗ Avoid - inconsistent
api.product.add_product_tag("PART-001", "category", "electronics")  # Lowercase
api.product.add_product_tag("PART-002", "Type", "Mechanical")       # Different key
```

### 5. Validate Before Production

```python
# ✓ Good - validate before activating
product = api.product.get_product("NEW-PART")
bom = api.product.get_bom("NEW-PART", "A")

if len(bom.items) > 0:  # Has BOM
    revision = api.product.get_revision("NEW-PART", "A")
    revision.state = ProductState.ACTIVE
    api.product.update_revision(revision)
else:
    print("ERROR: Cannot activate - BOM is empty")
```

## Troubleshooting

### Product Not Found

```python
# Check if product exists before operations
product = api.product.get_product("PART-001")
if not product:
    print("Product doesn't exist - create it first")
    product = api.product.create_product("PART-001", ...)
```

### BOM Upload Failing

```python
# Ensure all referenced parts exist
for item in bom_items:
    part = api.product.get_product(item["part_number"])
    if not part:
        print(f"Create {item['part_number']} first")
```

### Revision Conflicts

```python
# Check existing revisions before creating new
revisions = api.product.get_revisions("PART-001")
existing = [r.revision for r in revisions]
if "B" in existing:
    print("Revision B already exists")
```

## Related Documentation

- [Production Module](PRODUCTION_MODULE.md) - For manufacturing units from products
- [Report Module](REPORT_MODULE.md) - For testing products
- [Architecture](../ARCHITECTURE.md) - Overall system design
