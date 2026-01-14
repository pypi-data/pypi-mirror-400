"""
Analytics Domain: Yield Analysis

This example demonstrates yield and statistical analysis.
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
# Get Dynamic Yield
# =============================================================================

# Yield over time (last 30 days)
filter_data = WATSFilter(
    dateStart=datetime.now() - timedelta(days=30),
    dateStop=datetime.now()
)

yield_data = api.analytics.get_dynamic_yield(filter_data)

print("Dynamic Yield (last 30 days):")
for point in yield_data[:10]:  # First 10 points
    print(f"  {point.date}: {point.yield_pct:.1f}% ({point.passed}/{point.total})")


# =============================================================================
# Yield for Specific Product
# =============================================================================

filter_data = WATSFilter(
    partNumber="WIDGET-001",
    dateStart=datetime.now() - timedelta(days=30),
    dateStop=datetime.now()
)

yield_data = api.analytics.get_dynamic_yield(filter_data)

# Calculate overall yield
if yield_data:
    total_passed = sum(d.passed for d in yield_data)
    total_tested = sum(d.total for d in yield_data)
    overall_yield = (total_passed / total_tested * 100) if total_tested > 0 else 0
    
    print(f"\nWIDGET-001 Yield Summary:")
    print(f"  Overall yield: {overall_yield:.1f}%")
    print(f"  Total tested: {total_tested}")
    print(f"  Total passed: {total_passed}")


# =============================================================================
# Volume and Yield by Product
# =============================================================================

filter_data = WATSFilter(
    dateStart=datetime.now() - timedelta(days=7),
    dateStop=datetime.now()
)

volume_data = api.analytics.get_volume_yield(filter_data)

print("\nVolume & Yield by Product (last 7 days):")
for item in volume_data[:10]:
    print(f"  {item.partNumber}: {item.total} units, {item.yield_pct:.1f}% yield")


# =============================================================================
# Worst Yield Products
# =============================================================================

filter_data = WATSFilter(
    dateStart=datetime.now() - timedelta(days=7),
    dateStop=datetime.now()
)

worst = api.analytics.get_worst_yield(filter_data, limit=10)

print("\nWorst Yield Products (top 10):")
for i, item in enumerate(worst, 1):
    print(f"  {i}. {item.partNumber}: {item.yield_pct:.1f}% ({item.failed} failures)")


# =============================================================================
# Highest Volume Products
# =============================================================================

high_volume = api.analytics.get_high_volume(filter_data, limit=10)

print("\nHighest Volume Products (top 10):")
for i, item in enumerate(high_volume, 1):
    print(f"  {i}. {item.partNumber}: {item.total} units")


# =============================================================================
# Yield Dashboard
# =============================================================================

def print_yield_dashboard():
    """Print a yield dashboard summary."""
    now = datetime.now()
    today = datetime(now.year, now.month, now.day)
    week_ago = today - timedelta(days=7)
    
    print("\n" + "=" * 50)
    print("YIELD DASHBOARD")
    print(f"Generated: {now}")
    print("=" * 50)
    
    # Today's yield
    today_filter = WATSFilter(dateStart=today, dateStop=now)
    today_data = api.analytics.get_volume_yield(today_filter)
    
    if today_data:
        total = sum(d.total for d in today_data)
        passed = sum(d.passed for d in today_data)
        yield_pct = (passed / total * 100) if total > 0 else 0
        print(f"\nToday:")
        print(f"  Tested: {total}")
        print(f"  Yield: {yield_pct:.1f}%")
    
    # This week
    week_filter = WATSFilter(dateStart=week_ago, dateStop=now)
    week_data = api.analytics.get_volume_yield(week_filter)
    
    if week_data:
        total = sum(d.total for d in week_data)
        passed = sum(d.passed for d in week_data)
        yield_pct = (passed / total * 100) if total > 0 else 0
        print(f"\nThis Week:")
        print(f"  Tested: {total}")
        print(f"  Yield: {yield_pct:.1f}%")
    
    # Problem products
    print(f"\nProblem Products (< 95% yield):")
    worst = api.analytics.get_worst_yield(week_filter, limit=5)
    for item in worst:
        if item.yield_pct < 95:
            print(f"  ⚠️ {item.partNumber}: {item.yield_pct:.1f}%")
    
    print("=" * 50)


# print_yield_dashboard()
