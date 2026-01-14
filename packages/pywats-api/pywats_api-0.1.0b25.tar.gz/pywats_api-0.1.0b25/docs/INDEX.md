# PyWATS Documentation

Official documentation for pyWATS - Python API library for WATS (Web-based Automated Test System).

## Getting Started

- **[Getting Started Guide](GETTING_STARTED.md)** - Complete installation, configuration, and initialization guide
- **[README](../README.md)** - Package overview and quick start
- **[CHANGELOG](../CHANGELOG.md)** - Version history and release notes

## Domain Guides

Complete documentation for each WATS domain with examples and API reference:

### Core Domains

- **[Product Domain](PRODUCT.md)** - Products, revisions, BOMs, box build templates, vendors, categories
- **[Asset Domain](ASSET.md)** - Equipment tracking, calibration, maintenance, hierarchy, logs
- **[Production Domain](PRODUCTION.md)** - Unit lifecycle, serial numbers, assembly, verification, phases
- **[Report Domain](REPORT.md)** - Test reports (UUT/UUR), all step types, querying, attachments

### Analysis & Tracking

- **[Analytics Domain](ANALYTICS.md)** - Yield analysis, measurements, Cpk statistics, Unit Flow visualization
- **[Software Domain](SOFTWARE.md)** - Package management, versioning, distribution, tags, virtual folders
- **[RootCause Domain](ROOTCAUSE.md)** - Issue tracking, defect management, status workflows, priorities
- **[Process Domain](PROCESS.md)** - Operation types, test/repair processes, caching

### Detailed Module Guides

Legacy usage guides with comprehensive examples and patterns:

- **[Report Module Guide](usage/REPORT_MODULE.md)** - Detailed report creation and querying
- **[Product Module Guide](usage/PRODUCT_MODULE.md)** - Product and BOM management
- **[Production Module Guide](usage/PRODUCTION_MODULE.md)** - Serial number and unit tracking
- **[Asset Module Guide](usage/ASSET_MODULE.md)** - Equipment and calibration management
- **[Software Module Guide](usage/SOFTWARE_MODULE.md)** - Package distribution
- **[RootCause Module Guide](usage/ROOTCAUSE_MODULE.md)** - Ticket and defect tracking
- **[Process Module Guide](usage/PROCESS_MODULE.md)** - Process operations
- **[Box Build Guide](usage/BOX_BUILD_GUIDE.md)** - Assembly and box build workflows

## Client Documentation

Documentation for the pyWATS Client application:

- **[GUI Configuration](../src/pywats_client/GUI_CONFIGURATION.md)** - Configure GUI tabs, logging, and settings
- **[Headless Operation Guide](../src/pywats_client/control/HEADLESS_GUIDE.md)** - Run on Raspberry Pi, servers, embedded systems

## Quick Reference by Task

### Creating Test Reports
Start with [Report Domain](REPORT.md) - Learn how to create UUT reports with all step types

### Managing Products & BOMs
See [Product Domain](PRODUCT.md) - Product creation, revisions, BOMs, box build workflows

### Tracking Units Through Production
See [Production Domain](PRODUCTION.md) - Serial numbers, unit phases, assembly, verification

### Equipment & Calibration
See [Asset Domain](ASSET.md) - Asset tracking, calibration schedules, maintenance

### Analyzing Yield & Quality
See [Analytics Domain](ANALYTICS.md) - Yield calculations, measurement statistics, Cpk analysis

### Software Distribution
See [Software Domain](SOFTWARE.md) - Package management, versioning, releases

### Issue Tracking
See [RootCause Domain](ROOTCAUSE.md) - Create tickets, track defects, manage workflows

### Operation Types
See [Process Domain](PROCESS.md) - Define test/repair operations, process caching

## Links

- **GitHub Repository**: https://github.com/olreppe/pyWATS
- **WATS Website**: https://wats.com
- **Virinco**: https://virinco.com
- **PyPI Package**: https://pypi.org/project/pywats-api/

## Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/olreppe/pyWATS/issues
- Email: support@virinco.com
