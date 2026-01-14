# Software Domain

The Software domain manages software packages and their distribution. Use this to track software versions, manage releases, organize packages with tags and folders, and associate files with packages. It supports versioning, status management (Development, Released, Obsolete), and tag-based organization.

## Table of Contents

- [Quick Start](#quick-start)
- [Core Concepts](#core-concepts)
- [Package Management](#package-management)
- [Package Files](#package-files)
- [Tags and Organization](#tags-and-organization)
- [Virtual Folders](#virtual-folders)
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

# Get all released packages
from pywats.domains.software.models import PackageStatus

released = api.software.get_packages(status=PackageStatus.RELEASED)

for pkg in released:
    print(f"{pkg.name} v{pkg.version} - {pkg.description}")

# Get specific package by name
package = api.software.get_package_by_name("FirmwareUpdate")

if package:
    print(f"Package: {package.name}")
    print(f"Version: {package.version}")
    print(f"Status: {package.status}")
    print(f"Files: {len(package.files)}")
    
    # List package files
    for file in package.files:
        print(f"  - {file.file_name} ({file.file_size} bytes)")

# Get latest released version
latest = api.software.get_released_package("FirmwareUpdate")
```

---

## Core Concepts

### Packages
A **Package** is a versioned software distribution:
- `name`: Package name (unique)
- `version`: Version string
- `status`: DEVELOPMENT, RELEASED, or OBSOLETE
- `description`: Package description
- `files`: Associated files

### Package Status
Packages can be in three states:
- **DEVELOPMENT**: Under development, not ready for release
- **RELEASED**: Released and ready for use
- **OBSOLETE**: Deprecated, no longer recommended

### Tags
**Tags** are key-value pairs for organizing packages:
- `tag`: Tag name (e.g., "product", "type")
- `value`: Tag value (e.g., "WIDGET-001", "firmware")

### Virtual Folders
**Virtual Folders** organize packages hierarchically:
- Folder-like structure without physical directories
- Packages can belong to multiple folders
- Used for logical organization (e.g., by product line, by type)

---

## Package Management

### List All Packages

```python
# Get all packages
all_packages = api.software.get_packages()

print(f"Total packages: {len(all_packages)}")

for pkg in all_packages:
    print(f"{pkg.name} v{pkg.version} [{pkg.status}]")
```

### Filter by Status

```python
from pywats.domains.software.models import PackageStatus

# Get only released packages
released = api.software.get_packages(status=PackageStatus.RELEASED)

print("=== RELEASED PACKAGES ===")
for pkg in released:
    print(f"{pkg.name} v{pkg.version}")

# Get development packages
dev_packages = api.software.get_packages(status=PackageStatus.DEVELOPMENT)

print(f"\n{len(dev_packages)} packages in development")
```

### Get Package by ID

```python
# Get specific package
package = api.software.get_package(12345)

if package:
    print(f"Package: {package.name}")
    print(f"Version: {package.version}")
    print(f"Status: {package.status}")
    print(f"Description: {package.description}")
    print(f"Created: {package.created_date_time}")
else:
    print("Package not found")
```

### Get Package by Name

```python
# Get latest version of a package by name
package = api.software.get_package_by_name("FirmwareUpdate")

if package:
    print(f"Found: {package.name} v{package.version}")
else:
    print("Package not found")

# Get specific version and status
package = api.software.get_package_by_name(
    "FirmwareUpdate",
    version="2.1.0",
    status=PackageStatus.RELEASED
)
```

### Get Latest Released Package

```python
# Get the latest released version
latest = api.software.get_released_package("FirmwareUpdate")

if latest:
    print(f"Latest released: v{latest.version}")
    print(f"Released: {latest.created_date_time}")
else:
    print("No released version found")
```

---

## Package Files

### List Package Files

```python
# Get package and its files
package = api.software.get_package_by_name("FirmwareUpdate")

if package and package.files:
    print(f"=== FILES IN {package.name} v{package.version} ===")
    
    for file in package.files:
        print(f"\n{file.file_name}:")
        print(f"  Size: {file.file_size:,} bytes")
        print(f"  Type: {file.file_type}")
        print(f"  MD5: {file.md5_checksum}")
        
        if file.description:
            print(f"  Description: {file.description}")
else:
    print("No files found")
```

### Download Package File

```python
import os

def download_package_files(package_name, destination_folder):
    """Download all files from a package"""
    
    # Get package
    package = api.software.get_released_package(package_name)
    
    if not package:
        print(f"Package '{package_name}' not found")
        return
    
    if not package.files:
        print(f"No files in package '{package_name}'")
        return
    
    # Create destination folder
    os.makedirs(destination_folder, exist_ok=True)
    
    print(f"Downloading {len(package.files)} files from {package.name} v{package.version}...")
    
    for file in package.files:
        file_path = os.path.join(destination_folder, file.file_name)
        
        # Download using software service (method depends on implementation)
        # This is a placeholder - actual implementation may vary
        print(f"  - {file.file_name} ({file.file_size:,} bytes)")
        
        # Verify checksum after download
        if hasattr(file, 'md5_checksum'):
            print(f"    MD5: {file.md5_checksum}")
    
    print(f"Downloaded to: {destination_folder}")

# Use it
download_package_files("FirmwareUpdate", "C:\\Downloads\\Firmware")
```

---

## Tags and Organization

### Query Packages by Tag

```python
# Get packages with a specific tag
packages = api.software.get_packages_by_tag(
    tag="product",
    value="WIDGET-001"
)

print(f"=== PACKAGES FOR WIDGET-001 ===")
for pkg in packages:
    print(f"{pkg.name} v{pkg.version}")

# Filter by status too
released_packages = api.software.get_packages_by_tag(
    tag="product",
    value="WIDGET-001",
    status=PackageStatus.RELEASED
)
```

### List Package Tags

```python
# Get package and inspect tags
package = api.software.get_package_by_name("FirmwareUpdate")

if package and package.tags:
    print(f"=== TAGS FOR {package.name} ===")
    
    for tag in package.tags:
        print(f"{tag.tag}: {tag.value}")
else:
    print("No tags found")
```

### Organize by Tags

```python
def list_packages_by_product():
    """Group packages by product tag"""
    
    # Get all released packages
    packages = api.software.get_packages(status=PackageStatus.RELEASED)
    
    # Group by product tag
    by_product = {}
    
    for pkg in packages:
        if pkg.tags:
            for tag in pkg.tags:
                if tag.tag == "product":
                    product = tag.value
                    if product not in by_product:
                        by_product[product] = []
                    by_product[product].append(pkg)
    
    # Display
    for product, pkgs in by_product.items():
        print(f"\n=== {product} ===")
        for pkg in pkgs:
            print(f"  {pkg.name} v{pkg.version}")

# Use it
list_packages_by_product()
```

---

## Virtual Folders

### List Folders

```python
# Get all virtual folders
folders = api.software.get_virtual_folders()

print("=== VIRTUAL FOLDERS ===")
for folder in folders:
    print(f"{folder.path}")
    print(f"  Packages: {folder.package_count}")
```

### Get Packages in Folder

```python
# Get packages in a specific folder
folder_packages = api.software.get_packages_in_folder("Firmware/Stable")

print(f"=== PACKAGES IN Firmware/Stable ===")
for pkg in folder_packages:
    print(f"{pkg.name} v{pkg.version}")
```

### Folder Hierarchy

```python
def show_folder_tree():
    """Display virtual folder hierarchy"""
    
    folders = api.software.get_virtual_folders()
    
    # Sort by path
    folders.sort(key=lambda f: f.path)
    
    print("=== PACKAGE FOLDERS ===")
    for folder in folders:
        # Calculate indent based on path depth
        depth = folder.path.count('/') + folder.path.count('\\')
        indent = "  " * depth
        folder_name = folder.path.split('/')[-1]
        
        print(f"{indent}{folder_name}/ ({folder.package_count})")

# Use it
show_folder_tree()
```

---

## Advanced Usage

### Version Comparison

```python
from packaging import version

def get_latest_version(package_name):
    """Find latest version across all statuses"""
    
    # Get all packages with this name
    packages = api.software.get_packages()
    
    # Filter by name
    matching = [p for p in packages if p.name == package_name]
    
    if not matching:
        print(f"No packages found with name '{package_name}'")
        return None
    
    # Sort by version
    matching.sort(key=lambda p: version.parse(p.version), reverse=True)
    
    latest = matching[0]
    
    print(f"=== VERSIONS OF {package_name} ===")
    for pkg in matching:
        current = " <- LATEST" if pkg == latest else ""
        print(f"v{pkg.version} [{pkg.status}]{current}")
    
    return latest

# Use it
latest = get_latest_version("FirmwareUpdate")
```

### Package Audit

```python
from datetime import datetime, timedelta

def audit_packages(days=30):
    """Find packages that need attention"""
    
    cutoff = datetime.now() - timedelta(days=days)
    
    packages = api.software.get_packages()
    
    print(f"=== PACKAGE AUDIT (last {days} days) ===\n")
    
    # Old development packages
    old_dev = [
        p for p in packages 
        if p.status == PackageStatus.DEVELOPMENT 
        and p.created_date_time < cutoff
    ]
    
    if old_dev:
        print(f"⚠ {len(old_dev)} development packages older than {days} days:")
        for pkg in old_dev:
            age = (datetime.now() - pkg.created_date_time).days
            print(f"  - {pkg.name} v{pkg.version} ({age} days old)")
    
    # Packages with no files
    no_files = [p for p in packages if not p.files]
    
    if no_files:
        print(f"\n⚠ {len(no_files)} packages with no files:")
        for pkg in no_files:
            print(f"  - {pkg.name} v{pkg.version} [{pkg.status}]")
    
    # Released packages
    released = [p for p in packages if p.status == PackageStatus.RELEASED]
    print(f"\n✓ {len(released)} released packages")

# Use it
audit_packages(days=90)
```

### Package Distribution Report

```python
def package_distribution_report():
    """Show package distribution by status"""
    
    packages = api.software.get_packages()
    
    # Count by status
    by_status = {}
    for pkg in packages:
        status = pkg.status.name if hasattr(pkg.status, 'name') else str(pkg.status)
        by_status[status] = by_status.get(status, 0) + 1
    
    # Count by tag
    by_tag = {}
    for pkg in packages:
        if pkg.tags:
            for tag in pkg.tags:
                key = f"{tag.tag}:{tag.value}"
                by_tag[key] = by_tag.get(key, 0) + 1
    
    # Display
    print("=" * 60)
    print("PACKAGE DISTRIBUTION REPORT")
    print("=" * 60)
    
    print(f"\nTotal Packages: {len(packages)}")
    
    print("\nBy Status:")
    for status, count in sorted(by_status.items()):
        print(f"  {status}: {count}")
    
    print("\nTop Tags:")
    sorted_tags = sorted(by_tag.items(), key=lambda x: x[1], reverse=True)
    for tag, count in sorted_tags[:10]:
        print(f"  {tag}: {count}")
    
    print("=" * 60)

# Use it
package_distribution_report()
```

---

## API Reference

### SoftwareService Methods

#### Package Queries
- `get_packages(status=None)` → `List[Package]` - Get all packages, optionally filtered by status
- `get_package(package_id)` → `Optional[Package]` - Get package by ID
- `get_package_by_name(name, status=None, version=None)` → `Optional[Package]` - Get package by name
- `get_released_package(name)` → `Optional[Package]` - Get latest released version

#### Tag Queries
- `get_packages_by_tag(tag, value, status=None)` → `List[Package]` - Get packages with specific tag

#### Virtual Folder Queries
- `get_virtual_folders()` → `List[VirtualFolder]` - Get all folders
- `get_packages_in_folder(folder_path)` → `List[Package]` - Get packages in folder

### Models

#### Package
- `id`: int - Package ID
- `name`: str - Package name
- `version`: str - Version string
- `status`: PackageStatus - Status (DEVELOPMENT, RELEASED, OBSOLETE)
- `description`: str - Description
- `created_date_time`: datetime - Creation timestamp
- `files`: List[PackageFile] - Associated files
- `tags`: List[PackageTag] - Tags

#### PackageFile
- `id`: int - File ID
- `file_name`: str - File name
- `file_size`: int - File size in bytes
- `file_type`: str - MIME type
- `md5_checksum`: str - MD5 hash
- `description`: str - File description

#### PackageTag
- `tag`: str - Tag name
- `value`: str - Tag value

#### VirtualFolder
- `id`: int - Folder ID
- `path`: str - Folder path
- `package_count`: int - Number of packages

#### PackageStatus (Enum)
- `DEVELOPMENT` - Under development
- `RELEASED` - Released and ready
- `OBSOLETE` - Deprecated

---

## Best Practices

1. **Use status filtering** - Filter by RELEASED for production deployments
2. **Version semantically** - Use semantic versioning (major.minor.patch)
3. **Tag consistently** - Establish tag naming conventions
4. **Verify checksums** - Always verify MD5 checksums after download
5. **Organize with folders** - Use virtual folders for logical grouping
6. **Archive old versions** - Mark as OBSOLETE instead of deleting
7. **Document packages** - Provide clear descriptions
8. **Track associations** - Tag packages with product/component info

---

## See Also

- [Product Domain](PRODUCT.md) - Products and revisions
- [Production Domain](PRODUCTION.md) - Unit production and assembly
- [Asset Domain](ASSET.md) - Equipment and calibration
