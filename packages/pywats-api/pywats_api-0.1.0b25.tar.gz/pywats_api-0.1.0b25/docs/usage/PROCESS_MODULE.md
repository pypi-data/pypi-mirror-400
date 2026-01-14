# Process Module Usage Guide

## Overview

The Process module provides access to process/operation definitions in WATS. Processes define the types of operations that can be performed during manufacturing:

- **Test Operations** - End-of-line tests, ICT tests, functional tests
- **Repair Operations** - Repair, RMA repair, rework
- **WIP Operations** - Work-in-progress tracking, assembly steps

## Quick Start

```python
from pywats import pyWATS

api = pyWATS(base_url="https://wats.example.com", token="credentials")

# Get all processes
processes = api.process.get_processes()

# Get a specific test operation
test_op = api.process.get_test_operation(100)  # By code
test_op = api.process.get_test_operation("End of line test")  # By name

# Validate a process code
if api.process.is_valid_test_operation(100):
    print("Valid test operation")
```

## Process Types

| Type | Flag | Typical Codes | Examples |
|------|------|--------------|----------|
| Test | `is_test_operation` | 100-499 | End of line test, ICT, FCT |
| Repair | `is_repair_operation` | 500-599 | Repair, RMA Repair |
| WIP | `is_wip_operation` | 200-299 | Assembly, Inspection |

```python
# Check process type
if process.is_test_operation:
    print("This is a test operation")
elif process.is_repair_operation:
    print("This is a repair operation")
elif process.is_wip_operation:
    print("This is a WIP operation")
```

## Caching

The Process service maintains an in-memory cache to minimize API calls. By default, the cache refreshes every 5 minutes.

```python
# Configure cache refresh interval (seconds)
api.process.refresh_interval = 600  # 10 minutes

# Force cache refresh
api.process.refresh()

# Check cache status
print(f"Last refresh: {api.process.last_refresh}")
print(f"Refresh interval: {api.process.refresh_interval}s")
```

## Basic Operations

### 1. Get All Processes

```python
# Get all processes (cached)
processes = api.process.get_processes()

for proc in processes:
    print(f"{proc.code}: {proc.name}")
    if proc.is_test_operation:
        print("  Type: Test Operation")
    elif proc.is_repair_operation:
        print("  Type: Repair Operation")
    elif proc.is_wip_operation:
        print("  Type: WIP Operation")
```

### 2. Get Processes by Type

```python
# Get test operations only
test_ops = api.process.get_test_operations()
for op in test_ops:
    print(f"{op.code}: {op.name}")

# Get repair operations only
repair_ops = api.process.get_repair_operations()

# Get WIP operations only
wip_ops = api.process.get_wip_operations()
```

### 3. Get Specific Process

```python
# By code (int)
process = api.process.get_process(100)

# By name (str, case-insensitive)
process = api.process.get_process("End of line test")

if process:
    print(f"Found: {process.code} - {process.name}")
else:
    print("Process not found")
```

### 4. Get Specific Operation Types

```python
# Get test operation (returns None if not a test operation)
test_op = api.process.get_test_operation(100)
test_op = api.process.get_test_operation("ICT Test")

# Get repair operation (returns None if not a repair operation)
repair_op = api.process.get_repair_operation(500)
repair_op = api.process.get_repair_operation("Repair")

# Get WIP operation
wip_op = api.process.get_wip_operation(200)
wip_op = api.process.get_wip_operation("Assembly")
```

## Validation Helpers

### Validate Process Codes

```python
# Validate test operation code
if api.process.is_valid_test_operation(100):
    print("Code 100 is a valid test operation")
else:
    print("Code 100 is NOT a valid test operation")

# Validate repair operation code
if api.process.is_valid_repair_operation(500):
    print("Code 500 is a valid repair operation")

# Validate WIP operation code
if api.process.is_valid_wip_operation(200):
    print("Code 200 is a valid WIP operation")
```

### Get Default Codes

```python
# Get default test code (first available or 100 as fallback)
default_test = api.process.get_default_test_code()
print(f"Default test code: {default_test}")

# Get default repair code (first available or 500 as fallback)
default_repair = api.process.get_default_repair_code()
print(f"Default repair code: {default_repair}")
```

## Common Patterns

### Pattern 1: Process Validation Before Report Submission

```python
def validate_report_process(api, process_code):
    """Validate process code before submitting a report"""
    
    if not api.process.is_valid_test_operation(process_code):
        raise ValueError(f"Invalid test operation code: {process_code}")
    
    process = api.process.get_test_operation(process_code)
    return process.name

# Usage
try:
    process_name = validate_report_process(api, 100)
    print(f"Submitting report for: {process_name}")
except ValueError as e:
    print(f"Error: {e}")
```

### Pattern 2: Display Available Operations

```python
def display_available_operations(api):
    """Display all available operations by type"""
    
    print("=== TEST OPERATIONS ===")
    for op in api.process.get_test_operations():
        print(f"  {op.code:4d}: {op.name}")
    
    print("\n=== REPAIR OPERATIONS ===")
    for op in api.process.get_repair_operations():
        print(f"  {op.code:4d}: {op.name}")
    
    print("\n=== WIP OPERATIONS ===")
    for op in api.process.get_wip_operations():
        print(f"  {op.code:4d}: {op.name}")
```

### Pattern 3: Process Code Lookup Table

```python
def build_process_lookup(api):
    """Build lookup table for process codes"""
    
    lookup = {
        "test": {},
        "repair": {},
        "wip": {},
    }
    
    for proc in api.process.get_processes():
        if proc.is_test_operation:
            lookup["test"][proc.code] = proc.name
        elif proc.is_repair_operation:
            lookup["repair"][proc.code] = proc.name
        elif proc.is_wip_operation:
            lookup["wip"][proc.code] = proc.name
    
    return lookup

# Usage
lookup = build_process_lookup(api)
print(f"Test operation 100: {lookup['test'].get(100, 'Unknown')}")
```

### Pattern 4: Automatic Process Selection

```python
def get_appropriate_process(api, operation_type):
    """Get appropriate process code for operation type"""
    
    if operation_type == "test":
        return api.process.get_default_test_code()
    elif operation_type == "repair":
        return api.process.get_default_repair_code()
    else:
        wip_ops = api.process.get_wip_operations()
        return wip_ops[0].code if wip_ops else 200
```

## Internal API (Advanced)

The internal API provides additional functionality not available in the public API:

```python
# Check if internal service is available
if hasattr(api, 'process_internal'):
    # Get processes with full details (ProcessID, etc.)
    processes = api.process_internal.get_processes()
    
    # Get repair operation configurations
    configs = api.process_internal.get_repair_operation_configs()
    
    # Get repair categories (fail codes)
    categories = api.process_internal.get_repair_categories(500)
    
    # Get flattened fail codes
    fail_codes = api.process_internal.get_fail_codes(500)
```

⚠️ **Warning:** Internal API endpoints may change without notice.

## Model Reference

### ProcessInfo

| Field | Type | Description |
|-------|------|-------------|
| `code` | int | Process code (e.g., 100, 500) |
| `name` | str | Process name |
| `description` | str | Process description |
| `is_test_operation` | bool | True if test operation |
| `is_repair_operation` | bool | True if repair operation |
| `is_wip_operation` | bool | True if WIP operation |
| `process_id` | UUID | Process GUID (internal API) |
| `process_index` | int | Process order index |
| `state` | int | Process state (1=active) |

### RepairCategory (Internal API)

| Field | Type | Description |
|-------|------|-------------|
| `guid` | UUID | Category identifier |
| `description` | str | Category name |
| `selectable` | bool | Can be selected |
| `sort_order` | int | Display order |
| `failure_type` | int | Failure type code |
| `fail_codes` | List | Nested fail codes |

### RepairOperationConfig (Internal API)

| Field | Type | Description |
|-------|------|-------------|
| `description` | str | Configuration name |
| `uut_required` | int | UUT required flag |
| `bom_required` | int | BOM required flag |
| `vendor_required` | int | Vendor required flag |
| `comp_ref_mask` | str | Component reference regex |
| `categories` | List | Repair categories |

## Best Practices

### 1. Use Caching Effectively

```python
# Don't disable caching unless necessary
api.process.refresh_interval = 300  # Keep reasonable interval

# Only refresh when needed
if need_fresh_data:
    api.process.refresh()
```

### 2. Validate Before Operations

```python
# Always validate process codes
if not api.process.is_valid_test_operation(process_code):
    raise ValueError(f"Invalid process code: {process_code}")
```

### 3. Use Type-Specific Methods

```python
# Good - type-safe lookup
test_op = api.process.get_test_operation(100)

# Less safe - could return wrong type
process = api.process.get_process(100)
```

### 4. Handle Missing Processes

```python
# Always check for None
process = api.process.get_test_operation(code)
if process is None:
    # Use default or raise error
    code = api.process.get_default_test_code()
```

## Troubleshooting

### Process Not Found

```python
# Check if process exists
process = api.process.get_process(code)
if process is None:
    # List all available processes
    print("Available processes:")
    for p in api.process.get_processes():
        print(f"  {p.code}: {p.name}")
```

### Wrong Process Type

```python
# get_test_operation returns None if not a test operation
process = api.process.get_test_operation(500)  # Returns None (500 is repair)

# Use generic get_process to check type
process = api.process.get_process(500)
if process:
    if process.is_repair_operation:
        print("This is a repair operation, not a test operation")
```

### Stale Cache Data

```python
# Force refresh if you expect new processes
api.process.refresh()

# Or reduce refresh interval
api.process.refresh_interval = 60  # 1 minute
```

## Limitations

### Read-Only Operations

Process definitions are **read-only** through the PyWATS API. 
Creating, updating, or deleting processes is not supported.

Process management must be done through the WATS Admin interface:
- Add new test operations
- Configure repair operations  
- Set up WIP operations

The API provides:
- ✅ List all processes
- ✅ Filter by process type
- ✅ Look up by code or name
- ✅ Validate process codes
- ❌ Create processes
- ❌ Update processes
- ❌ Delete processes

## Related Documentation

- [Report Module](REPORT_MODULE.md) - Test reports using process codes
- [Production Module](PRODUCTION_MODULE.md) - Production with process tracking
- [Software Module](SOFTWARE_MODULE.md) - Software distribution
