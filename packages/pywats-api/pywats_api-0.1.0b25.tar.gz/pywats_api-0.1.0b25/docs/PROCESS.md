# Process Domain

The Process domain provides access to process and operation type definitions. Processes define the types of operations performed on units (e.g., Test, Repair, Assembly). This domain uses an in-memory cache with configurable refresh intervals to optimize performance by reducing API calls. It provides read-only access to process definitions.

## Table of Contents

- [Quick Start](#quick-start)
- [Core Concepts](#core-concepts)
- [Process Operations](#process-operations)
- [Cache Management](#cache-management)
- [Operation Types](#operation-types)
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

# Get test operation
test_op = api.process.get_test_operation("ICT")

if test_op:
    print(f"Operation: {test_op.name}")
    print(f"Code: {test_op.code}")
    print(f"Type: {test_op.process_type}")

# Get repair operation
repair_op = api.process.get_repair_operation("Rework")

# Get operation by name or code
operation = api.process.get_operation("FCT")  # Can be name or code

# Refresh cache manually
api.process.refresh()

print(f"Cache last refreshed: {api.process.last_refresh}")
print(f"Refresh interval: {api.process.refresh_interval} seconds")
```

---

## Core Concepts

### Process (Operation Type)
A **Process** defines a type of operation:
- `name`: Operation name (e.g., "In-Circuit Test")
- `code`: Short code (e.g., "ICT")
- `process_type`: Type (TEST, REPAIR, ASSEMBLY, etc.)
- `description`: Operation description

### Process Types
Common process types:
- **TEST**: Testing operations (ICT, FCT, Functional Test)
- **REPAIR**: Repair and rework operations
- **ASSEMBLY**: Assembly and integration
- **CALIBRATION**: Calibration operations
- **INSPECTION**: Visual or automated inspection

### Caching
The Process service uses in-memory caching:
- **Default refresh**: 300 seconds (5 minutes)
- **Auto-refresh**: Cache refreshes when age exceeds interval
- **Thread-safe**: Uses locks for concurrent access
- **Performance**: Reduces API calls for frequently accessed data

---

## Process Operations

### Get Operation by Code or Name

```python
# Get by code
ict = api.process.get_operation("ICT")

if ict:
    print(f"Name: {ict.name}")
    print(f"Code: {ict.code}")
    print(f"Type: {ict.process_type}")
    print(f"Description: {ict.description}")

# Get by name
fct = api.process.get_operation("Functional Test")

if fct:
    print(f"Found: {fct.name} ({fct.code})")
```

### Get Test Operations

```python
# Get test operation specifically
test_op = api.process.get_test_operation("ICT")

if test_op:
    print(f"Test Operation: {test_op.name}")
    print(f"Code: {test_op.code}")
else:
    print("Test operation not found")

# Try by name or code
fct = api.process.get_test_operation("FCT")
functional = api.process.get_test_operation("Functional Test")

# Both should return the same operation
if fct and functional:
    assert fct.code == functional.code
    print(f"Found: {fct.name}")
```

### Get Repair Operations

```python
# Get repair operation
repair = api.process.get_repair_operation("Rework")

if repair:
    print(f"Repair Operation: {repair.name}")
    print(f"Code: {repair.code}")
    print(f"Type: {repair.process_type}")

# Common repair operations
repair_codes = ["Rework", "Repair", "Debug"]

for code in repair_codes:
    op = api.process.get_repair_operation(code)
    if op:
        print(f"  {code}: {op.name}")
```

### List All Operations

```python
# Get all operations (via cache)
# Note: This accesses internal cache - implementation may vary

all_operations = api.process.get_all_operations()

print(f"=== ALL OPERATIONS ({len(all_operations)}) ===\n")

# Group by type
by_type = {}
for op in all_operations:
    op_type = op.process_type
    if op_type not in by_type:
        by_type[op_type] = []
    by_type[op_type].append(op)

for op_type, ops in sorted(by_type.items()):
    print(f"{op_type}:")
    for op in ops:
        print(f"  {op.code}: {op.name}")
    print()
```

---

## Cache Management

### Check Cache Status

```python
from datetime import datetime

# Get cache info
last_refresh = api.process.last_refresh
refresh_interval = api.process.refresh_interval

print(f"=== CACHE STATUS ===")
print(f"Last refresh: {last_refresh}")
print(f"Refresh interval: {refresh_interval} seconds ({refresh_interval/60:.1f} minutes)")

# Calculate cache age
if last_refresh:
    age = (datetime.now() - last_refresh).total_seconds()
    print(f"Cache age: {age:.0f} seconds")
    
    if age > refresh_interval:
        print("⚠ Cache is stale and will refresh on next access")
    else:
        remaining = refresh_interval - age
        print(f"✓ Cache is fresh ({remaining:.0f} seconds until refresh)")
else:
    print("Cache not initialized")
```

### Manual Refresh

```python
# Force cache refresh
print("Refreshing process cache...")
api.process.refresh()

print(f"Cache refreshed at: {api.process.last_refresh}")
```

### Configure Refresh Interval

```python
# Set custom refresh interval (in seconds)
# 10 minutes = 600 seconds
api.process.refresh_interval = 600

print(f"Refresh interval set to {api.process.refresh_interval} seconds")

# For frequently changing process definitions, use shorter interval
# 1 minute = 60 seconds
api.process.refresh_interval = 60

# For stable definitions, use longer interval
# 1 hour = 3600 seconds
api.process.refresh_interval = 3600
```

### Auto-Refresh Behavior

```python
import time

# Cache auto-refreshes when age exceeds interval
# Set short interval for demo
api.process.refresh_interval = 5  # 5 seconds

# First access - loads cache
op1 = api.process.get_operation("ICT")
print(f"First access: {api.process.last_refresh}")

# Wait for cache to expire
time.sleep(6)

# Next access - auto-refreshes
op2 = api.process.get_operation("FCT")
print(f"After expiry: {api.process.last_refresh}")

# Reset to default
api.process.refresh_interval = 300
```

---

## Operation Types

### Using Processes in Production

```python
# When creating production records, reference processes

from pywats.domains.production.models import UnitInfo

# Get the test operation
test_op = api.process.get_test_operation("ICT")

# Use in unit creation or update
unit = api.production.get_unit("SN12345")

if unit and test_op:
    # Record that unit went through this process
    # (actual method depends on Production API)
    print(f"Unit {unit.serial_number} processed through {test_op.name}")
```

### Using Processes in Reports

```python
# When creating UUT reports, reference the operation

from pywats.domains.report.models import UUTReport

# Get operation
operation = api.process.get_test_operation("FCT")

# Create report with operation reference
report = UUTReport(
    serial_number="SN12345",
    part_number="WIDGET-001",
    operation_type_code=operation.code,  # Reference operation
    station="FCT-01"
)

# Submit report
api.report.submit_uut_report(report)
```

### Validation Helper

```python
def validate_operation_code(code):
    """Validate that an operation code exists"""
    
    operation = api.process.get_operation(code)
    
    if operation:
        print(f"✓ Valid operation: {operation.name} ({operation.code})")
        return True
    else:
        print(f"✗ Invalid operation code: {code}")
        return False

# Use it
validate_operation_code("ICT")  # Valid
validate_operation_code("INVALID")  # Invalid
```

---

## Advanced Usage

### Operation Lookup Table

```python
def build_operation_lookup():
    """Build quick lookup table for operations"""
    
    # Get all operations
    all_ops = api.process.get_all_operations()
    
    # Build lookup by code
    by_code = {op.code: op for op in all_ops}
    
    # Build lookup by name (lowercase for case-insensitive)
    by_name = {op.name.lower(): op for op in all_ops}
    
    return by_code, by_name

# Use it
code_lookup, name_lookup = build_operation_lookup()

# Fast lookups
ict = code_lookup.get("ICT")
fct = name_lookup.get("functional test")

print(f"ICT: {ict.name if ict else 'Not found'}")
print(f"FCT: {fct.name if fct else 'Not found'}")
```

### Process Type Report

```python
def process_type_report():
    """Generate report of operations by type"""
    
    all_ops = api.process.get_all_operations()
    
    # Group by type
    by_type = {}
    for op in all_ops:
        op_type = op.process_type
        if op_type not in by_type:
            by_type[op_type] = []
        by_type[op_type].append(op)
    
    print("=" * 70)
    print("PROCESS TYPE REPORT")
    print("=" * 70)
    
    for op_type in sorted(by_type.keys()):
        ops = by_type[op_type]
        print(f"\n{op_type} ({len(ops)} operations):")
        
        for op in sorted(ops, key=lambda x: x.code):
            print(f"  {op.code:<10} {op.name}")
    
    print("\n" + "=" * 70)
    print(f"Total: {len(all_ops)} operations")
    print("=" * 70)

# Use it
process_type_report()
```

### Find Operations by Prefix

```python
def find_operations_by_prefix(prefix):
    """Find operations with codes starting with prefix"""
    
    all_ops = api.process.get_all_operations()
    
    matching = [
        op for op in all_ops 
        if op.code.startswith(prefix.upper())
    ]
    
    print(f"=== OPERATIONS STARTING WITH '{prefix}' ({len(matching)}) ===")
    
    for op in matching:
        print(f"{op.code}: {op.name}")
        print(f"  Type: {op.process_type}")

# Use it
find_operations_by_prefix("T")  # All test operations
find_operations_by_prefix("R")  # All repair operations
```

### Operation Usage Tracking

```python
def track_operation_usage(operation_code, days=7):
    """Track how often an operation is used in reports"""
    
    from pywats.domains.report import WATSFilter
    from datetime import datetime, timedelta
    
    # Verify operation exists
    operation = api.process.get_operation(operation_code)
    
    if not operation:
        print(f"Operation '{operation_code}' not found")
        return
    
    # Query reports with this operation
    filter_obj = WATSFilter(
        operation_type_code=operation_code,
        days=days
    )
    
    reports = api.report.get_uut_reports(filter_obj)
    
    print(f"=== USAGE: {operation.name} ({operation.code}) ===")
    print(f"Period: Last {days} days")
    print(f"Reports: {len(reports)}")
    
    # Breakdown by station
    by_station = {}
    for report in reports:
        station = report.station
        by_station[station] = by_station.get(station, 0) + 1
    
    print("\nBy Station:")
    for station, count in sorted(by_station.items()):
        print(f"  {station}: {count}")

# Use it
track_operation_usage("ICT", days=30)
```

### Cached Access Pattern

```python
class ProcessCache:
    """Wrapper for cached process access with fallback"""
    
    def __init__(self, api):
        self.api = api
        self._cache = {}
    
    def get_operation(self, code_or_name):
        """Get operation with local cache layer"""
        
        # Check local cache first
        if code_or_name in self._cache:
            return self._cache[code_or_name]
        
        # Get from API (uses API's cache)
        operation = self.api.process.get_operation(code_or_name)
        
        # Store in local cache
        if operation:
            self._cache[code_or_name] = operation
            self._cache[operation.code] = operation
            self._cache[operation.name] = operation
        
        return operation
    
    def clear_cache(self):
        """Clear local cache"""
        self._cache.clear()

# Use it
cache = ProcessCache(api)

# First access - loads from API
op1 = cache.get_operation("ICT")

# Second access - uses local cache
op2 = cache.get_operation("ICT")

# Clear when needed
cache.clear_cache()
```

---

## API Reference

### ProcessService Methods

#### Operation Queries
- `get_operation(code_or_name)` → `Optional[ProcessInfo]` - Get operation by code or name
- `get_test_operation(code_or_name)` → `Optional[ProcessInfo]` - Get test operation
- `get_repair_operation(code_or_name)` → `Optional[ProcessInfo]` - Get repair operation
- `get_all_operations()` → `List[ProcessInfo]` - Get all operations (from cache)

#### Cache Management
- `refresh()` → `None` - Force cache refresh
- `refresh_interval` → `int` - Get/set refresh interval in seconds
- `last_refresh` → `datetime` - Get last refresh timestamp

### Models

#### ProcessInfo
- `id`: int - Process ID
- `name`: str - Operation name
- `code`: str - Short code
- `process_type`: str - Type (TEST, REPAIR, etc.)
- `description`: str - Operation description

### Cache Behavior

- **Default Refresh**: 300 seconds (5 minutes)
- **Auto-Refresh**: When cache age exceeds refresh_interval
- **Thread-Safe**: Uses threading.Lock for concurrent access
- **Read-Only**: Process definitions are read-only via API

---

## Best Practices

1. **Use the cache** - Don't bypass caching for frequent lookups
2. **Set appropriate interval** - Balance freshness vs performance
3. **Lookup by code** - Codes are more stable than names
4. **Validate codes** - Check operation exists before using
5. **Refresh on startup** - Ensure cache is fresh when application starts
6. **Monitor cache age** - Track when last refresh occurred
7. **Use in reports** - Reference operation codes in test reports
8. **Handle missing operations** - Gracefully handle unknown codes

---

## See Also

- [Report Domain](REPORT.md) - Use operation codes in test reports
- [Production Domain](PRODUCTION.md) - Track operations performed on units
- [Analytics Domain](ANALYTICS.md) - Analyze data by operation type
