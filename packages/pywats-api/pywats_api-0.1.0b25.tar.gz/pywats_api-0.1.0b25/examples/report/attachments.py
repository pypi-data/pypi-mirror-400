"""
Report Domain: Attachments

This example demonstrates adding attachments to reports.
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
# Add File Attachment
# =============================================================================

report = UUTReport(
    pn="WIDGET-001",
    sn="SN-2024-001234",
    rev="A",
    result="Passed",
    start=datetime.now(),
)

# Add a file attachment (reads file from disk)
report.add_attachment_from_file(
    file_path="test_data/waveform.png",
    name="Waveform Capture",
    description="Output waveform during test"
)


# =============================================================================
# Add Binary Data Attachment
# =============================================================================

# Add raw binary data
with open("test_data/measurement.bin", "rb") as f:
    binary_data = f.read()

report.add_attachment(
    name="Raw Measurement Data",
    data=binary_data,
    mime_type="application/octet-stream",
    description="Binary measurement data"
)


# =============================================================================
# Add Text Attachment
# =============================================================================

# Add text content
log_content = """
Test Log - 2024-01-15 10:30:00
=============================
Step 1: Initialize - OK
Step 2: Self test - OK
Step 3: Calibration - OK
Step 4: Measurement - OK
Test completed successfully.
"""

report.add_attachment(
    name="Test Log",
    data=log_content.encode("utf-8"),
    mime_type="text/plain",
    description="Detailed test log"
)


# =============================================================================
# Add JSON Attachment
# =============================================================================

import json

# Add structured data as JSON
test_data = {
    "measurements": [
        {"name": "voltage", "value": 5.02, "unit": "V"},
        {"name": "current", "value": 0.152, "unit": "A"},
    ],
    "environment": {
        "temperature": 25.0,
        "humidity": 45.0
    }
}

report.add_attachment(
    name="Test Data",
    data=json.dumps(test_data, indent=2).encode("utf-8"),
    mime_type="application/json",
    description="Structured test data"
)


# =============================================================================
# Add Image Attachment
# =============================================================================

# Add a captured image
with open("test_data/board_photo.jpg", "rb") as f:
    image_data = f.read()

report.add_attachment(
    name="Board Photo",
    data=image_data,
    mime_type="image/jpeg",
    description="Photo of tested board"
)


# =============================================================================
# Add CSV Attachment
# =============================================================================

# Add measurement data as CSV
csv_content = """Time,Voltage,Current
0.0,5.01,0.150
0.1,5.02,0.151
0.2,5.01,0.152
0.3,5.00,0.151
0.4,5.02,0.150
"""

report.add_attachment(
    name="Measurement Data",
    data=csv_content.encode("utf-8"),
    mime_type="text/csv",
    description="Time-series measurement data"
)


# =============================================================================
# Complete Example with Attachments
# =============================================================================

def create_report_with_attachments(serial_number: str, log_file: str = None):
    """Create a test report with attachments."""
    
    report = UUTReport(
        pn="WIDGET-001",
        sn=serial_number,
        rev="A",
        result="Passed",
        start=datetime.now(),
    )
    
    # Add test steps
    report.add_numeric_limit_step(
        name="Voltage",
        status="Passed",
        value=5.01,
        units="V",
        low_limit=4.8,
        high_limit=5.2
    )
    
    # Add log file if provided
    if log_file and os.path.exists(log_file):
        report.add_attachment_from_file(
            file_path=log_file,
            name="Test Log",
            description="Detailed test log file"
        )
    
    # Add test metadata as JSON
    metadata = {
        "test_version": "1.0.0",
        "station": "TEST-STATION-01",
        "operator": os.environ.get("USER", "unknown"),
        "timestamp": datetime.now().isoformat()
    }
    
    report.add_attachment(
        name="Test Metadata",
        data=json.dumps(metadata, indent=2).encode("utf-8"),
        mime_type="application/json"
    )
    
    return report


# report = create_report_with_attachments("SN-2024-001241", "test.log")
# api.report.submit_report(report)
