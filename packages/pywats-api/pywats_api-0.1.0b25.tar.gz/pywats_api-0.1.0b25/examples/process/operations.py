"""
Process Domain: Process and Operation Management

This example demonstrates process and test operation queries.
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
# Get All Processes
# =============================================================================

# Get defined test processes/operations
processes = api.analytics.get_processes()

print("Test Processes:")
for process in processes:
    test_flag = "✓" if process.is_test_operation else " "
    print(f"  [{test_flag}] {process.code}: {process.name}")


# =============================================================================
# Get Test Operations Only
# =============================================================================

test_operations = [p for p in api.analytics.get_processes() if p.is_test_operation]

print(f"\nTest Operations ({len(test_operations)}):")
for op in test_operations:
    print(f"  {op.code}: {op.name}")


# =============================================================================
# Get Non-Test Operations (Repair, Rework, etc.)
# =============================================================================

non_test = [p for p in api.analytics.get_processes() if not p.is_test_operation]

print(f"\nNon-Test Operations ({len(non_test)}):")
for op in non_test:
    print(f"  {op.code}: {op.name}")


# =============================================================================
# Get Production Levels
# =============================================================================

levels = api.analytics.get_levels()

print("\nProduction Levels:")
for level in levels:
    print(f"  {level.level_id}: {level.level_name}")


# =============================================================================
# Process Code Reference
# =============================================================================

# Common WATS process codes (may vary by configuration)
STANDARD_PROCESS_CODES = {
    100: "End of Line Test (EOL)",
    200: "In-Circuit Test (ICT)",
    300: "Functional Test (FCT)",
    400: "Burn-in Test",
    500: "Repair",
    600: "Rework",
    700: "Final Inspection",
}

print("\nStandard Process Codes Reference:")
for code, name in STANDARD_PROCESS_CODES.items():
    print(f"  {code}: {name}")


# =============================================================================
# Get Process by Code
# =============================================================================

def get_process_by_code(code: int):
    """Get process info by code."""
    processes = api.analytics.get_processes()
    
    for process in processes:
        if process.code == code:
            return process
    
    return None


process = get_process_by_code(100)
if process:
    print(f"\nProcess 100: {process.name}")
    print(f"  Is test: {process.is_test_operation}")


# =============================================================================
# Using Process Codes in Reports
# =============================================================================

from pywats.models import UUTReport, UURReport
from datetime import datetime

# UUT Report with specific process
uut_report = UUTReport(
    pn="WIDGET-001",
    sn="SN-001",
    rev="A",
    result="Passed",
    start=datetime.now(),
    processCode=100  # EOL Test
)

# UUR Report for repair
uur_report = UURReport(
    pn="WIDGET-001",
    sn="SN-001",
    rev="A",
    result="Passed",
    start=datetime.now(),
    processCode=500  # Repair
)

print("\nReports created with process codes")
