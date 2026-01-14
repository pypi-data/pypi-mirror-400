"""
Analytics Domain: Measurement Data

This example demonstrates measurement data retrieval and analysis.
"""
import os
from datetime import datetime, timedelta
from pywats import pyWATS
from pywats.domains.report import WATSFilter

# =============================================================================
# Setup
# =============================================================================

api = pyWATS(
    base_url=os.environ.get("WATS_BASE_URL", "https://demo.wats.com"),
    token=os.environ.get("WATS_TOKEN", "")
)


# =============================================================================
# Get Raw Measurements
# =============================================================================

filter_data = WATSFilter(
    partNumber="WIDGET-001",
    dateStart=datetime.now() - timedelta(days=7),
    dateStop=datetime.now()
)

measurements = api.analytics.get_measurements(
    filter_data,
    step_name="Voltage Check",
    limit=100
)

print(f"Measurements for 'Voltage Check' (last 7 days):")
if measurements:
    print(f"  Total: {len(measurements)} readings")
    
    # Calculate statistics
    values = [m.value for m in measurements if m.value is not None]
    if values:
        avg = sum(values) / len(values)
        min_val = min(values)
        max_val = max(values)
        print(f"  Min: {min_val:.4f}")
        print(f"  Max: {max_val:.4f}")
        print(f"  Avg: {avg:.4f}")
    
    # Show recent values
    print("\n  Recent values:")
    for m in measurements[:5]:
        print(f"    {m.timestamp}: {m.value} {m.units or ''}")


# =============================================================================
# Get Aggregated Measurements
# =============================================================================

# More efficient when only statistics are needed
filter_data = WATSFilter(
    partNumber="WIDGET-001",
    dateStart=datetime.now() - timedelta(days=30),
    dateStop=datetime.now()
)

agg_data = api.analytics.get_aggregated_measurements(
    filter_data,
    step_name="Voltage Check"
)

if agg_data:
    print(f"\nAggregated stats for 'Voltage Check':")
    print(f"  Count: {agg_data.count}")
    print(f"  Mean: {agg_data.mean:.4f}")
    print(f"  Std Dev: {agg_data.stdDev:.4f}")
    print(f"  Min: {agg_data.min:.4f}")
    print(f"  Max: {agg_data.max:.4f}")
    if agg_data.lowLimit is not None:
        print(f"  Low Limit: {agg_data.lowLimit}")
    if agg_data.highLimit is not None:
        print(f"  High Limit: {agg_data.highLimit}")
    if agg_data.cp is not None:
        print(f"  Cp: {agg_data.cp:.2f}")
    if agg_data.cpk is not None:
        print(f"  Cpk: {agg_data.cpk:.2f}")


# =============================================================================
# Process Capability Analysis
# =============================================================================

def process_capability(part_number: str, step_name: str):
    """Analyze process capability (Cp/Cpk)."""
    filter_data = WATSFilter(
        partNumber=part_number,
        dateStart=datetime.now() - timedelta(days=30),
        dateStop=datetime.now()
    )
    
    data = api.analytics.get_aggregated_measurements(filter_data, step_name=step_name)
    
    if not data:
        print("No data available")
        return
    
    print(f"\nProcess Capability: {step_name}")
    print("=" * 50)
    
    print(f"\nProcess Statistics:")
    print(f"  Sample size: {data.count}")
    print(f"  Mean (μ): {data.mean:.4f}")
    print(f"  Std Dev (σ): {data.stdDev:.4f}")
    
    if data.lowLimit is not None and data.highLimit is not None:
        print(f"\nSpecification Limits:")
        print(f"  LSL: {data.lowLimit}")
        print(f"  USL: {data.highLimit}")
        
        if data.cpk is not None:
            print(f"\nCapability Indices:")
            print(f"  Cp: {data.cp:.2f}")
            print(f"  Cpk: {data.cpk:.2f}")
            
            # Interpretation
            if data.cpk >= 1.33:
                print("  ✓ Process is capable (Cpk ≥ 1.33)")
            elif data.cpk >= 1.0:
                print("  ⚠️ Process is marginally capable (1.0 ≤ Cpk < 1.33)")
            else:
                print("  ✗ Process is not capable (Cpk < 1.0)")


# process_capability("WIDGET-001", "Voltage Check")


# =============================================================================
# Measurement Trend
# =============================================================================

def measurement_trend(part_number: str, step_name: str, days: int = 14):
    """Track measurement trend over time."""
    print(f"\nMeasurement Trend: {step_name}")
    print("=" * 50)
    
    for days_ago in range(days, -1, -1):
        date = datetime.now() - timedelta(days=days_ago)
        date_start = datetime(date.year, date.month, date.day)
        date_end = date_start + timedelta(days=1)
        
        filter_data = WATSFilter(
            partNumber=part_number,
            dateStart=date_start,
            dateStop=date_end
        )
        
        data = api.analytics.get_aggregated_measurements(filter_data, step_name=step_name)
        
        if data and data.count > 0:
            print(f"  {date_start.strftime('%m-%d')}: mean={data.mean:7.3f} n={data.count:4}")


# measurement_trend("WIDGET-001", "Voltage Check")


# =============================================================================
# Histogram Analysis
# =============================================================================

def histogram_analysis(part_number: str, step_name: str, bins: int = 10):
    """Create histogram distribution of measurements."""
    filter_data = WATSFilter(
        partNumber=part_number,
        dateStart=datetime.now() - timedelta(days=30),
        dateStop=datetime.now()
    )
    
    data = api.analytics.get_measurements(filter_data, step_name=step_name, limit=1000)
    
    if not data:
        print("No data available")
        return
    
    values = [m.value for m in data if m.value is not None]
    
    if not values:
        print("No valid values")
        return
    
    min_val = min(values)
    max_val = max(values)
    bin_width = (max_val - min_val) / bins if max_val > min_val else 1
    
    histogram = [0] * bins
    for v in values:
        bin_idx = min(int((v - min_val) / bin_width), bins - 1)
        histogram[bin_idx] += 1
    
    print(f"\nHistogram: {step_name}")
    print(f"Range: {min_val:.3f} to {max_val:.3f}")
    print(f"Samples: {len(values)}")
    print()
    
    max_count = max(histogram)
    for i, count in enumerate(histogram):
        bin_start = min_val + i * bin_width
        bin_end = bin_start + bin_width
        bar_len = int(count / max_count * 40) if max_count > 0 else 0
        bar = "█" * bar_len
        print(f"  {bin_start:7.3f}-{bin_end:7.3f} | {count:4} | {bar}")


# histogram_analysis("WIDGET-001", "Voltage Check")
