"""
Production Domain: Serial Number Management

This example demonstrates serial number allocation and management.
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
# Allocate Serial Numbers
# =============================================================================

# Allocate a block of serial numbers
result = api.production.allocate_serial_numbers(
    part_number="WIDGET-001",
    quantity=100
)

print(f"Allocated {100} serial numbers:")
print(f"  Start: {result.start}")
print(f"  End: {result.end}")


# =============================================================================
# Allocate with Prefix
# =============================================================================

result = api.production.allocate_serial_numbers(
    part_number="WIDGET-001",
    quantity=10,
    prefix="WDG"
)

print(f"\nAllocated with prefix 'WDG':")
for serial in result.serials[:5]:
    print(f"  {serial}")


# =============================================================================
# Find Serial Numbers in Range
# =============================================================================

# Find existing units in a serial number range
units = api.production.find_serial_numbers_in_range(
    start="SN-2024-001000",
    end="SN-2024-001100"
)

print(f"\nUnits in range:")
for unit in units[:10]:
    print(f"  {unit.serialNumber}: {unit.status}")


# =============================================================================
# Check Serial Number Availability
# =============================================================================

def check_availability(serial_number: str) -> bool:
    """Check if a serial number is available."""
    unit = api.production.get_unit(serial_number)
    
    if unit is None:
        print(f"✓ Serial number '{serial_number}' is available")
        return True
    else:
        print(f"✗ Serial number '{serial_number}' is already in use")
        print(f"  Part: {unit.partNumber}, Status: {unit.status}")
        return False


# check_availability("SN-2024-NEW-001")


# =============================================================================
# Reserve Serial Numbers
# =============================================================================

serial_numbers = ["RESERVED-001", "RESERVED-002", "RESERVED-003"]

result = api.production.reserve_serial_numbers(
    part_number="WIDGET-001",
    serial_numbers=serial_numbers
)

print(f"\nReserved {len(serial_numbers)} serial numbers")


# =============================================================================
# Release Serial Number
# =============================================================================

api.production.release_serial_number("RESERVED-001")
print("Released serial number: RESERVED-001")


# =============================================================================
# Serial Number Generation (Local Utility)
# =============================================================================

def generate_serial_number(
    part_number: str, 
    format_string: str = "{prefix}{date}{seq:04d}"
) -> str:
    """
    Generate a serial number locally.
    
    Format placeholders:
    - {prefix}: Part number prefix (first 3 chars)
    - {date}: Current date (YYYYMMDD)
    - {time}: Current time (HHMMSS)
    - {seq}: Sequence number
    """
    now = datetime.now()
    prefix = part_number[:3] if len(part_number) >= 3 else part_number
    
    return format_string.format(
        prefix=prefix,
        date=now.strftime("%Y%m%d"),
        time=now.strftime("%H%M%S"),
        seq=1
    )


serial = generate_serial_number("WIDGET-001")
print(f"\nGenerated serial: {serial}")


# =============================================================================
# Serial Number Validation (Local Utility)
# =============================================================================

import re

def validate_serial_number(serial_number: str, rules: dict = None) -> bool:
    """
    Validate serial number format.
    
    Rules:
    - min_length: Minimum length
    - max_length: Maximum length
    - prefix: Required prefix
    - pattern: Regex pattern
    """
    if rules is None:
        rules = {"min_length": 5, "max_length": 50}
    
    errors = []
    
    if "min_length" in rules and len(serial_number) < rules["min_length"]:
        errors.append(f"Too short (min {rules['min_length']})")
    
    if "max_length" in rules and len(serial_number) > rules["max_length"]:
        errors.append(f"Too long (max {rules['max_length']})")
    
    if "prefix" in rules and not serial_number.startswith(rules["prefix"]):
        errors.append(f"Must start with '{rules['prefix']}'")
    
    if "pattern" in rules and not re.match(rules["pattern"], serial_number):
        errors.append(f"Does not match pattern")
    
    if errors:
        print(f"✗ Invalid: {serial_number}")
        for error in errors:
            print(f"  - {error}")
        return False
    
    print(f"✓ Valid: {serial_number}")
    return True


# Validation examples
validate_serial_number("ABC123456", {"min_length": 10, "prefix": "ABC"})
validate_serial_number("ABC1234567890", {"min_length": 10, "prefix": "ABC"})
