"""
Report Domain: Create UUT Report

This example demonstrates creating and submitting UUT (Unit Under Test) reports.
"""
import os
from datetime import datetime
from pywats import pyWATS
from pywats.core import Station
from pywats.models import UUTReport

# =============================================================================
# Setup
# =============================================================================

station = Station(name="TEST-STATION-01", location="Lab A")

api = pyWATS(
    base_url=os.environ.get("WATS_BASE_URL", "https://demo.wats.com"),
    token=os.environ.get("WATS_TOKEN", ""),
    station=station
)


# =============================================================================
# Create Simple UUT Report
# =============================================================================

# Create a basic test report
report = UUTReport(
    pn="WIDGET-001",           # Part number
    sn="SN-2024-001234",       # Serial number
    rev="A",                    # Revision
    result="Passed",           # Overall result
    start=datetime.now(),      # Test start time
)

# Submit to WATS
response = api.report.submit_report(report)
print(f"Report submitted: {response.id}")


# =============================================================================
# Report with Test Steps
# =============================================================================

report = UUTReport(
    pn="WIDGET-001",
    sn="SN-2024-001235",
    rev="A",
    result="Passed",
    start=datetime.now(),
)

# Add a numeric limit test
report.add_numeric_limit_step(
    name="Voltage Check",
    status="Passed",
    value=5.02,
    units="V",
    low_limit=4.8,
    high_limit=5.2,
    comp_operator="GELE"  # Greater than or equal, Less than or equal
)

# Add another measurement
report.add_numeric_limit_step(
    name="Current Draw",
    status="Passed",
    value=0.150,
    units="A",
    low_limit=0.100,
    high_limit=0.200
)

# Add a pass/fail step
report.add_pass_fail_step(
    name="Visual Inspection",
    status="Passed"
)

# Add a string value step
report.add_string_value_step(
    name="Firmware Version",
    status="Passed",
    value="v2.1.3"
)

response = api.report.submit_report(report)
print(f"Report with steps submitted: {response.id}")


# =============================================================================
# Report with Nested Steps (Sequence Calls)
# =============================================================================

report = UUTReport(
    pn="WIDGET-001",
    sn="SN-2024-001236",
    rev="A",
    result="Passed",
    start=datetime.now(),
)

# Create a sequence (group of steps)
sequence = report.add_sequence_call(
    name="Power Supply Tests",
    status="Passed"
)

# Add steps to the sequence
sequence.add_numeric_limit_step(
    name="3.3V Rail",
    status="Passed",
    value=3.31,
    units="V",
    low_limit=3.2,
    high_limit=3.4
)

sequence.add_numeric_limit_step(
    name="5V Rail",
    status="Passed",
    value=5.01,
    units="V",
    low_limit=4.9,
    high_limit=5.1
)

# Add another sequence
sequence2 = report.add_sequence_call(
    name="Communication Tests",
    status="Passed"
)

sequence2.add_pass_fail_step(name="UART Test", status="Passed")
sequence2.add_pass_fail_step(name="I2C Test", status="Passed")

response = api.report.submit_report(report)
print(f"Report with sequences submitted: {response.id}")


# =============================================================================
# Report with Misc Info (Custom Data)
# =============================================================================

report = UUTReport(
    pn="WIDGET-001",
    sn="SN-2024-001237",
    rev="A",
    result="Passed",
    start=datetime.now(),
)

# Add custom metadata
report.add_misc_info("Operator", "John Smith")
report.add_misc_info("Batch", "BATCH-2024-Q4-001")
report.add_misc_info("Temperature", "25°C")
report.add_misc_info("Humidity", "45%")

response = api.report.submit_report(report)
print(f"Report with misc info submitted: {response.id}")


# =============================================================================
# Failed Report
# =============================================================================

report = UUTReport(
    pn="WIDGET-001",
    sn="SN-2024-001238",
    rev="A",
    result="Failed",
    start=datetime.now(),
)

# Add passing step
report.add_numeric_limit_step(
    name="Voltage Check",
    status="Passed",
    value=5.01,
    units="V",
    low_limit=4.8,
    high_limit=5.2
)

# Add failing step
report.add_numeric_limit_step(
    name="Current Draw",
    status="Failed",
    value=0.350,  # Out of spec!
    units="A",
    low_limit=0.100,
    high_limit=0.200
)

response = api.report.submit_report(report)
print(f"Failed report submitted: {response.id}")


# =============================================================================
# Complete Test Report Workflow
# =============================================================================

def run_test_and_report(serial_number: str):
    """Example of a complete test workflow."""
    
    # Create report
    report = UUTReport(
        pn="WIDGET-001",
        sn=serial_number,
        rev="A",
        start=datetime.now(),
    )
    
    all_passed = True
    
    # Simulate tests
    tests = [
        ("Voltage", 5.01, 4.8, 5.2, "V"),
        ("Current", 0.152, 0.1, 0.2, "A"),
        ("Resistance", 99.8, 95, 105, "Ω"),
    ]
    
    for name, value, low, high, units in tests:
        passed = low <= value <= high
        status = "Passed" if passed else "Failed"
        
        if not passed:
            all_passed = False
        
        report.add_numeric_limit_step(
            name=name,
            status=status,
            value=value,
            units=units,
            low_limit=low,
            high_limit=high
        )
    
    # Set overall result
    report.result = "Passed" if all_passed else "Failed"
    
    # Submit
    response = api.report.submit_report(report)
    
    print(f"Test complete: {serial_number} - {report.result}")
    return response


# run_test_and_report("SN-2024-001239")
