"""
Report Domain: Step Types

This example demonstrates different test step types available in reports.
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
# Numeric Limit Step
# =============================================================================

# For measurements with numeric limits
report = UUTReport(pn="DEMO", sn="SN001", rev="A", start=datetime.now())

report.add_numeric_limit_step(
    name="Voltage Test",
    status="Passed",
    value=5.02,
    units="V",
    low_limit=4.8,
    high_limit=5.2,
    comp_operator="GELE"  # >= low AND <= high
)

# Comparison operators:
# "GELE" - Greater than or equal, Less than or equal (4.8 <= x <= 5.2)
# "GTLT" - Greater than, Less than (4.8 < x < 5.2)
# "GELT" - Greater than or equal, Less than (4.8 <= x < 5.2)
# "GTLE" - Greater than, Less than or equal (4.8 < x <= 5.2)
# "EQ"   - Equal to
# "NE"   - Not equal to
# "GT"   - Greater than (low limit only)
# "LT"   - Less than (high limit only)
# "GE"   - Greater than or equal (low limit only)
# "LE"   - Less than or equal (high limit only)


# =============================================================================
# Pass/Fail Step
# =============================================================================

# For simple pass/fail tests
report.add_pass_fail_step(
    name="Visual Inspection",
    status="Passed"
)

report.add_pass_fail_step(
    name="LED Check",
    status="Passed"
)


# =============================================================================
# String Value Step
# =============================================================================

# For text/string results
report.add_string_value_step(
    name="Firmware Version",
    status="Passed",
    value="v2.1.3"
)

report.add_string_value_step(
    name="MAC Address",
    status="Passed",
    value="00:1A:2B:3C:4D:5E"
)


# =============================================================================
# Sequence Call (Grouping Steps)
# =============================================================================

# Create a sequence to group related steps
power_tests = report.add_sequence_call(
    name="Power Supply Tests",
    status="Passed"
)

# Add steps to the sequence
power_tests.add_numeric_limit_step(
    name="3.3V Rail",
    status="Passed",
    value=3.31,
    units="V",
    low_limit=3.2,
    high_limit=3.4
)

power_tests.add_numeric_limit_step(
    name="5V Rail",
    status="Passed",
    value=5.01,
    units="V",
    low_limit=4.9,
    high_limit=5.1
)


# =============================================================================
# Nested Sequences
# =============================================================================

# Sequences can be nested
main_sequence = report.add_sequence_call(
    name="Functional Tests",
    status="Passed"
)

# Sub-sequence 1
comm_tests = main_sequence.add_sequence_call(
    name="Communication Tests",
    status="Passed"
)
comm_tests.add_pass_fail_step(name="UART", status="Passed")
comm_tests.add_pass_fail_step(name="SPI", status="Passed")
comm_tests.add_pass_fail_step(name="I2C", status="Passed")

# Sub-sequence 2
io_tests = main_sequence.add_sequence_call(
    name="I/O Tests",
    status="Passed"
)
io_tests.add_pass_fail_step(name="GPIO Input", status="Passed")
io_tests.add_pass_fail_step(name="GPIO Output", status="Passed")


# =============================================================================
# Chart (Multiple Measurements)
# =============================================================================

# For waveform or multi-point data
report.add_chart(
    name="Frequency Response",
    status="Passed",
    chart_type="line",
    x_label="Frequency (Hz)",
    y_label="Amplitude (dB)",
    data=[
        (100, -0.5),
        (1000, 0.0),
        (10000, -0.3),
        (20000, -1.2),
    ]
)


# =============================================================================
# Message Step
# =============================================================================

# For logging information
report.add_message_step(
    name="Test Info",
    status="Done",
    message="Test completed without issues"
)


# =============================================================================
# Complete Example
# =============================================================================

def create_comprehensive_report(serial_number: str):
    """Create a report demonstrating all step types."""
    
    report = UUTReport(
        pn="WIDGET-001",
        sn=serial_number,
        rev="A",
        start=datetime.now(),
    )
    
    # Setup sequence
    setup = report.add_sequence_call(name="Setup", status="Passed")
    setup.add_string_value_step(name="Firmware", status="Passed", value="v2.1.3")
    setup.add_pass_fail_step(name="Initialize", status="Passed")
    
    # Power tests
    power = report.add_sequence_call(name="Power Tests", status="Passed")
    power.add_numeric_limit_step(
        name="Voltage", status="Passed",
        value=5.01, units="V", low_limit=4.8, high_limit=5.2
    )
    power.add_numeric_limit_step(
        name="Current", status="Passed",
        value=0.152, units="A", low_limit=0.1, high_limit=0.2
    )
    
    # Functional tests
    func = report.add_sequence_call(name="Functional Tests", status="Passed")
    func.add_pass_fail_step(name="Self Test", status="Passed")
    func.add_pass_fail_step(name="Memory Test", status="Passed")
    
    # Final inspection
    report.add_pass_fail_step(name="Visual Inspection", status="Passed")
    
    # Set result
    report.result = "Passed"
    
    return report


# report = create_comprehensive_report("SN-2024-001240")
# api.report.submit_report(report)
