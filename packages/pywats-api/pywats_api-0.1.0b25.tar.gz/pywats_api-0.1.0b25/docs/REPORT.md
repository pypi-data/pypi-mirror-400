# Report Domain

The Report domain manages test reports (UUT/UUR) containing test results, measurements, and step hierarchies. Test reports are the core data structure in WATS - they capture what happened when a unit was tested, including all measurements, pass/fail results, and contextual information.

## Table of Contents

- [Quick Start](#quick-start)
- [Core Concepts](#core-concepts)
- [UUT Reports (Unit Under Test)](#uut-reports-unit-under-test)
- [UUR Reports (Unit Under Repair)](#uur-reports-unit-under-repair)
- [Test Steps](#test-steps)
- [Querying Reports](#querying-reports)
- [Report Attachments](#report-attachments)
- [Advanced Usage](#advanced-usage)
- [API Reference](#api-reference)

---

## Quick Start

```python
from pywats import pyWATS

# Initialize
api = pyWATS(
    base_url="https://your-wats-server.com",
    token="your-api-token"
)

# Create a UUT (test) report
report = api.report.create_uut_report(
    operator="John Smith",
    part_number="WIDGET-001",
    revision="B",
    serial_number="W12345",
    operation_type=100,  # End-of-line test
    station_name="FINAL-TEST-01",
    location="Production Floor"
)

# Add test steps
root = report.get_root_sequence_call()

root.add_numeric_limit_step(
    name="Supply Voltage",
    value=5.02,
    units="V",
    low_limit=4.9,
    high_limit=5.1,
    status="Passed"
)

root.add_pass_fail_step(
    name="Communication Test",
    status="Passed"
)

# Submit report
report_id = api.report.submit_report(report)
print(f"Report submitted: {report_id}")

# Query reports
from pywats.domains.report import WATSFilter

filter_obj = WATSFilter(
    part_number="WIDGET-001",
    days=7  # Last 7 days
)

headers = api.report.query_uut_headers(filter_obj)
print(f"Found {len(headers)} reports")
```

---

## Core Concepts

### UUT Report (Unit Under Test)
A **UUT Report** documents a test session for a single unit. It contains:
- Unit identification (part number, serial, revision)
- Station information (where tested)
- Test results (steps, measurements, pass/fail)
- Timing information (start time, execution time)
- Custom metadata

**Key attributes:**
- `pn`: Part number
- `sn`: Serial number
- `rev`: Revision
- `process_code`: Operation type (e.g., 100 = EOL test)
- `result`: Overall result ("P" = Pass, "F" = Fail)
- `root`: Root SequenceCall containing all test steps

### UUR Report (Unit Under Repair)
A **UUR Report** documents a repair operation on a failed unit. It contains:
- Reference to the original failed UUT
- Repair actions taken
- Failure analysis
- Re-test results

**Key relationship:**
- `repair_process_code`: Repair operation type (typically 500)
- `test_operation_code`: Original test that failed

### Test Steps
Test steps are organized hierarchically:

- **SequenceCall**: Container for other steps (like a folder)
- **NumericStep**: Measurement with limits (voltage, current, etc.)
- **BooleanStep**: Pass/Fail test
- **StringStep**: Text verification
- **ChartStep**: Graphical data (waveforms, plots)
- **GenericStep**: Actions, labels, comments

### Step Hierarchy
Steps form a tree structure:

```
MainSequence (root)
├─ Power Supply Tests (SequenceCall)
│  ├─ 3.3V Rail (NumericStep)
│  ├─ 5V Rail (NumericStep)
│  └─ 12V Rail (NumericStep)
├─ Communication Tests (SequenceCall)
│  ├─ UART Test (BooleanStep)
│  └─ I2C Test (BooleanStep)
└─ Final Verification (SequenceCall)
   └─ Overall Status (BooleanStep)
```

---

## UUT Reports (Unit Under Test)

### Create UUT Report

```python
# Using factory method (recommended)
report = api.report.create_uut_report(
    operator="Jane Doe",
    part_number="PCB-MAIN-001",
    revision="C",
    serial_number="PCB12345",
    operation_type=50,  # FCT test
    station_name="FCT-STATION-02",
    location="Factory Floor",
    purpose="Production"
)

# Set overall result
report.result = "P"  # or "F" for failed

# Get root sequence to add steps
root = report.get_root_sequence_call()
```

### Add Numeric Test Steps

```python
# Simple numeric limit test
root.add_numeric_limit_step(
    name="3.3V Rail",
    value=3.31,
    units="V",
    low_limit=3.2,
    high_limit=3.4,
    status="Passed"
)

# Using comparison operator explicitly
from pywats.domains.report.report_models.uut.steps.comp_operator import CompOp

root.add_numeric_step(
    name="Temperature",
    value=25.5,
    unit="°C",
    comp_op=CompOp.GELE,  # Greater or Equal, Less or Equal
    low_limit=20.0,
    high_limit=30.0,
    status="P"
)

# Log value only (no limits)
root.add_numeric_step(
    name="Ambient Humidity",
    value=45.2,
    unit="%",
    comp_op=CompOp.LOG,  # Log only, no comparison
    status="P"
)
```

### Add Boolean Test Steps

```python
# Simple pass/fail
root.add_pass_fail_step(
    name="Power On Self Test",
    status="Passed"
)

# Using explicit status codes
root.add_boolean_step(
    name="Firmware Load",
    status="P"  # P=Pass, F=Fail, T=Terminated, etc.
)

# Failed step
root.add_pass_fail_step(
    name="Network Connection",
    status="Failed"
)
```

### Add String Test Steps

```python
# String comparison
root.add_string_step(
    name="Firmware Version",
    value="2.1.5",
    limit="2.1.5",  # Expected value
    comp_op=CompOp.CASESENSIT,  # Case-sensitive compare
    status="P"
)

# Log string value
root.add_string_step(
    name="MAC Address",
    value="00:1A:2B:3C:4D:5E",
    comp_op=CompOp.LOG,
    status="P"
)
```

### Create Sequence Hierarchy

```python
# Create a sequence (test group)
power_seq = root.add_sequence_call(
    name="Power Supply Tests",
    file_name="power_tests.py",
    version="1.0.0"
)

# Add tests to the sequence
power_seq.add_numeric_limit_step(
    name="3.3V Rail", value=3.31, units="V",
    low_limit=3.2, high_limit=3.4, status="Passed"
)

power_seq.add_numeric_limit_step(
    name="5V Rail", value=5.01, units="V",
    low_limit=4.9, high_limit=5.1, status="Passed"
)

# Nested sequences
comm_seq = root.add_sequence_call(name="Communication Tests")
uart_tests = comm_seq.add_sequence_call(name="UART Tests")
uart_tests.add_pass_fail_step(name="Loopback Test", status="Passed")
```

### Add Misc Info (Custom Metadata)

```python
# Add custom key-value metadata
report.add_misc_info("LotNumber", "LOT-2025-W01")
report.add_misc_info("WorkOrder", "WO-12345")
report.add_misc_info("Temperature", "25°C")
report.add_misc_info("Operator_Badge", "EMP-789")

# Access misc info
misc = report.misc_info
for item in misc:
    print(f"{item.key}: {item.value}")
```

### Submit Report

```python
# Submit to server
report_id = api.report.submit_report(report)

if report_id:
    print(f"✓ Report submitted successfully: {report_id}")
else:
    print("✗ Failed to submit report")
```

---

## UUR Reports (Unit Under Repair)

### Create UUR from Failed UUT

```python
# After a unit fails a test, create UUR for repair

# 1. Create and submit failed UUT
failed_uut = api.report.create_uut_report(
    operator="Test Op",
    part_number="WIDGET-001",
    revision="A",
    serial_number="W-FAIL-001",
    operation_type=100,
    station_name="TEST-01"
)

root = failed_uut.get_root_sequence_call()
root.add_pass_fail_step(name="Power Test", status="Failed")

uut_id = api.report.submit_report(failed_uut)

# 2. Create UUR from the failed UUT
uur = api.report.create_uur_report(
    failed_uut,  # Pass the UUT object
    repair_process_code=500,  # Default repair code
    operator="Repair Tech",
    station_name="REPAIR-STATION-01"
)

# 3. Add repair steps
uur_root = uur.get_root_sequence_call()

uur_root.add_generic_step(
    step_type="Action",
    name="Replaced faulty capacitor C15",
    status="P"
)

uur_root.add_pass_fail_step(
    name="Re-test Power Supply",
    status="Passed"
)

# 4. Submit UUR
uur_id = api.report.submit_report(uur)
```

### Create UUR from Part/Process

```python
# Create UUR when you don't have the UUT object
uur = api.report.create_uur_from_part_and_process(
    part_number="WIDGET-001",
    serial_number="W-REPAIR-002",
    revision="A",
    test_operation_code=100,  # Original test operation
    repair_process_code=500,  # Repair operation
    operator="Repair Specialist"
)

# Add repair documentation
uur_root = uur.get_root_sequence_call()

uur_root.add_string_step(
    name="Failure Mode",
    value="No output on 12V rail",
    comp_op=CompOp.LOG,
    status="P"
)

uur_root.add_string_step(
    name="Root Cause",
    value="Damaged voltage regulator U5",
    comp_op=CompOp.LOG,
    status="P"
)

uur_root.add_string_step(
    name="Corrective Action",
    value="Replaced U5 with known good part",
    comp_op=CompOp.LOG,
    status="P"
)

api.report.submit_report(uur)
```

---

## Test Steps

### Numeric Steps with Comparison Operators

```python
from pywats.domains.report.report_models.uut.steps.comp_operator import CompOp

# GELE - Greater or Equal, Less or Equal (standard range)
root.add_numeric_step(
    name="Voltage", value=5.0, unit="V",
    comp_op=CompOp.GELE, low_limit=4.5, high_limit=5.5,
    status="P"
)

# GT - Greater Than
root.add_numeric_step(
    name="Signal Strength", value=75, unit="dBm",
    comp_op=CompOp.GT, low_limit=70,
    status="P"
)

# LT - Less Than
root.add_numeric_step(
    name="Noise Level", value=5, unit="mV",
    comp_op=CompOp.LT, high_limit=10,
    status="P"
)

# EQ - Equal
root.add_numeric_step(
    name="Counter Value", value=100,
    comp_op=CompOp.EQ, low_limit=100,
    status="P"
)

# NE - Not Equal
root.add_numeric_step(
    name="Error Code", value=0,
    comp_op=CompOp.NE, low_limit=1,  # Should NOT be 1
    status="P"
)

# LOG - Log only (no comparison)
root.add_numeric_step(
    name="Timestamp", value=1640000000,
    comp_op=CompOp.LOG,
    status="P"
)
```

### Multi-Measurement Steps

```python
# Create a multi-measurement container
multi_num = root.add_multiple_numeric_limit_test(
    name="Power Rail Measurements"
)

# Add multiple measurements
multi_num.add_measurement(
    name="3.3V Rail", value=3.31, unit="V",
    comp_op=CompOp.GELE, low_limit=3.2, high_limit=3.4,
    status="P"
)

multi_num.add_measurement(
    name="5V Rail", value=5.01, unit="V",
    comp_op=CompOp.GELE, low_limit=4.9, high_limit=5.1,
    status="P"
)

multi_num.add_measurement(
    name="12V Rail", value=12.05, unit="V",
    comp_op=CompOp.GELE, low_limit=11.5, high_limit=12.5,
    status="P"
)

# String multi-measurement
multi_str = root.add_multiple_string_value_test(
    name="Device Information"
)

multi_str.add_measurement(
    name="Model", value="WIDGET-X1",
    comp_op=CompOp.CASESENSIT, limit="WIDGET-X1",
    status="P"
)

multi_str.add_measurement(
    name="Serial", value="SN12345",
    comp_op=CompOp.LOG,
    status="P"
)
```

### Generic Steps (Actions, Comments)

```python
from pywats.domains.report.report_models.uut.steps.generic_step import FlowType

# Action step
root.add_generic_step(
    step_type=FlowType.Action,
    name="Initialize Hardware",
    status="P"
)

# Label/Comment
root.add_generic_step(
    step_type=FlowType.Label,
    name="Starting communication tests...",
    status="P"
)

# Goto (control flow)
root.add_generic_step(
    step_type=FlowType.Goto,
    name="Jump to cleanup",
    status="P"
)
```

---

## Querying Reports

### Query UUT Report Headers

```python
from pywats.domains.report import WATSFilter

# Basic query - last 7 days
filter_obj = WATSFilter(days=7)
headers = api.report.query_uut_headers(filter_obj)

print(f"Found {len(headers)} reports")
for header in headers[:10]:
    print(f"{header.serial_number}: {header.result} ({header.start_time})")

# Filter by part number
filter_obj = WATSFilter(
    part_number="WIDGET-001",
    days=30
)
headers = api.report.query_uut_headers(filter_obj)

# Filter by serial number
filter_obj = WATSFilter(
    serial_number="W12345"
)
headers = api.report.query_uut_headers(filter_obj)

# Filter by result (passed/failed)
filter_obj = WATSFilter(
    part_number="WIDGET-001",
    result="Failed",  # or "Passed"
    days=7
)
headers = api.report.query_uut_headers(filter_obj)

# Date range
from datetime import datetime, timedelta

end_date = datetime.now()
start_date = end_date - timedelta(days=90)

filter_obj = WATSFilter(
    part_number="WIDGET-001",
    start_date_time=start_date,
    end_date_time=end_date
)
headers = api.report.query_uut_headers(filter_obj)

# Limit results
filter_obj = WATSFilter(
    part_number="WIDGET-001",
    days=30,
    top_count=100  # Limit to 100 results
)
headers = api.report.query_uut_headers(filter_obj)
```

### Load Full Report

```python
# Get report by UUID
report_id = "550e8400-e29b-41d4-a716-446655440000"
report = api.report.get_uut_report(report_id)

if report:
    print(f"Loaded report: {report.sn}")
    print(f"Result: {report.result}")
    print(f"Station: {report.station_name}")
    
    # Access steps
    root = report.get_root_sequence_call()
    print(f"Steps: {len(root.steps)}")
```

### Query by Operation Type

```python
# Get reports for specific test operation
filter_obj = WATSFilter(
    part_number="WIDGET-001",
    operation_type=100,  # EOL test
    days=7
)
headers = api.report.query_uut_headers(filter_obj)

print(f"EOL test reports: {len(headers)}")
```

---

## Report Attachments

### Add Attachment to Report

```python
# Create report
report = api.report.create_uut_report(
    operator="Tester",
    part_number="WIDGET-001",
    revision="A",
    serial_number="W12345",
    operation_type=100
)

# Add steps...
root = report.get_root_sequence_call()
root.add_pass_fail_step(name="Test", status="Passed")

# Add attachment (e.g., screenshot, log file)
with open("test_screenshot.png", "rb") as f:
    file_data = f.read()

from pywats.domains.report.report_models import Attachment

attachment = Attachment(
    file_name="test_screenshot.png",
    mime_type="image/png",
    data=file_data
)

report.add_attachment(attachment)

# Submit with attachment
api.report.submit_report(report)
```

### Download Attachments

```python
# Get report header
filter_obj = WATSFilter(serial_number="W12345")
headers = api.report.query_uut_headers(filter_obj)

if headers:
    header = headers[0]
    
    # Get attachments for this report
    attachments = api.report.get_attachments(str(header.uuid))
    
    for att in attachments:
        print(f"Attachment: {att.name} ({att.size} bytes)")
        
        # Download attachment data
        data = api.report.download_attachment(
            str(header.uuid),
            att.name
        )
        
        # Save to file
        with open(f"downloaded_{att.name}", "wb") as f:
            f.write(data)
```

---

## Advanced Usage

### Complete Test Workflow

```python
def run_test_and_report(serial_number, part_number, revision):
    """Complete test workflow with reporting"""
    
    # 1. Create report
    report = api.report.create_uut_report(
        operator="AutoTest",
        part_number=part_number,
        revision=revision,
        serial_number=serial_number,
        operation_type=100,
        station_name="AUTO-TEST-01"
    )
    
    root = report.get_root_sequence_call()
    all_passed = True
    
    # 2. Run power tests
    power_seq = root.add_sequence_call(name="Power Supply Tests")
    
    voltage_3v3 = measure_voltage("3V3")  # Your measurement function
    power_seq.add_numeric_limit_step(
        name="3.3V Rail",
        value=voltage_3v3,
        units="V",
        low_limit=3.2,
        high_limit=3.4,
        status="Passed" if 3.2 <= voltage_3v3 <= 3.4 else "Failed"
    )
    
    if not (3.2 <= voltage_3v3 <= 3.4):
        all_passed = False
    
    # 3. Run communication tests
    comm_seq = root.add_sequence_call(name="Communication Tests")
    
    uart_ok = test_uart()  # Your test function
    comm_seq.add_pass_fail_step(
        name="UART Loopback",
        status="Passed" if uart_ok else "Failed"
    )
    
    if not uart_ok:
        all_passed = False
    
    # 4. Set overall result
    report.result = "P" if all_passed else "F"
    
    # 5. Submit report
    report_id = api.report.submit_report(report)
    
    # 6. Update production unit status
    if all_passed:
        api.production.set_unit_phase(
            serial_number, part_number,
            phase="Passed"
        )
    else:
        api.production.set_unit_phase(
            serial_number, part_number,
            phase="Failed"
        )
    
    return all_passed, report_id

# Run it
passed, report_id = run_test_and_report("W12345", "WIDGET-001", "A")
print(f"Test {'PASSED' if passed else 'FAILED'} - Report: {report_id}")
```

### Failure Analysis Report

```python
def generate_failure_report(days=7):
    """Generate failure analysis from recent tests"""
    from pywats.domains.report import WATSFilter
    
    # Get failed reports
    filter_obj = WATSFilter(
        result="Failed",
        days=days
    )
    
    headers = api.report.query_uut_headers(filter_obj)
    
    print(f"\n=== FAILURE ANALYSIS ({days} days) ===\n")
    print(f"Total failures: {len(headers)}")
    
    # Group by part number
    failures_by_part = {}
    for header in headers:
        pn = header.part_number
        if pn not in failures_by_part:
            failures_by_part[pn] = []
        failures_by_part[pn].append(header)
    
    # Print summary
    for pn, fails in sorted(failures_by_part.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"\n{pn}: {len(fails)} failures")
        
        # Show first few
        for header in fails[:5]:
            print(f"  {header.serial_number} - {header.start_time}")
    
    print("\n" + "="*50 + "\n")

# Run it
generate_failure_report(days=7)
```

---

## API Reference

### ReportService Methods

#### UUT Report Operations
- `create_uut_report(...)` → `UUTReport` - Create new UUT report
- `query_uut_headers(filter)` → `List[ReportHeader]` - Query report headers
- `get_uut_report(report_id)` → `Optional[UUTReport]` - Get full report
- `submit_report(report)` → `Optional[UUID]` - Submit report to server

#### UUR Report Operations  
- `create_uur_report(uut, ...)` → `UURReport` - Create UUR from UUT
- `create_uur_from_part_and_process(...)` → `UURReport` - Create UUR from metadata

#### Attachment Operations
- `get_attachments(report_id)` → `List[Attachment]` - Get attachment list
- `download_attachment(report_id, filename)` → `bytes` - Download attachment data

### Models

#### UUTReport
- `pn`: Part number
- `sn`: Serial number
- `rev`: Revision
- `process_code`: Operation type
- `result`: "P" or "F"
- `station_name`: Station name
- `root`: SequenceCall (test steps)
- `info`: UUTInfo (metadata)

#### SequenceCall
- `name`: Sequence name
- `status`: Overall status
- `steps`: List of child steps
- Methods: `add_numeric_step()`, `add_pass_fail_step()`, `add_sequence_call()`, etc.

#### WATSFilter
- `part_number`: Filter by part
- `serial_number`: Filter by serial
- `result`: "Passed" or "Failed"
- `days`: Last N days
- `start_date_time`, `end_date_time`: Date range
- `operation_type`: Operation code
- `top_count`: Limit results

---

## Best Practices

1. **Always add at least one step** - Reports must have test steps
2. **Set overall result** - Set `report.result` to "P" or "F"
3. **Use meaningful step names** - Clear, descriptive names
4. **Organize with sequences** - Group related tests
5. **Add misc info for context** - Lot numbers, work orders, etc.
6. **Submit promptly** - Don't delay report submission
7. **Include units** - Always specify measurement units
8. **Set proper limits** - Define pass/fail criteria
9. **Log important values** - Use CompOp.LOG for reference data
10. **Link to production** - Update unit status after testing

---

## See Also

- [Production Domain](PRODUCTION.md) - Managing units and updating status
- [Analytics Domain](ANALYTICS.md) - Analyzing test results and yield
- [Process Domain](PROCESS.md) - Defining operation types
