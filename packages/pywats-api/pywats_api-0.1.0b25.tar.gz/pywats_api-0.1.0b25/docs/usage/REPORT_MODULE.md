# Report Module Usage Guide

## Overview

The Report module handles test report submission and querying. It supports two report types:
- **UUT Reports** (Unit Under Test) - Test results for passing/failing units
- **UUR Reports** (Unit Under Repair) - Repair/rework documentation

## Quick Start

```python
from pywats import pyWATS
from pywats.models import UUTReport
from pywats.tools.test_uut import TestUUT

api = pyWATS(base_url="https://wats.example.com", token="credentials")

# Create report using factory
uut = TestUUT(
    part_number="PART-001",
    serial_number="SN-12345",
    revision="A",
    operator="John Doe",
    purpose=10  # Test
)

# Add test steps
root = uut.get_root()
root.add_numeric_step(
    name="Voltage Test",
    value=5.0,
    unit="V",
    comp_op="GELE",
    low_limit=4.5,
    high_limit=5.5,
    status="Passed"
)

# Submit report
report = uut.to_report()
api.report.send_uut_report(report)
```

## Factory Methods (RECOMMENDED)

### Why Use Factory Methods?

The `TestUUT` factory provides:
- ✅ Automatic report structure creation
- ✅ Proper sequence hierarchy
- ✅ Convenient step creation methods
- ✅ Automatic timestamp management
- ✅ Validation during construction

### Creating a Report with TestUUT

```python
from pywats.tools.test_uut import TestUUT

# Initialize with basic info
uut = TestUUT(
    part_number="MODULE-100",
    serial_number="MOD-2025-001",
    revision="B",
    operator="Test Operator",
    station="Station-5",
    purpose=10,  # Test purpose
    operation_type=100  # Operation/process code (optional)
)

# Get root sequence to add steps
root = uut.get_root()

# Add test steps (see step types below)
root.add_numeric_step(...)
root.add_boolean_step(...)

# Convert to report and submit
report = uut.to_report()
api.report.send_uut_report(report)
```

### Factory Constructor Parameters

```python
TestUUT(
    part_number: str,              # Product part number (required)
    serial_number: str,            # Unit serial number (required)
    revision: str = "A",           # Product revision
    operator: str = "Unknown",     # Operator name
    station: str = "",             # Test station ID
    purpose: int = 10,             # Purpose code (10=Test, 20=Debug, etc.)
    operation_type: Optional[int] = None,  # Process/operation code
    batch_serial_number: str = "",         # Batch/lot number
    start_time: Optional[datetime] = None  # Auto-set if not provided
)
```

## Step Types and Methods

All step methods are called on a sequence (typically `root = uut.get_root()`).

### 1. Numeric Step (Single Measurement)

```python
root.add_numeric_step(
    name="Voltage Output",
    value=5.02,
    unit="V",
    comp_op="GELE",      # Comparison: GELE, GT, LT, EQ, NE, GE, LE, LOG
    low_limit=4.5,
    high_limit=5.5,
    status="Passed"      # "Passed", "Failed", "Done", "Skipped", etc.
)
```

**Comparison Operators**:
- `GELE` - Greater or Equal, Less or Equal (in range)
- `GT` - Greater Than
- `LT` - Less Than
- `GE` - Greater or Equal
- `LE` - Less or Equal
- `EQ` - Equal
- `NE` - Not Equal
- `LOG` - Logarithmic

### 2. Multi-Numeric Step (Multiple Measurements)

```python
root.add_multi_numeric_step(
    name="Power Rails",
    measurements=[
        {
            "name": "3.3V Rail",
            "value": 3.31,
            "unit": "V",
            "comp_op": "GELE",
            "low_limit": 3.0,
            "high_limit": 3.6,
            "status": "Passed"
        },
        {
            "name": "5V Rail",
            "value": 5.05,
            "unit": "V",
            "comp_op": "GELE",
            "low_limit": 4.75,
            "high_limit": 5.25,
            "status": "Passed"
        }
    ],
    status="Passed"  # Overall step status
)
```

### 3. Boolean Step (Pass/Fail Test)

```python
root.add_boolean_step(
    name="LED Test",
    value=True,         # True = Passed, False = Failed
    status="Passed"
)
```

### 4. Multi-Boolean Step (Multiple Pass/Fail Tests)

```python
root.add_multi_boolean_step(
    name="Digital I/O Test",
    measurements=[
        {"name": "Output 1", "value": True, "status": "Passed"},
        {"name": "Output 2", "value": True, "status": "Passed"},
        {"name": "Output 3", "value": False, "status": "Failed"}
    ],
    status="Failed"  # Overall - failed if any measurement failed
)
```

### 5. String Step (Text Value)

```python
root.add_string_step(
    name="Firmware Version",
    value="v2.1.5",
    status="Done"
)
```

### 6. Multi-String Step (Multiple Text Values)

```python
root.add_multi_string_step(
    name="Component Versions",
    measurements=[
        {"name": "Bootloader", "value": "v1.2.0", "status": "Done"},
        {"name": "Application", "value": "v2.1.5", "status": "Done"},
        {"name": "FPGA", "value": "v3.0.1", "status": "Done"}
    ],
    status="Done"
)
```

### 7. Nested Sequences (Test Groups)

```python
# Create a sub-sequence for grouping related tests
power_tests = root.add_sequence("Power Supply Tests")

# Add steps to the sub-sequence
power_tests.add_numeric_step(...)
power_tests.add_numeric_step(...)

# Create another sub-sequence
io_tests = root.add_sequence("I/O Tests")
io_tests.add_boolean_step(...)
```

### 8. Chart Step (Graphs/Plots)

```python
root.add_chart_step(
    name="Frequency Response",
    chart_type="LINE",  # LINE, LINE_LOG_X, LINE_LOG_Y, LINE_LOG_XY
    series=[
        {
            "name": "Magnitude",
            "x_values": [100, 1000, 10000, 100000],
            "y_values": [-0.5, -0.1, -3.0, -12.0],
            "x_unit": "Hz",
            "y_unit": "dB"
        }
    ],
    status="Done"
)
```

## Complete Example: Complex Test Report

```python
from pywats.tools.test_uut import TestUUT
from datetime import datetime

# Create test report
uut = TestUUT(
    part_number="POWER-MODULE-500W",
    serial_number="PM500-2025-12345",
    revision="C",
    operator="Jane Smith",
    station="Final-Test-3",
    purpose=10,
    operation_type=50,  # Final test
    batch_serial_number="BATCH-2025-W50",
    start_time=datetime.now()
)

root = uut.get_root()

# 1. Initialization tests
init_seq = root.add_sequence("Initialization")
init_seq.add_string_step("Firmware Version", "v3.2.1", "Done")
init_seq.add_boolean_step("Self-Test", True, "Passed")

# 2. Power output tests
power_seq = root.add_sequence("Power Output Tests")
power_seq.add_multi_numeric_step(
    name="Output Voltages",
    measurements=[
        {
            "name": "12V Output",
            "value": 12.05,
            "unit": "V",
            "comp_op": "GELE",
            "low_limit": 11.4,
            "high_limit": 12.6,
            "status": "Passed"
        },
        {
            "name": "5V Output",
            "value": 5.02,
            "unit": "V",
            "comp_op": "GELE",
            "low_limit": 4.75,
            "high_limit": 5.25,
            "status": "Passed"
        },
        {
            "name": "3.3V Output",
            "value": 3.31,
            "unit": "V",
            "comp_op": "GELE",
            "low_limit": 3.14,
            "high_limit": 3.47,
            "status": "Passed"
        }
    ],
    status="Passed"
)

# 3. Load regulation test
load_seq = root.add_sequence("Load Regulation")
load_seq.add_numeric_step(
    name="12V @ 10A",
    value=11.98,
    unit="V",
    comp_op="GELE",
    low_limit=11.4,
    high_limit=12.6,
    status="Passed"
)
load_seq.add_numeric_step(
    name="12V @ 40A",
    value=11.92,
    unit="V",
    comp_op="GELE",
    low_limit=11.4,
    high_limit=12.6,
    status="Passed"
)

# 4. Protection tests
protection_seq = root.add_sequence("Protection Tests")
protection_seq.add_multi_boolean_step(
    name="Protection Circuits",
    measurements=[
        {"name": "Over-Voltage", "value": True, "status": "Passed"},
        {"name": "Over-Current", "value": True, "status": "Passed"},
        {"name": "Over-Temperature", "value": True, "status": "Passed"},
        {"name": "Short-Circuit", "value": True, "status": "Passed"}
    ],
    status="Passed"
)

# 5. Efficiency test with chart
efficiency_seq = root.add_sequence("Efficiency Test")
efficiency_seq.add_chart_step(
    name="Efficiency vs Load",
    chart_type="LINE",
    series=[
        {
            "name": "Efficiency",
            "x_values": [10, 20, 30, 40],  # Load in amps
            "y_values": [88.5, 91.2, 92.1, 91.8],  # Efficiency %
            "x_unit": "A",
            "y_unit": "%"
        }
    ],
    status="Done"
)

# Convert and submit
report = uut.to_report()
api.report.send_uut_report(report)
print(f"Report submitted for {uut.serial_number}")
```

## Manual Report Creation (Advanced)

If you need fine-grained control, create reports directly:

```python
from pywats.models import UUTReport, UUTInfo, SequenceCall, NumericStep
from datetime import datetime, timezone

# Create report structure manually
report = UUTReport()
report.info = UUTInfo(
    part_number="PART-001",
    serial_number="SN-001",
    revision="A",
    operator="Operator Name",
    start_date_time=datetime.now(timezone.utc)
)

# Create root sequence
root = SequenceCall(name="MainSequence")
report.add_step(root)

# Add step manually
step = NumericStep(
    step_type="ET_NLT",
    name="Voltage",
    value=5.0,
    unit="V",
    comp_op="GELE",
    low_limit=4.5,
    high_limit=5.5,
    status="Passed"
)
root.add_step(step)

# Submit
api.report.send_uut_report(report)
```

**⚠️ Warning**: Manual creation requires understanding the internal structure. Use `TestUUT` factory instead.

## UUR Reports (Repairs)

### Creating Repair Reports

```python
from pywats.models import UURReport

# Option 1: From existing UUT report
uur = api.report.create_uur_report(
    from_uut_report=uut_report,
    failure_category=500,  # Repair category code
    failure_code=501,      # Specific failure code
    description="Replaced capacitor C15",
    action_taken="Component replacement",
    operator="Repair Tech"
)
api.report.send_uur_report(uur)

# Option 2: From part number and process
uur = api.report.create_uur_from_part_and_process(
    part_number="PART-001",
    serial_number="SN-001",
    revision="A",
    process_code=100,
    failure_category=500,
    failure_code=501,
    description="Failed power test",
    operator="Repair Tech"
)
api.report.send_uur_report(uur)
```

## Querying Reports

### Using WATSFilter

```python
from pywats.domains.report import WATSFilter
from datetime import datetime, timedelta

# Filter by part number
filter = WATSFilter(part_number="PART-001")
headers = api.report.query_uut_headers(filter)

# Filter by date range
start = datetime.now() - timedelta(days=7)
filter = WATSFilter(date_from=start, date_to=datetime.now())
headers = api.report.query_uut_headers(filter)

# Filter by serial number
filter = WATSFilter(serial_number="SN-12345")
headers = api.report.query_uut_headers(filter)

# Complex filter
filter = WATSFilter(
    part_number="PART-001",
    date_from=start,
    date_to=datetime.now(),
    passed=True,  # Only passed reports
    top_count=100  # Limit results
)
headers = api.report.query_uut_headers(filter)
```

### Convenience Methods

```python
# Get reports by serial number
reports = api.report.get_uut_reports_by_serial("SN-12345")

# Get reports by part number
reports = api.report.get_uut_reports_by_part("PART-001")

# Get recent reports
reports = api.report.get_recent_uut_reports(days=7, top=50)

# Get today's reports
reports = api.report.get_todays_reports(top=100)

# Load full report by UUID
report = api.report.get_uut_report("report-uuid-here")
```

## Best Practices

### 1. Always Use TestUUT Factory

```python
# ✓ RECOMMENDED
uut = TestUUT(...)
root = uut.get_root()
root.add_numeric_step(...)

# ✗ AVOID - Manual creation is error-prone
report = UUTReport()
report.info = UUTInfo(...)
# ... lots of boilerplate ...
```

### 2. Use Appropriate Step Types

```python
# ✓ Good - use specific types
root.add_numeric_step("Voltage", value=5.0, ...)
root.add_boolean_step("LED Test", value=True, ...)

# ✗ Avoid - generic steps when specific ones exist
root.add_string_step("Voltage", value="5.0", ...)  # Should be numeric
```

### 3. Organize with Sequences

```python
# ✓ Good - grouped logically
power_tests = root.add_sequence("Power Tests")
power_tests.add_numeric_step(...)
power_tests.add_numeric_step(...)

io_tests = root.add_sequence("I/O Tests")
io_tests.add_boolean_step(...)

# ✗ Avoid - flat structure
root.add_numeric_step("Power 1", ...)
root.add_numeric_step("Power 2", ...)
root.add_boolean_step("I/O 1", ...)  # Mixed without grouping
```

### 4. Set Meaningful Status

```python
# ✓ Good - clear status
root.add_numeric_step(..., status="Passed")
root.add_boolean_step(..., status="Failed")
root.add_string_step(..., status="Done")  # For informational steps

# ✗ Avoid - wrong status
root.add_numeric_step(..., status="Done")  # Should be Passed/Failed
```

### 5. Include Units

```python
# ✓ Good - includes units
root.add_numeric_step("Voltage", value=5.0, unit="V", ...)

# ✗ Avoid - missing units
root.add_numeric_step("Voltage", value=5.0, ...)  # What unit?
```

## Common Patterns

### Pattern 1: Test with Retry Logic

```python
def run_test_with_retry(uut: TestUUT, max_retries=3):
    root = uut.get_root()
    
    for attempt in range(max_retries):
        result = perform_test()  # Your test logic
        
        if result.passed:
            root.add_boolean_step(
                f"Test (attempt {attempt + 1})",
                value=True,
                status="Passed"
            )
            break
        else:
            root.add_boolean_step(
                f"Test (attempt {attempt + 1})",
                value=False,
                status="Failed"
            )
    
    return uut.to_report()
```

### Pattern 2: Conditional Testing

```python
def conditional_test(uut: TestUUT):
    root = uut.get_root()
    
    # Initial test
    voltage = measure_voltage()
    root.add_numeric_step("Initial Voltage", voltage, "V", ...)
    
    # Only do burn-in if voltage is good
    if 4.5 <= voltage <= 5.5:
        burnin_seq = root.add_sequence("Burn-In Test")
        # ... burn-in steps ...
    else:
        root.add_string_step("Burn-In", "Skipped - voltage out of range", "Skipped")
    
    return uut.to_report()
```

### Pattern 3: Data-Driven Testing

```python
def data_driven_test(uut: TestUUT, test_points):
    root = uut.get_root()
    
    measurements = []
    for point in test_points:
        value = measure_at_point(point)
        measurements.append({
            "name": point.name,
            "value": value,
            "unit": point.unit,
            "comp_op": "GELE",
            "low_limit": point.min,
            "high_limit": point.max,
            "status": "Passed" if point.min <= value <= point.max else "Failed"
        })
    
    root.add_multi_numeric_step(
        name="Test Points",
        measurements=measurements,
        status="Passed" if all(m["status"] == "Passed" for m in measurements) else "Failed"
    )
    
    return uut.to_report()
```

## Troubleshooting

### Factory Methods Not Working?

```python
# Make sure you import from tools
from pywats.tools.test_uut import TestUUT  # ✓ Correct

from pywats.models import UUTReport  # ✗ Wrong - this is the model, not factory
```

### Steps Not Appearing in Report?

```python
# Make sure you call methods on the sequence, not the factory
root = uut.get_root()  # Get the root sequence
root.add_numeric_step(...)  # ✓ Correct

uut.add_numeric_step(...)  # ✗ Wrong - call on root
```

### Report Submission Failing?

```python
# Convert to report before sending
report = uut.to_report()  # Don't forget this!
api.report.send_uut_report(report)

# Not:
api.report.send_uut_report(uut)  # ✗ Wrong - uut is factory, not report
```

## Related Documentation

- [Production Module](PRODUCTION_MODULE.md) - For serial number management before testing
- [Product Module](PRODUCT_MODULE.md) - For product/revision setup
- [Architecture](../ARCHITECTURE.md) - Overall system design
