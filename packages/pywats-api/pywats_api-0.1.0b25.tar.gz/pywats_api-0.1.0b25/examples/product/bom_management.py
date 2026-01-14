"""
Product Domain: BOM Management

This example demonstrates Bill of Materials (BOM) operations.
"""
import os
from pywats import pyWATS

# =============================================================================
# Setup
# =============================================================================

api = pyWATS(
    base_url=os.environ.get("WATS_BASE_URL", "https://demo.wats.com"),
    token=os.environ.get("WATS_TOKEN", "")
)


# =============================================================================
# Get BOM for a Product
# =============================================================================

# Get the Bill of Materials
bom = api.product.get_bom("ASSEMBLY-001")

if bom:
    print(f"BOM for ASSEMBLY-001:")
    for item in bom.items:
        print(f"  {item.partNumber} x{item.quantity}")
        if item.referenceDesignator:
            print(f"    Ref: {item.referenceDesignator}")


# =============================================================================
# BOM Tree Structure
# =============================================================================

def print_bom_tree(part_number: str, level: int = 0):
    """Recursively print BOM as a tree."""
    indent = "  " * level
    product = api.product.get_product(part_number)
    name = product.productName if product else part_number
    
    print(f"{indent}├─ {part_number}: {name}")
    
    bom = api.product.get_bom(part_number)
    if bom and bom.items:
        for item in bom.items:
            print_bom_tree(item.partNumber, level + 1)


# Print full BOM tree
print("BOM Tree:")
print_bom_tree("TOP-ASSEMBLY-001")


# =============================================================================
# Add BOM Item
# =============================================================================

from pywats.domains.product import BomItem

# Add a component to the BOM
new_item = BomItem(
    partNumber="RESISTOR-10K",
    quantity=4,
    referenceDesignator="R1,R2,R3,R4"
)

api.product.add_bom_item("PCBA-001", new_item)
print("Added BOM item")


# =============================================================================
# Update BOM Item
# =============================================================================

# Update quantity for a BOM item
api.product.update_bom_item("PCBA-001", "RESISTOR-10K", quantity=8)
print("Updated BOM item quantity")


# =============================================================================
# Remove BOM Item
# =============================================================================

# Remove a component from the BOM
api.product.remove_bom_item("PCBA-001", "RESISTOR-10K")
print("Removed BOM item")


# =============================================================================
# BOM Cost Calculation Example
# =============================================================================

def calculate_bom_cost(part_number: str) -> float:
    """Calculate total BOM cost (example with mock prices)."""
    # In real use, you'd get prices from your system
    mock_prices = {
        "RESISTOR-10K": 0.01,
        "CAPACITOR-100NF": 0.02,
        "IC-MCU-001": 5.00,
    }
    
    total = 0.0
    bom = api.product.get_bom(part_number)
    
    if bom and bom.items:
        for item in bom.items:
            price = mock_prices.get(item.partNumber, 0)
            total += price * item.quantity
    
    return total


cost = calculate_bom_cost("PCBA-001")
print(f"Estimated BOM cost: ${cost:.2f}")
