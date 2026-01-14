"""
Report Domain: Query Reports

This example demonstrates querying and filtering reports.
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
# Get Report Headers (List)
# =============================================================================

# Get recent report headers
headers = api.report.query_uut_headers()

print(f"Found {len(headers)} reports")
for header in headers[:5]:
    print(f"  {header.serialNumber}: {header.result} ({header.start})")


# =============================================================================
# Filter by Date Range
# =============================================================================

filter_data = WATSFilter(
    dateStart=datetime.now() - timedelta(days=7),
    dateStop=datetime.now()
)

headers = api.report.query_uut_headers(filter_data)
print(f"\nReports from last 7 days: {len(headers)}")


# =============================================================================
# Filter by Part Number
# =============================================================================

filter_data = WATSFilter(partNumber="WIDGET-001")

headers = api.report.query_uut_headers(filter_data)
print(f"\nReports for WIDGET-001: {len(headers)}")


# =============================================================================
# Filter by Serial Number
# =============================================================================

filter_data = WATSFilter(serialNumber="SN-2024-001234")

headers = api.report.query_uut_headers(filter_data)
print(f"\nReports for serial SN-2024-001234: {len(headers)}")


# =============================================================================
# Filter by Result
# =============================================================================

# Get failed reports only
filter_data = WATSFilter(
    dateStart=datetime.now() - timedelta(days=7),
    status="Failed"
)

headers = api.report.query_uut_headers(filter_data)
print(f"\nFailed reports (last 7 days): {len(headers)}")

for header in headers[:5]:
    print(f"  {header.serialNumber}: {header.partNumber}")


# =============================================================================
# Get Full Report
# =============================================================================

# Get a report by ID
report_id = "some-report-uuid"  # Replace with actual ID
report = api.report.get_report(report_id)

if report:
    print(f"\nFull Report:")
    print(f"  Serial: {report.sn}")
    print(f"  Part: {report.pn}")
    print(f"  Result: {report.result}")
    print(f"  Steps: {len(report.root.steps) if report.root else 0}")


# =============================================================================
# Get Serial Number History
# =============================================================================

# Get all reports for a serial number
history = api.analytics.get_sn_history("SN-2024-001234")

print(f"\nHistory for SN-2024-001234:")
for report in history:
    print(f"  {report.start}: {report.result} ({report.processCode})")


# =============================================================================
# Combined Filters
# =============================================================================

filter_data = WATSFilter(
    partNumber="WIDGET-001",
    dateStart=datetime.now() - timedelta(days=30),
    dateStop=datetime.now(),
    status="Failed",
)

headers = api.report.query_uut_headers(filter_data)
print(f"\nFailed WIDGET-001 reports (last 30 days): {len(headers)}")


# =============================================================================
# Report Query with Pagination
# =============================================================================

# Get reports in batches
all_headers = []
page = 0
page_size = 100

while True:
    filter_data = WATSFilter(
        dateStart=datetime.now() - timedelta(days=7),
        skip=page * page_size,
        top=page_size
    )
    
    headers = api.report.query_uut_headers(filter_data)
    
    if not headers:
        break
    
    all_headers.extend(headers)
    page += 1
    
    if len(headers) < page_size:
        break

print(f"\nTotal reports (paginated): {len(all_headers)}")
