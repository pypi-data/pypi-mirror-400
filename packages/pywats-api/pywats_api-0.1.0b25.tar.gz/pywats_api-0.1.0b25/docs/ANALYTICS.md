# Analytics Domain

The Analytics domain provides data analysis and visualization capabilities for test results. It includes yield calculations, measurement aggregation, Cpk analysis, and production flow visualization (Unit Flow). Use this domain to understand manufacturing performance, identify trends, and optimize processes.

## Table of Contents

- [Quick Start](#quick-start)
- [Core Concepts](#core-concepts)
- [Yield Analysis](#yield-analysis)
- [Measurement Aggregation](#measurement-aggregation)
- [Unit Flow Analysis](#unit-flow-analysis-internal)
- [Advanced Usage](#advanced-usage)
- [API Reference](#api-reference)

---

## Quick Start

```python
from pywats import pyWATS
from pywats.domains.report import WATSFilter
from datetime import datetime, timedelta

# Initialize
api = pyWATS(
    base_url="https://your-wats-server.com",
    token="your-api-token"
)

# Get yield for last 7 days
filter_obj = WATSFilter(
    part_number="WIDGET-001",
    days=7
)

yield_result = api.analytics.get_yield(filter_obj)
print(f"Yield: {yield_result.yield_pct:.1f}%")
print(f"Passed: {yield_result.passed}")
print(f"Failed: {yield_result.failed}")
print(f"Total: {yield_result.total}")

# Get measurements for a step
measurements = api.analytics.get_aggregated_measurements(
    filter_obj,
    measurement_paths="Numeric Limit Tests>>3.3V Rail"
)

for meas in measurements:
    print(f"{meas.step_name}:")
    print(f"  Avg: {meas.avg:.3f}")
    print(f"  Cpk: {meas.cpk:.2f}")
```

---

## Core Concepts

### Yield
**Yield** is the percentage of units that passed testing:
- `yield_pct`: Percentage (0-100)
- `passed`: Number of passed units
- `failed`: Number of failed units
- `total`: Total units tested

### Measurements
**Aggregated measurements** provide statistical analysis of numeric test steps:
- `avg`: Average value
- `min`, `max`: Minimum and maximum
- `std_dev`: Standard deviation
- `cpk`: Process capability index
- `count`: Number of measurements

### Unit Flow
**Unit Flow** visualizes how units move through production:
- **Nodes**: Operations/processes (e.g., "ICT", "FCT", "Assembly")
- **Links**: Transitions between operations
- **Units**: Individual units tracked through the flow

---

## Yield Analysis

### Get Overall Yield

```python
from pywats.domains.report import WATSFilter

# Yield for last 30 days
filter_obj = WATSFilter(
    part_number="WIDGET-001",
    days=30
)

yield_result = api.analytics.get_yield(filter_obj)

print(f"=== YIELD ANALYSIS ===")
print(f"Yield: {yield_result.yield_pct:.2f}%")
print(f"Passed: {yield_result.passed}")
print(f"Failed: {yield_result.failed}")
print(f"Total: {yield_result.total}")
```

### Yield by Date Range

```python
from datetime import datetime, timedelta

# Last quarter
end_date = datetime.now()
start_date = end_date - timedelta(days=90)

filter_obj = WATSFilter(
    part_number="WIDGET-001",
    start_date_time=start_date,
    end_date_time=end_date
)

yield_result = api.analytics.get_yield(filter_obj)
print(f"Q1 Yield: {yield_result.yield_pct:.1f}%")
```

### Yield by Station

```python
# Compare yield across stations
stations = ["ICT-01", "ICT-02", "ICT-03"]

print("=== YIELD BY STATION ===")
for station in stations:
    filter_obj = WATSFilter(
        part_number="WIDGET-001",
        station=station,
        days=7
    )
    
    yield_result = api.analytics.get_yield(filter_obj)
    print(f"{station}: {yield_result.yield_pct:.1f}% ({yield_result.total} units)")
```

### Yield Trend Over Time

```python
from datetime import datetime, timedelta

def get_daily_yield(part_number, days=30):
    """Get yield for each of the last N days"""
    
    trends = []
    end_date = datetime.now()
    
    for i in range(days):
        day_end = end_date - timedelta(days=i)
        day_start = day_end - timedelta(days=1)
        
        filter_obj = WATSFilter(
            part_number=part_number,
            start_date_time=day_start,
            end_date_time=day_end
        )
        
        yield_result = api.analytics.get_yield(filter_obj)
        
        trends.append({
            'date': day_start.date(),
            'yield': yield_result.yield_pct,
            'total': yield_result.total
        })
    
    return trends

# Use it
trends = get_daily_yield("WIDGET-001", days=14)

print("=== 14-DAY YIELD TREND ===")
for trend in reversed(trends):
    yield_bar = "█" * int(trend['yield'] / 5)  # Visual bar
    print(f"{trend['date']}: {trend['yield']:.1f}% {yield_bar} ({trend['total']} units)")
```

---

## Measurement Aggregation

### Get Measurement Statistics

```python
from pywats.domains.report import WATSFilter

# Get measurements for a specific test step
filter_obj = WATSFilter(
    part_number="WIDGET-001",
    days=7
)

measurements = api.analytics.get_aggregated_measurements(
    filter_obj,
    measurement_paths="Power Supply Tests>>3.3V Rail"
)

if measurements:
    meas = measurements[0]
    print(f"Step: {meas.step_name}")
    print(f"Count: {meas.count}")
    print(f"Average: {meas.avg:.3f}")
    print(f"Min: {meas.min:.3f}")
    print(f"Max: {meas.max:.3f}")
    print(f"Std Dev: {meas.std_dev:.3f}")
    print(f"Cpk: {meas.cpk:.2f}")
```

### Multiple Measurements

```python
# Get multiple measurements at once
step_paths = [
    "Power Supply Tests>>3.3V Rail",
    "Power Supply Tests>>5V Rail",
    "Power Supply Tests>>12V Rail"
]

measurements = api.analytics.get_aggregated_measurements(
    filter_obj,
    measurement_paths=step_paths
)

print("=== POWER RAIL MEASUREMENTS ===")
for meas in measurements:
    print(f"\n{meas.step_name}:")
    print(f"  Avg: {meas.avg:.3f} (σ={meas.std_dev:.3f})")
    print(f"  Range: {meas.min:.3f} to {meas.max:.3f}")
    print(f"  Cpk: {meas.cpk:.2f}")
```

### Cpk Analysis

```python
def analyze_process_capability(part_number, step_path, days=30):
    """Analyze process capability (Cpk) for a measurement"""
    
    filter_obj = WATSFilter(
        part_number=part_number,
        days=days
    )
    
    measurements = api.analytics.get_aggregated_measurements(
        filter_obj,
        measurement_paths=step_path
    )
    
    if not measurements:
        print("No measurements found")
        return
    
    meas = measurements[0]
    
    print(f"\n=== PROCESS CAPABILITY: {meas.step_name} ===")
    print(f"Cpk: {meas.cpk:.2f}")
    
    if meas.cpk >= 1.33:
        print("✓ Process is capable (Cpk ≥ 1.33)")
    elif meas.cpk >= 1.0:
        print("⚠ Process is marginally capable (1.0 ≤ Cpk < 1.33)")
    else:
        print("✗ Process is not capable (Cpk < 1.0)")
    
    print(f"\nStatistics:")
    print(f"  Mean: {meas.avg:.3f}")
    print(f"  Std Dev: {meas.std_dev:.3f}")
    print(f"  Range: {meas.min:.3f} to {meas.max:.3f}")
    print(f"  Samples: {meas.count}")

# Use it
analyze_process_capability("WIDGET-001", "3.3V Rail", days=90)
```

---

## Unit Flow Analysis (Internal)

⚠️ **INTERNAL API - Subject to change**

Unit Flow visualizes production flow and identifies bottlenecks.

### Basic Unit Flow Query

```python
from pywats.domains.analytics import UnitFlowFilter
from datetime import datetime, timedelta

# Create filter
flow_filter = UnitFlowFilter(
    part_number="WIDGET-001",
    date_from=datetime.now() - timedelta(days=7),
    date_to=datetime.now()
)

# Get flow data
flow = api.analytics_internal.get_unit_flow(flow_filter)

print(f"=== UNIT FLOW ===")
print(f"Nodes: {len(flow.nodes)}")
print(f"Links: {len(flow.links)}")
print(f"Units: {len(flow.units)}")

# Show nodes (operations)
print("\nOperations:")
for node in flow.nodes:
    print(f"  {node.name}: {node.unit_count} units")

# Show transitions
print("\nTransitions:")
for link in flow.links:
    print(f"  {link.source_name} → {link.target_name}: {link.unit_count} units")
```

### Identify Bottlenecks

```python
# Get bottlenecks (nodes with high unit count)
flow_filter = UnitFlowFilter(
    part_number="WIDGET-001",
    days=7
)

bottlenecks = api.analytics_internal.get_bottlenecks(flow_filter)

print("=== BOTTLENECKS ===")
for bottleneck in bottlenecks:
    print(f"{bottleneck.operation_name}:")
    print(f"  Units waiting: {bottleneck.unit_count}")
    print(f"  Avg time: {bottleneck.avg_time_hours:.1f} hours")
```

### Trace Serial Numbers Through Flow

```python
# Trace specific units
flow_filter = UnitFlowFilter(
    part_number="WIDGET-001",
    serial_numbers=["W12345", "W12346", "W12347"],
    days=30
)

trace_result = api.analytics_internal.trace_serial_numbers(flow_filter)

for unit in trace_result.units:
    print(f"\n{unit.serial_number}:")
    print(f"  Status: {unit.status}")
    print(f"  Path: {' → '.join(unit.node_path)}")
    print(f"  Total time: {unit.total_time_hours:.1f} hours")
```

---

## Advanced Usage

### Yield Dashboard

```python
def yield_dashboard(part_numbers, days=7):
    """Generate yield dashboard for multiple products"""
    from pywats.domains.report import WATSFilter
    
    print("=" * 70)
    print(f"YIELD DASHBOARD ({days} days)")
    print("=" * 70)
    
    results = []
    
    for pn in part_numbers:
        filter_obj = WATSFilter(part_number=pn, days=days)
        yield_result = api.analytics.get_yield(filter_obj)
        
        results.append({
            'part': pn,
            'yield': yield_result.yield_pct,
            'passed': yield_result.passed,
            'failed': yield_result.failed,
            'total': yield_result.total
        })
    
    # Sort by yield (ascending)
    results.sort(key=lambda x: x['yield'])
    
    print(f"\n{'Part Number':<20} {'Yield':>8} {'Passed':>8} {'Failed':>8} {'Total':>8}")
    print("-" * 70)
    
    for r in results:
        status = "✓" if r['yield'] >= 95 else "⚠" if r['yield'] >= 85 else "✗"
        print(f"{r['part']:<20} {r['yield']:>7.1f}% {r['passed']:>8} {r['failed']:>8} {r['total']:>8} {status}")
    
    # Summary
    avg_yield = sum(r['yield'] for r in results) / len(results)
    total_units = sum(r['total'] for r in results)
    
    print("-" * 70)
    print(f"{'AVERAGE':<20} {avg_yield:>7.1f}% {'':>8} {'':>8} {total_units:>8}")
    print("=" * 70)

# Use it
products = ["WIDGET-001", "WIDGET-002", "WIDGET-003", "GADGET-001"]
yield_dashboard(products, days=30)
```

### Measurement Report

```python
def measurement_report(part_number, step_paths, days=7):
    """Generate measurement report for multiple steps"""
    from pywats.domains.report import WATSFilter
    
    filter_obj = WATSFilter(part_number=part_number, days=days)
    
    measurements = api.analytics.get_aggregated_measurements(
        filter_obj,
        measurement_paths=step_paths
    )
    
    print(f"\n=== MEASUREMENT REPORT: {part_number} ({days} days) ===\n")
    print(f"{'Step':<40} {'Avg':>10} {'Std Dev':>10} {'Cpk':>8} {'Count':>8}")
    print("-" * 80)
    
    for meas in measurements:
        cpk_status = "✓" if meas.cpk >= 1.33 else "⚠" if meas.cpk >= 1.0 else "✗"
        print(f"{meas.step_name:<40} {meas.avg:>10.3f} {meas.std_dev:>10.3f} {meas.cpk:>7.2f} {meas.count:>8} {cpk_status}")
    
    print("=" * 80)

# Use it
steps = [
    "Power Supply Tests>>3.3V Rail",
    "Power Supply Tests>>5V Rail",
    "Power Supply Tests>>12V Rail",
    "Temperature Tests>>Idle Temp",
    "Temperature Tests>>Load Temp"
]

measurement_report("WIDGET-001", steps, days=30)
```

---

## API Reference

### AnalyticsService Methods

#### Yield Operations
- `get_yield(filter)` → `YieldResult` - Calculate yield statistics

#### Measurement Operations
- `get_aggregated_measurements(filter, measurement_paths)` → `List[AggregatedMeasurement]` - Get measurement statistics

### AnalyticsServiceInternal Methods (⚠️ Subject to change)

#### Unit Flow Operations
- `get_unit_flow(filter)` → `UnitFlowResult` - Get complete flow data
- `get_bottlenecks(filter)` → `List[Bottleneck]` - Identify bottlenecks
- `trace_serial_numbers(filter)` → `UnitFlowResult` - Trace specific units

### Models

#### YieldResult
- `yield_pct`: float (percentage)
- `passed`: int
- `failed`: int
- `total`: int

#### AggregatedMeasurement
- `step_name`: str
- `count`: int
- `avg`: float
- `min`, `max`: float
- `std_dev`: float
- `cpk`: float (process capability index)

#### UnitFlowFilter
- `part_number`: str
- `date_from`, `date_to`: datetime
- `days`: int (shortcut for last N days)
- `serial_numbers`: List[str] (optional filter)

---

## Best Practices

1. **Use appropriate time windows** - Balance detail with performance
2. **Filter by relevant criteria** - Part number, station, date range
3. **Monitor Cpk trends** - Watch for process degradation
4. **Track yield daily** - Catch issues early
5. **Compare stations** - Identify equipment issues
6. **Investigate anomalies** - Low Cpk or sudden yield drops
7. **Use Unit Flow for bottlenecks** - Visualize production flow

---

## See Also

- [Report Domain](REPORT.md) - Test reports and measurements
- [Production Domain](PRODUCTION.md) - Unit lifecycle and status
- [Process Domain](PROCESS.md) - Operation type definitions
