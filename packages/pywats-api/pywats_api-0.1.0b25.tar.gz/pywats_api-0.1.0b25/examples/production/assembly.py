"""
Production Domain: Assembly Management

This example demonstrates assembly and component tracking.
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
# Get Assembly Structure
# =============================================================================

assembly = api.production.get_assembly("MAIN-ASSY-001")

if assembly:
    print(f"Assembly: {assembly.serialNumber}")
    print(f"  Part: {assembly.partNumber}")
    print("\n  Components:")
    for child in assembly.children or []:
        print(f"    - {child.serialNumber} ({child.partNumber})")
        if child.position:
            print(f"      Position: {child.position}")


# =============================================================================
# Print Assembly Tree
# =============================================================================

def print_assembly_tree(serial_number: str, level: int = 0):
    """Recursively print assembly structure as tree."""
    assembly = api.production.get_assembly(serial_number)
    if not assembly:
        return
    
    indent = "  " * level
    prefix = "├─ " if level > 0 else ""
    print(f"{indent}{prefix}{assembly.serialNumber} ({assembly.partNumber})")
    
    for child in assembly.children or []:
        print_assembly_tree(child.serialNumber, level + 1)


print("\nAssembly Tree:")
print_assembly_tree("TOP-LEVEL-001")


# =============================================================================
# Add Child to Assembly
# =============================================================================

# Add a component to an assembly
api.production.add_child_to_assembly(
    parent_serial="MAIN-ASSY-001",
    child_serial="PCBA-001",
    position="SLOT1"
)

print("Added PCBA-001 to MAIN-ASSY-001 at SLOT1")


# =============================================================================
# Remove Child from Assembly
# =============================================================================

api.production.remove_child_from_assembly(
    parent_serial="MAIN-ASSY-001",
    child_serial="PCBA-001"
)

print("Removed PCBA-001 from assembly")


# =============================================================================
# Verify Assembly Completeness
# =============================================================================

verification = api.production.verify_assembly("MAIN-ASSY-001")

print(f"\nAssembly Verification:")
if verification.is_complete:
    print("  ✓ Assembly is complete")
else:
    print("  ✗ Assembly is incomplete")
    print("\n  Missing components:")
    for item in verification.missing_components:
        print(f"    - {item.position}: {item.partNumber}")


# =============================================================================
# Get Component Usage
# =============================================================================

# Find where a component is used
usage = api.production.get_component_usage("PCBA-001")

print(f"\nComponent PCBA-001 usage:")
for assembly in usage:
    print(f"  Used in: {assembly.parent_serial}")
    if assembly.position:
        print(f"    Position: {assembly.position}")


# =============================================================================
# Replace Component
# =============================================================================

def replace_component(parent_serial: str, old_child: str, new_child: str):
    """Replace a component in an assembly."""
    # Get current position
    assembly = api.production.get_assembly(parent_serial)
    position = None
    
    for child in assembly.children or []:
        if child.serialNumber == old_child:
            position = child.position
            break
    
    # Remove old, add new
    api.production.remove_child_from_assembly(parent_serial, old_child)
    api.production.add_child_to_assembly(parent_serial, new_child, position)
    
    print(f"Replaced {old_child} with {new_child}")


# replace_component("MAIN-ASSY-001", "PCBA-OLD", "PCBA-NEW")


# =============================================================================
# Assembly Workflow Example
# =============================================================================

def assembly_workflow():
    """Demonstrate assembly workflow."""
    print("=" * 50)
    print("Assembly Workflow")
    print("=" * 50)
    
    main_serial = f"MAIN-{datetime.now().strftime('%Y%m%d%H%M')}"
    pcba_serial = f"PCBA-{datetime.now().strftime('%Y%m%d%H%M')}"
    psu_serial = f"PSU-{datetime.now().strftime('%Y%m%d%H%M')}"
    
    print(f"\n1. Creating components...")
    print(f"   Main: {main_serial}")
    print(f"   PCBA: {pcba_serial}")
    print(f"   PSU: {psu_serial}")
    
    print(f"\n2. Building assembly...")
    print(f"   Adding PCBA to SLOT1")
    print(f"   Adding PSU to SLOT2")
    
    print(f"\n3. Final structure:")
    print(f"   {main_serial}")
    print(f"   ├─ {pcba_serial} [SLOT1]")
    print(f"   └─ {psu_serial} [SLOT2]")
    
    print("=" * 50)


# assembly_workflow()


# =============================================================================
# BOM Validation Example
# =============================================================================

# Example BOM definition
EXAMPLE_BOM = {
    "PRODUCT-001": [
        {"position": "PCBA", "partNumber": "PCBA-100", "quantity": 1},
        {"position": "PSU", "partNumber": "PSU-200", "quantity": 1},
        {"position": "CABLE", "partNumber": "CABLE-50", "quantity": 2},
    ]
}


def validate_against_bom(serial_number: str, bom: dict):
    """Validate assembly against BOM."""
    unit = api.production.get_unit(serial_number)
    if not unit or unit.partNumber not in bom:
        return False
    
    assembly = api.production.get_assembly(serial_number)
    bom_items = bom[unit.partNumber]
    
    print(f"BOM Validation: {serial_number}")
    
    for item in bom_items:
        found = [c for c in (assembly.children or []) 
                 if c.position == item["position"]]
        
        if len(found) >= item["quantity"]:
            print(f"  ✓ {item['position']}: OK")
        else:
            print(f"  ✗ {item['position']}: Missing")
    
    return True


# validate_against_bom("PRODUCT-001-SN", EXAMPLE_BOM)
