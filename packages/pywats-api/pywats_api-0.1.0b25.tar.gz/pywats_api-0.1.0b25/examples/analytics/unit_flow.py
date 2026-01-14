"""
Analytics Domain: Unit Flow Analysis

⚠️ INTERNAL API - SUBJECT TO CHANGE ⚠️

This example demonstrates Unit Flow analysis for production flow visualization.
Unit Flow helps you understand how units move through your production processes
and identify bottlenecks.

Features demonstrated:
- Query unit flow with filters
- Get flow nodes (operations/processes)
- Get flow links (transitions between nodes)
- Trace specific serial numbers
- Split flow by dimension
- Find bottlenecks
- Get flow summary statistics
"""
import os
from datetime import datetime, timedelta
from pywats import pyWATS
from pywats.domains.analytics import UnitFlowFilter

# =============================================================================
# Setup
# =============================================================================

api = pyWATS(
    base_url=os.environ.get("WATS_BASE_URL", "https://demo.wats.com"),
    token=os.environ.get("WATS_TOKEN", "")
)


# =============================================================================
# Basic Unit Flow Query
# =============================================================================

print("=" * 60)
print("UNIT FLOW ANALYSIS")
print("=" * 60)

# Get unit flow for a product in the last 7 days
filter_data = UnitFlowFilter(
    part_number="WIDGET-001",
    date_from=datetime.now() - timedelta(days=7),
    date_to=datetime.now(),
    include_passed=True,
    include_failed=True
)

result = api.analytics_internal.get_unit_flow(filter_data)

print(f"\nUnit Flow Results:")
print(f"  Total nodes: {len(result.nodes or [])}")
print(f"  Total links: {len(result.links or [])}")
if result.total_units:
    print(f"  Total units: {result.total_units}")

# Display nodes (operations)
print("\nFlow Nodes (Operations):")
for node in result.nodes or []:
    yield_pct = f"{node.yield_percent:.1f}%" if node.yield_percent is not None else "N/A"
    print(f"  - {node.name}: {node.unit_count or 0} units, {yield_pct} yield")

# Display links (transitions)
print("\nFlow Links (Transitions):")
for link in result.links or []:
    print(f"  - {link.source_name} -> {link.target_name}: {link.unit_count or 0} units")


# =============================================================================
# Find Bottlenecks
# =============================================================================

print("\n" + "=" * 60)
print("BOTTLENECK ANALYSIS")
print("=" * 60)

# Find operations with yield below 95%
bottlenecks = api.analytics_internal.get_bottlenecks(
    filter_data=filter_data,
    min_yield_threshold=95.0
)

if bottlenecks:
    print("\n⚠️ Potential Bottlenecks (yield < 95%):")
    for node in bottlenecks:
        print(f"  - {node.name}: {node.yield_percent:.1f}% yield")
        if node.fail_count:
            print(f"    Failures: {node.fail_count}")
else:
    print("\n✅ No bottlenecks found (all operations >= 95% yield)")


# =============================================================================
# Flow Summary Statistics
# =============================================================================

print("\n" + "=" * 60)
print("FLOW SUMMARY")
print("=" * 60)

summary = api.analytics_internal.get_flow_summary(filter_data)

print(f"\nFlow Statistics:")
print(f"  Total nodes: {summary['total_nodes']}")
print(f"  Total links: {summary['total_links']}")
print(f"  Total units: {summary['total_units']}")
print(f"  Passed units: {summary['passed_units']}")
print(f"  Failed units: {summary['failed_units']}")
print(f"  Average yield: {summary['avg_yield']:.1f}%")
print(f"  Min yield: {summary['min_yield']:.1f}%")
print(f"  Max yield: {summary['max_yield']:.1f}%")


# =============================================================================
# Trace Specific Serial Numbers
# =============================================================================

print("\n" + "=" * 60)
print("SERIAL NUMBER TRACING")
print("=" * 60)

# Trace specific units through the flow
serial_numbers = ["SN001", "SN002", "SN003"]
print(f"\nTracing serial numbers: {serial_numbers}")

trace_result = api.analytics_internal.trace_serial_numbers(serial_numbers)

print(f"  Found {len(trace_result.nodes or [])} nodes in trace")
print(f"  Found {len(trace_result.links or [])} links in trace")

if trace_result.units:
    print("\nUnit Details:")
    for unit in trace_result.units:
        print(f"  - {unit.serial_number}: {unit.status}")
        if unit.node_path:
            print(f"    Path: {' -> '.join(unit.node_path)}")


# =============================================================================
# Split Flow by Dimension
# =============================================================================

print("\n" + "=" * 60)
print("SPLIT FLOW BY STATION")
print("=" * 60)

# Split the flow by station name
split_result = api.analytics_internal.split_flow_by("stationName", filter_data)

print(f"\nFlow split by station:")
for node in split_result.nodes or []:
    station = node.station_name or "Unknown"
    print(f"  - {station} / {node.name}: {node.unit_count or 0} units")


# =============================================================================
# Expand/Collapse Operations
# =============================================================================

print("\n" + "=" * 60)
print("EXPAND OPERATIONS")
print("=" * 60)

# Expand to see detailed sub-operations
expanded_result = api.analytics_internal.expand_operations(True, filter_data)

print(f"\nExpanded view: {len(expanded_result.nodes or [])} nodes")
for node in expanded_result.nodes or []:
    level_indent = "  " * (node.level or 0)
    print(f"  {level_indent}- {node.name}")


# =============================================================================
# Show/Hide Operations
# =============================================================================

print("\n" + "=" * 60)
print("FILTER OPERATIONS")
print("=" * 60)

# Hide packaging operations
hidden_result = api.analytics_internal.hide_operations(
    ["Packaging", "Labeling"],
    filter_data
)

print(f"\nWith Packaging/Labeling hidden: {len(hidden_result.nodes or [])} nodes")

# Show only specific operations
shown_result = api.analytics_internal.show_operations(
    ["Assembly", "EndOfLineTest", "FunctionalTest"],
    filter_data
)

print(f"With only test operations shown: {len(shown_result.nodes or [])} nodes")


# =============================================================================
# Get Raw Nodes and Links
# =============================================================================

print("\n" + "=" * 60)
print("RAW FLOW DATA")
print("=" * 60)

# Get nodes directly
nodes = api.analytics_internal.get_flow_nodes()
print(f"\nAll flow nodes: {len(nodes)}")

# Get links directly
links = api.analytics_internal.get_flow_links()
print(f"All flow links: {len(links)}")

# Get units directly
units = api.analytics_internal.get_flow_units()
print(f"All flow units: {len(units)}")


print("\n" + "=" * 60)
print("UNIT FLOW ANALYSIS COMPLETE")
print("=" * 60)
