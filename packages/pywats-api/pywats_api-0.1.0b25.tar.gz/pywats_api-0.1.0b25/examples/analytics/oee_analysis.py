"""
Analytics Domain: OEE Analysis

This example demonstrates Overall Equipment Effectiveness (OEE) analysis.
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
# Get OEE Analysis
# =============================================================================

# OEE = Availability × Performance × Quality

filter_data = WATSFilter(
    dateStart=datetime.now() - timedelta(days=7),
    dateStop=datetime.now()
)

oee_data = api.analytics.get_oee_analysis(filter_data)

if oee_data:
    print("OEE Analysis (last 7 days):")
    print(f"  Availability: {oee_data.availability:.1f}%")
    print(f"  Performance: {oee_data.performance:.1f}%")
    print(f"  Quality: {oee_data.quality:.1f}%")
    print(f"  OEE: {oee_data.oee:.1f}%")
    
    # World-class benchmark
    if oee_data.oee >= 85:
        print("  ✓ World-class OEE (≥85%)")
    elif oee_data.oee >= 60:
        print("  ⚠️ Typical OEE (60-85%)")
    else:
        print("  ✗ OEE needs improvement (<60%)")


# =============================================================================
# OEE Breakdown Analysis
# =============================================================================

def oee_breakdown():
    """Detailed OEE component breakdown."""
    filter_data = WATSFilter(
        dateStart=datetime.now() - timedelta(days=7),
        dateStop=datetime.now()
    )
    
    data = api.analytics.get_oee_analysis(filter_data)
    
    if not data:
        print("No OEE data available")
        return
    
    print("\nOEE Breakdown Analysis")
    print("=" * 50)
    
    print(f"\n  Overall OEE: {data.oee:.1f}%")
    print()
    
    # Component analysis
    components = [
        ("Availability", data.availability, "Downtime losses"),
        ("Performance", data.performance, "Speed losses"),
        ("Quality", data.quality, "Quality losses"),
    ]
    
    min_component = min(components, key=lambda x: x[1] if x[1] is not None else 100)
    
    for name, value, loss_type in components:
        if value is not None:
            bar_len = int(value / 2.5)
            bar = "█" * bar_len
            indicator = " ← Focus area" if name == min_component[0] else ""
            print(f"  {name:12}: {value:5.1f}% {bar}{indicator}")
            print(f"               ({loss_type})")
    
    print("\nRecommendations:")
    if min_component[0] == "Availability":
        print("  - Reduce unplanned downtime")
        print("  - Improve changeover times")
        print("  - Implement preventive maintenance")
    elif min_component[0] == "Performance":
        print("  - Reduce minor stops")
        print("  - Optimize cycle times")
        print("  - Address speed losses")
    else:
        print("  - Reduce first-pass failures")
        print("  - Improve process stability")
        print("  - Address quality variations")


# oee_breakdown()


# =============================================================================
# OEE Trend
# =============================================================================

def oee_trend(days: int = 14):
    """Track OEE trend over time."""
    print(f"\nOEE Trend (last {days} days):")
    print("=" * 50)
    
    for days_ago in range(days, -1, -1):
        date = datetime.now() - timedelta(days=days_ago)
        date_start = datetime(date.year, date.month, date.day)
        date_end = date_start + timedelta(days=1)
        
        filter_data = WATSFilter(
            dateStart=date_start,
            dateStop=date_end
        )
        
        data = api.analytics.get_oee_analysis(filter_data)
        
        if data and data.oee is not None:
            bar_len = int(data.oee / 2.5)
            bar = "█" * bar_len
            print(f"  {date_start.strftime('%m-%d')}: {data.oee:5.1f}% {bar}")


# oee_trend()


# =============================================================================
# Six Big Losses Reference
# =============================================================================

def six_big_losses_info():
    """Information about the Six Big Losses affecting OEE."""
    print("\nSix Big Losses Analysis")
    print("=" * 50)
    
    print("""
    AVAILABILITY LOSSES:
    1. Equipment Breakdowns
       - Track unplanned downtime events
       - Monitor MTBF (Mean Time Between Failures)
    
    2. Setup and Adjustments
       - Monitor changeover times
       - Track calibration events
    
    PERFORMANCE LOSSES:
    3. Idling and Minor Stops
       - Track short stops (<5 min)
       - Monitor operator wait times
    
    4. Reduced Speed
       - Compare actual vs. ideal cycle time
       - Monitor throughput rates
    
    QUALITY LOSSES:
    5. Process Defects
       - Track first-pass yield
       - Monitor scrap/rework rates
    
    6. Reduced Yield (Startup)
       - Track yield after changeovers
       - Monitor warmup period quality
    """)


# six_big_losses_info()
