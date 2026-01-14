"""
Report Domain: Create UUR Report

This example demonstrates creating UUR (Unit Under Repair) reports.
"""
import os
from datetime import datetime
from pywats import pyWATS
from pywats.core import Station
from pywats.models import UURReport

# =============================================================================
# Setup
# =============================================================================

station = Station(name="REPAIR-STATION-01", location="Repair Center")

api = pyWATS(
    base_url=os.environ.get("WATS_BASE_URL", "https://demo.wats.com"),
    token=os.environ.get("WATS_TOKEN", ""),
    station=station
)


# =============================================================================
# Create Simple Repair Report
# =============================================================================

# Create a basic repair report
report = UURReport(
    pn="WIDGET-001",           # Part number
    sn="SN-2024-001234",       # Serial number
    rev="A",                    # Revision
    result="Passed",           # Repair result
    start=datetime.now(),      # Repair start time
    processCode=500,           # Repair process code
)

# Add repair information
report.add_repair(
    symptom="Unit failed voltage test",
    cause="Damaged capacitor C12",
    action="Replaced capacitor C12"
)

# Submit to WATS
response = api.report.submit_report(report)
print(f"Repair report submitted: {response.id}")


# =============================================================================
# Repair with Multiple Actions
# =============================================================================

report = UURReport(
    pn="WIDGET-001",
    sn="SN-2024-001235",
    rev="A",
    result="Passed",
    start=datetime.now(),
    processCode=500,
)

# Add multiple repairs
report.add_repair(
    symptom="No power",
    cause="Blown fuse F1",
    action="Replaced fuse F1"
)

report.add_repair(
    symptom="Overheating",
    cause="Thermal paste degraded",
    action="Reapplied thermal paste"
)

response = api.report.submit_report(report)
print(f"Multi-repair report submitted: {response.id}")


# =============================================================================
# No Fault Found (NFF)
# =============================================================================

report = UURReport(
    pn="WIDGET-001",
    sn="SN-2024-001236",
    rev="A",
    result="Passed",
    start=datetime.now(),
    processCode=500,
)

report.add_repair(
    symptom="Intermittent failure reported by customer",
    cause="No fault found",
    action="Unit tested - all tests passed"
)

response = api.report.submit_report(report)
print(f"NFF report submitted: {response.id}")


# =============================================================================
# Repair with Replaced Components
# =============================================================================

report = UURReport(
    pn="WIDGET-001",
    sn="SN-2024-001237",
    rev="A",
    result="Passed",
    start=datetime.now(),
    processCode=500,
)

# Add repair with component details
report.add_repair(
    symptom="Unit failed power supply test",
    cause="Failed voltage regulator U3",
    action="Replaced U3 with new component"
)

# Add component information via misc info
report.add_misc_info("Replaced_Component", "U3 - LM7805")
report.add_misc_info("Component_Lot", "LOT-2024-Q4")

response = api.report.submit_report(report)
print(f"Component replacement report submitted: {response.id}")


# =============================================================================
# Warranty Repair
# =============================================================================

report = UURReport(
    pn="WIDGET-001",
    sn="SN-2024-001238",
    rev="A",
    result="Passed",
    start=datetime.now(),
    processCode=500,
)

report.add_repair(
    symptom="Customer reported display malfunction",
    cause="Defective LCD panel",
    action="Replaced LCD panel under warranty"
)

# Track warranty info
report.add_misc_info("Repair_Type", "Warranty")
report.add_misc_info("RMA_Number", "RMA-2024-001234")
report.add_misc_info("Customer", "Acme Corp")

response = api.report.submit_report(report)
print(f"Warranty repair report submitted: {response.id}")


# =============================================================================
# Complete Repair Workflow
# =============================================================================

def repair_workflow(serial_number: str, symptom: str, cause: str, action: str):
    """Standard repair workflow."""
    
    # Create repair report
    report = UURReport(
        pn="WIDGET-001",
        sn=serial_number,
        rev="A",
        start=datetime.now(),
        processCode=500,
    )
    
    # Record repair
    report.add_repair(
        symptom=symptom,
        cause=cause,
        action=action
    )
    
    # Add technician info
    report.add_misc_info("Technician", os.environ.get("USER", "Unknown"))
    
    # Assume repair successful
    report.result = "Passed"
    
    # Submit
    response = api.report.submit_report(report)
    
    print(f"Repair complete: {serial_number}")
    return response


# repair_workflow(
#     "SN-2024-001239",
#     "Unit not powering on",
#     "Corroded battery contacts",
#     "Cleaned contacts and replaced battery"
# )
