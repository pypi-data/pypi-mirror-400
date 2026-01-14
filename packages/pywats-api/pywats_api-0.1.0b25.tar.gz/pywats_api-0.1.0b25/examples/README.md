# pyWATS Examples

Comprehensive examples organized by domain for the pyWATS library.

## Quick Start

```python
from pywats import pyWATS

# Initialize the API
api = pyWATS(
    base_url="https://your-wats-server.com",
    token="your-base64-token"  # Base64 of "username:password"
)

# Access any domain
products = api.product.get_products()
```

## Directory Structure

```
examples/
├── getting_started/          # Basic setup and connection
│   ├── 01_connection.py      # API connection basics
│   ├── 02_authentication.py  # Authentication options
│   └── 03_station_setup.py   # Test station configuration
│
├── product/                  # Product management
│   ├── basic_operations.py   # CRUD operations
│   ├── revisions.py          # Revision management
│   ├── bom_management.py     # Bill of Materials
│   └── product_groups.py     # Product grouping
│
├── asset/                    # Asset management
│   ├── basic_operations.py   # CRUD operations
│   ├── calibration.py        # Calibration tracking
│   ├── maintenance.py        # Maintenance scheduling
│   └── monitoring.py         # Status monitoring
│
├── report/                   # Test report handling
│   ├── create_uut_report.py  # Create test reports
│   ├── create_uur_report.py  # Create repair reports
│   ├── query_reports.py      # Query and filter
│   ├── step_types.py         # Different step types
│   └── attachments.py        # File attachments
│
├── analytics/                # Statistics and KPIs
│   ├── yield_analysis.py     # Yield statistics
│   ├── failure_analysis.py   # Top failed steps
│   ├── measurements.py       # Measurement data
│   └── oee_analysis.py       # OEE metrics
│
├── production/               # Production management
│   ├── unit_tracking.py      # Unit lifecycle
│   ├── serial_numbers.py     # Serial number allocation
│   ├── phase_management.py   # Production phases
│   └── assembly.py           # Box build/assembly
│
├── rootcause/                # Issue tracking
│   ├── ticket_management.py  # Ticket CRUD
│   ├── workflow.py           # Status workflow
│   └── attachments.py        # File attachments
│
├── software/                 # Software distribution
│   ├── package_management.py # Package CRUD
│   ├── release_workflow.py   # Review/release process
│   └── file_upload.py        # ZIP uploads
│
├── process/                  # Process configuration
│   └── operations.py         # Test/repair operations
│
└── advanced/                 # Advanced patterns
    ├── error_handling.py     # Exception handling
    ├── batch_operations.py   # Bulk operations
    ├── converters.py         # Data converters
    └── async_patterns.py     # Async usage
```

## Requirements

```bash
pip install pywats-api
```

## Environment Setup

Set these environment variables (or use a `.env` file):

```bash
WATS_BASE_URL=https://your-wats-server.com
WATS_TOKEN=your-base64-encoded-token
```

## Running Examples

```bash
# Run any example
python examples/product/basic_operations.py

# Or import in your code
from examples.product.basic_operations import demo_product_crud
```

## Note

These examples use placeholder URLs and tokens. Replace with your actual WATS server configuration.
