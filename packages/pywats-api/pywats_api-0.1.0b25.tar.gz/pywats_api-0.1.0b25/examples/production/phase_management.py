"""
Production Domain: Phase Management

This example demonstrates production phase management.
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
# Get Available Phases
# =============================================================================

# Get all production phases
phases = api.production.get_phases()

print("Production Phases:")
for phase in phases:
    print(f"  {phase.order}. {phase.name}")
    if phase.description:
        print(f"     {phase.description}")


# =============================================================================
# Get Phases for Specific Product
# =============================================================================

phases = api.production.get_phases(part_number="WIDGET-001")

print(f"\nPhases for WIDGET-001:")
for phase in phases:
    print(f"  {phase.name}")


# =============================================================================
# Get Unit's Current Phase
# =============================================================================

unit = api.production.get_unit("SN-2024-001234")

if unit:
    print(f"\nUnit {unit.serialNumber}:")
    print(f"  Current Phase: {unit.currentPhase}")
    print(f"  Status: {unit.status}")


# =============================================================================
# Set Unit Phase
# =============================================================================

# Move unit to a specific phase
api.production.set_unit_phase("SN-2024-001234", "FCT")
print("Set unit to phase: FCT")


# =============================================================================
# Get Units in Phase
# =============================================================================

from pywats.domains.report import WATSFilter

filter_data = WATSFilter(
    partNumber="WIDGET-001",
    phase="ICT"
)

units = api.production.search_units(filter_data)

print(f"\nUnits in ICT phase: {len(units)}")
for unit in units[:5]:
    print(f"  {unit.serialNumber}")


# =============================================================================
# Advance Unit to Next Phase
# =============================================================================

def advance_phase(serial_number: str):
    """Advance unit to the next phase."""
    unit = api.production.get_unit(serial_number)
    if not unit:
        print(f"Unit '{serial_number}' not found")
        return
    
    phases = api.production.get_phases(part_number=unit.partNumber)
    phase_names = [p.name for p in phases]
    
    try:
        current_idx = phase_names.index(unit.currentPhase)
        if current_idx < len(phases) - 1:
            next_phase = phases[current_idx + 1].name
            api.production.set_unit_phase(serial_number, next_phase)
            print(f"Advanced {serial_number}: {unit.currentPhase} -> {next_phase}")
        else:
            print(f"Unit is already in final phase: {unit.currentPhase}")
    except ValueError:
        print(f"Phase '{unit.currentPhase}' not found")


# advance_phase("SN-2024-001234")


# =============================================================================
# Phase Gate Check
# =============================================================================

def phase_gate_check(serial_number: str, target_phase: str) -> bool:
    """Check if unit can move to target phase."""
    unit = api.production.get_unit(serial_number)
    
    if not unit:
        print(f"✗ Unit not found")
        return False
    
    phases = api.production.get_phases(part_number=unit.partNumber)
    phase_names = [p.name for p in phases]
    
    if target_phase not in phase_names:
        print(f"✗ Invalid phase: '{target_phase}'")
        return False
    
    current_idx = phase_names.index(unit.currentPhase) if unit.currentPhase in phase_names else -1
    target_idx = phase_names.index(target_phase)
    
    if target_idx <= current_idx:
        print(f"✗ Cannot move backwards")
        return False
    
    if unit.status == "Failed":
        print(f"✗ Unit has failed status")
        return False
    
    print(f"✓ Unit can move to '{target_phase}'")
    return True


# phase_gate_check("SN-2024-001234", "PACK")


# =============================================================================
# Standard Phases Reference
# =============================================================================

STANDARD_PHASES = [
    ("SMT", "Surface Mount Technology assembly"),
    ("ICT", "In-Circuit Test"),
    ("AOI", "Automated Optical Inspection"),
    ("FCT", "Functional Test"),
    ("BURN_IN", "Burn-in testing"),
    ("FINAL_QC", "Final Quality Check"),
    ("PACK", "Packaging"),
    ("SHIP", "Ready for shipment"),
]

print("\nStandard Production Phases Reference:")
for phase, description in STANDARD_PHASES:
    print(f"  {phase:12} - {description}")
