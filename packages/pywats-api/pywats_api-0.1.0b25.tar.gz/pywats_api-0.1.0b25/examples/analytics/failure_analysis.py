"""
Analytics Domain: Failure Analysis

This example demonstrates failure analysis features.
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
# Get Top Failed Steps
# =============================================================================

filter_data = WATSFilter(
    dateStart=datetime.now() - timedelta(days=30),
    dateStop=datetime.now()
)

top_failed = api.analytics.get_top_failed(filter_data, limit=10)

print("Top 10 Failed Steps (all products):")
for i, step in enumerate(top_failed, 1):
    print(f"  {i}. {step.stepName}:")
    print(f"     Failures: {step.failCount} ({step.failPercent:.1f}%)")


# =============================================================================
# Top Failures for Specific Product
# =============================================================================

filter_data = WATSFilter(
    partNumber="WIDGET-001",
    dateStart=datetime.now() - timedelta(days=30),
    dateStop=datetime.now()
)

top_failed = api.analytics.get_top_failed(filter_data, limit=10)

print(f"\nTop Failed Steps for WIDGET-001:")
for i, step in enumerate(top_failed, 1):
    print(f"  {i}. {step.stepName}: {step.failCount} failures")


# =============================================================================
# Test Step Analysis
# =============================================================================

# Detailed analysis of a specific step
step_analysis = api.analytics.get_test_step_analysis(
    filter_data,
    step_name="Voltage Check"
)

if step_analysis:
    print(f"\nAnalysis for 'Voltage Check':")
    print(f"  Total runs: {step_analysis.totalCount}")
    print(f"  Pass count: {step_analysis.passCount}")
    print(f"  Fail count: {step_analysis.failCount}")
    print(f"  Mean: {step_analysis.mean:.4f}")
    print(f"  Std Dev: {step_analysis.stdDev:.4f}")
    if step_analysis.cp:
        print(f"  Cp: {step_analysis.cp:.2f}")
    if step_analysis.cpk:
        print(f"  Cpk: {step_analysis.cpk:.2f}")


# =============================================================================
# Repair Statistics
# =============================================================================

repair_stats = api.analytics.get_dynamic_repair(filter_data)

print(f"\nRepair Statistics:")
for stat in repair_stats[:10]:
    print(f"  {stat.date}: {stat.repair_count} repairs")


# =============================================================================
# Related Repair History
# =============================================================================

# Get repairs related to a specific failing step
repair_history = api.analytics.get_related_repair_history(
    filter_data,
    step_name="Voltage Check"
)

print(f"\nRepair history for 'Voltage Check' failures:")
for record in repair_history[:5]:
    print(f"  Cause: {record.cause}")
    print(f"  Action: {record.action}")
    print(f"  Count: {record.count}")
    print()


# =============================================================================
# Pareto Analysis
# =============================================================================

def pareto_analysis(part_number: str, days: int = 30):
    """Perform Pareto analysis on failures."""
    filter_data = WATSFilter(
        partNumber=part_number,
        dateStart=datetime.now() - timedelta(days=days),
        dateStop=datetime.now()
    )
    
    failures = api.analytics.get_top_failed(filter_data, limit=20)
    
    if not failures:
        print(f"No failures found for {part_number}")
        return
    
    total_failures = sum(f.failCount for f in failures)
    
    print(f"\nPareto Analysis for {part_number}")
    print(f"Total failures: {total_failures}")
    print("=" * 60)
    
    cumulative = 0
    for i, step in enumerate(failures, 1):
        cumulative += step.failCount
        cumulative_pct = (cumulative / total_failures * 100)
        
        bar_len = int(step.failPercent / 2)
        bar = "█" * bar_len
        
        print(f"{i:2}. {step.stepName[:30]:30} {step.failCount:5} ({step.failPercent:5.1f}%) {bar}")
        
        if cumulative_pct >= 80 and (cumulative - step.failCount) / total_failures * 100 < 80:
            print("-" * 60 + " 80% threshold")


# pareto_analysis("WIDGET-001")


# =============================================================================
# Failure Investigation Workflow
# =============================================================================

def investigate_failures(part_number: str):
    """Complete failure investigation workflow."""
    print("=" * 60)
    print(f"FAILURE INVESTIGATION: {part_number}")
    print("=" * 60)
    
    filter_data = WATSFilter(
        partNumber=part_number,
        dateStart=datetime.now() - timedelta(days=30),
        dateStop=datetime.now()
    )
    
    # Step 1: Overall yield
    print("\n1. Overall Yield")
    volume = api.analytics.get_volume_yield(filter_data)
    if volume:
        total = sum(v.total for v in volume)
        passed = sum(v.passed for v in volume)
        yield_pct = (passed / total * 100) if total > 0 else 0
        print(f"   Yield: {yield_pct:.1f}% ({total - passed} failures out of {total})")
    
    # Step 2: Top failures
    print("\n2. Top Failing Steps")
    failures = api.analytics.get_top_failed(filter_data, limit=5)
    for f in failures:
        print(f"   - {f.stepName}: {f.failCount} ({f.failPercent:.1f}%)")
    
    # Step 3: Repair history for top failure
    if failures:
        top_step = failures[0].stepName
        print(f"\n3. Repair History for '{top_step}'")
        repairs = api.analytics.get_related_repair_history(filter_data, step_name=top_step)
        for r in repairs[:3]:
            print(f"   - {r.cause} -> {r.action} ({r.count}x)")
    
    print("=" * 60)


# investigate_failures("WIDGET-001")
