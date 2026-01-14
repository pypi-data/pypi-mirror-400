# Software Module Usage Guide

## Overview

The Software module provides functionality for managing software distribution packages in WATS. These packages are used to distribute software, configurations, and files to test stations and production equipment.

## Quick Start

```python
from pywats import pyWATS
from pywats.domains.software import PackageStatus

api = pyWATS(base_url="https://wats.example.com", token="credentials")

# Get all software packages
packages = api.software.get_packages()

# Get a released package by name
package = api.software.get_released_package("TestExecutive")

# Create a new package
new_pkg = api.software.create_package(
    name="MyTestSoftware",
    description="Test station software v2.0",
    priority=10
)
```

## Package Status Workflow

Software packages follow a strict status workflow:

```
DRAFT ─────► PENDING ─────► RELEASED ─────► REVOKED
  ▲             │
  └─────────────┘
     (return)
```

| Status | Description | Can Edit | Can Delete |
|--------|-------------|----------|------------|
| `DRAFT` | Initial state, under development | All fields | ✅ Yes |
| `PENDING` | Submitted for review | Status, Tags only | ❌ No |
| `RELEASED` | Approved for distribution | Status, Tags only | ❌ No |
| `REVOKED` | Withdrawn from distribution | - | ✅ Yes |

```python
from pywats.domains.software import PackageStatus

# Status enum values
PackageStatus.DRAFT      # "Draft"
PackageStatus.PENDING    # "Pending"
PackageStatus.RELEASED   # "Released"
PackageStatus.REVOKED    # "Revoked"
```

## Basic Operations

### 1. List All Packages

```python
# Get all packages
packages = api.software.get_packages()

for pkg in packages:
    print(f"{pkg.name} v{pkg.version} [{pkg.status.value}]")
```

### 2. Get Package by ID

```python
# Get specific package
package = api.software.get_package(package_id)

if package:
    print(f"Name: {package.name}")
    print(f"Version: {package.version}")
    print(f"Status: {package.status.value}")
    print(f"Description: {package.description}")
```

### 3. Get Package by Name

```python
# Get package by name and status
package = api.software.get_package_by_name(
    name="TestExecutive",
    status=PackageStatus.RELEASED,
    version=2  # Optional - omit for latest
)

# Convenience method for released packages
released = api.software.get_released_package("TestExecutive")
```

### 4. Create Package

```python
from pywats.domains.software import PackageTag

# Create with basic info
package = api.software.create_package(
    name="MyTestSoftware",
    description="Automated test software for production",
    install_on_root=False,
    root_directory="/TestStation",
    priority=10,
)

# Create with tags
tags = [
    PackageTag(key="platform", value="windows"),
    PackageTag(key="category", value="test-executive"),
    PackageTag(key="version", value="2.0.0"),
]

package = api.software.create_package(
    name="TaggedSoftware",
    description="Software with metadata tags",
    tags=tags,
)
```

**Note:** If a package with the same name exists, the new version will be incremented automatically.

### 5. Update Package

```python
# Get package
package = api.software.get_package(package_id)

# Update metadata (only in DRAFT status)
package.description = "Updated description"
package.priority = 20

updated = api.software.update_package(package)
```

**Note:** Only DRAFT packages allow full editing. PENDING and RELEASED packages can only have Status and Tags updated.

### 6. Delete Package

```python
# Delete by ID (must be DRAFT or REVOKED)
success = api.software.delete_package(package_id)

# Delete by name and version
success = api.software.delete_package_by_name("MyTestSoftware", version=1)
```

## Status Workflow Methods

### Submit for Review (Draft → Pending)

```python
success = api.software.submit_for_review(package_id)
if success:
    print("Package submitted for review")
```

### Return to Draft (Pending → Draft)

```python
success = api.software.return_to_draft(package_id)
if success:
    print("Package returned to draft")
```

### Release Package (Pending → Released)

```python
success = api.software.release_package(package_id)
if success:
    print("Package released for distribution")
```

### Revoke Package (Released → Revoked)

```python
success = api.software.revoke_package(package_id)
if success:
    print("Package revoked")
```

## Package Files

### List Package Files

```python
files = api.software.get_package_files(package_id)

for f in files:
    size_mb = f.size / (1024 * 1024) if f.size else 0
    print(f"{f.filename} - {size_mb:.2f} MB")
    print(f"  Path: {f.path}")
    print(f"  Checksum: {f.checksum}")
    print(f"  Attributes: {f.attributes}")
```

### Upload Zip File

```python
# Read zip file
with open("software_package.zip", "rb") as f:
    zip_content = f.read()

# Upload to package (merge with existing)
success = api.software.upload_zip(
    package_id=package_id,
    zip_content=zip_content,
    clean_install=False  # Merge files
)

# Upload with clean install (delete existing first)
success = api.software.upload_zip(
    package_id=package_id,
    zip_content=zip_content,
    clean_install=True  # Delete all existing files first
)
```

**Zip File Requirements:**
- Files cannot be at the root level of the zip
- All files must be in a folder: `zipFile/myFolder/myFile.txt`

### Update File Attributes

```python
# Get files first
files = api.software.get_package_files(package_id)

# Update attribute for a file
target_file = next(f for f in files if f.filename == "setup.exe")

success = api.software.update_file_attribute(
    file_id=target_file.file_id,
    attributes="ExecuteOnce"
)
```

**File Attribute Values:**
| Attribute | Description |
|-----------|-------------|
| `None` | No special handling |
| `ExecuteOnce` | Execute once after install |
| `ExecuteAlways` | Execute on every sync |
| `TopLevelFile` | Display in package root |
| `OverwriteNever` | Never overwrite existing |
| `OverwriteOnNewPackageVersion` | Only overwrite on new version |
| `ExecuteOncePerVersion` | Execute once per package version |

## Package Tags

Tags provide metadata for filtering and organizing packages.

### Create Package with Tags

```python
from pywats.domains.software import PackageTag

tags = [
    PackageTag(key="platform", value="windows"),
    PackageTag(key="environment", value="production"),
    PackageTag(key="owner", value="test-engineering"),
]

package = api.software.create_package(
    name="TaggedPackage",
    description="Package with tags",
    tags=tags,
)
```

### Filter by Tag

```python
# Get packages with specific tag
packages = api.software.get_packages_by_tag(
    tag="platform",
    value="windows",
    status=PackageStatus.RELEASED
)

for pkg in packages:
    print(f"{pkg.name} v{pkg.version}")
```

## Virtual Folders

Virtual folders are registered directories in Production Manager.

```python
# Get all virtual folders
folders = api.software.get_virtual_folders()

for folder in folders:
    print(f"{folder.name}: {folder.path}")
    print(f"  Description: {folder.description}")
```

## Common Patterns

### Pattern 1: Create and Release Package

```python
def create_and_release_package(api, name, description, zip_path):
    """Create a package and release it for distribution"""
    
    # 1. Create draft package
    package = api.software.create_package(
        name=name,
        description=description,
    )
    
    if not package:
        raise Exception("Failed to create package")
    
    # 2. Upload files
    with open(zip_path, "rb") as f:
        zip_content = f.read()
    
    api.software.upload_zip(
        package_id=package.package_id,
        zip_content=zip_content,
        clean_install=True
    )
    
    # 3. Submit for review
    api.software.submit_for_review(package.package_id)
    
    # 4. Release (requires approval workflow in production)
    api.software.release_package(package.package_id)
    
    return api.software.get_package(package.package_id)
```

### Pattern 2: Get Latest Released Package

```python
def get_latest_package(api, name):
    """Get the latest released version of a package"""
    return api.software.get_package_by_name(
        name=name,
        status=PackageStatus.RELEASED
        # Omit version to get highest version
    )
```

### Pattern 3: Package Version Comparison

```python
def is_newer_version_available(api, name, current_version):
    """Check if a newer released version exists"""
    latest = api.software.get_released_package(name)
    
    if latest and latest.version:
        return latest.version > current_version
    return False
```

### Pattern 4: Revoke and Replace Package

```python
def replace_package(api, old_pkg_id, new_zip_path):
    """Revoke old package and create replacement"""
    
    # Get old package info
    old_pkg = api.software.get_package(old_pkg_id)
    
    # Revoke old package (if released)
    if old_pkg.status == PackageStatus.RELEASED:
        api.software.revoke_package(old_pkg_id)
    
    # Create new version (auto-increments version number)
    new_pkg = api.software.create_package(
        name=old_pkg.name,
        description=old_pkg.description,
        priority=old_pkg.priority,
        tags=old_pkg.tags,
    )
    
    # Upload new files
    with open(new_zip_path, "rb") as f:
        api.software.upload_zip(new_pkg.package_id, f.read(), clean_install=True)
    
    return new_pkg
```

## Model Reference

### Package

| Field | Type | Description |
|-------|------|-------------|
| `package_id` | UUID | Unique identifier |
| `name` | str | Package name |
| `description` | str | Package description |
| `version` | int | Version number (auto-incremented) |
| `status` | PackageStatus | Current status |
| `install_on_root` | bool | Install at root level |
| `root_directory` | str | Root installation directory |
| `priority` | int | Installation priority |
| `tags` | List[PackageTag] | Metadata tags |
| `created_utc` | datetime | Creation timestamp |
| `modified_utc` | datetime | Last modification |
| `created_by` | str | Creator username |
| `modified_by` | str | Last modifier username |
| `files` | List[PackageFile] | Package files (when populated) |

### PackageFile

| Field | Type | Description |
|-------|------|-------------|
| `file_id` | UUID | File identifier |
| `filename` | str | File name |
| `path` | str | Full path within package |
| `size` | int | File size in bytes |
| `checksum` | str | File checksum |
| `attributes` | str | File attributes |
| `created_utc` | datetime | Creation timestamp |
| `modified_utc` | datetime | Last modification |

### PackageTag

| Field | Type | Description |
|-------|------|-------------|
| `key` | str | Tag name/key |
| `value` | str | Tag value |

### VirtualFolder

| Field | Type | Description |
|-------|------|-------------|
| `folder_id` | UUID | Folder identifier |
| `name` | str | Folder name |
| `path` | str | Folder path |
| `description` | str | Folder description |

## Best Practices

### 1. Use Meaningful Names

```python
# Good - descriptive name with version info
"TestExecutive_EOL_v2"
"Calibration_Tools_ICT"

# Avoid - vague names
"Software1"
"Package"
```

### 2. Use Tags for Organization

```python
# Organize by metadata
tags = [
    PackageTag(key="platform", value="windows"),
    PackageTag(key="station_type", value="ICT"),
    PackageTag(key="maintainer", value="test-team"),
    PackageTag(key="semantic_version", value="2.1.0"),
]
```

### 3. Always Test Before Release

```python
# Create and test in DRAFT
package = api.software.create_package(...)
api.software.upload_zip(package.package_id, zip_content)

# Verify files
files = api.software.get_package_files(package.package_id)
assert len(files) > 0

# Then release
api.software.submit_for_review(package.package_id)
api.software.release_package(package.package_id)
```

### 4. Clean Up Test Packages

```python
# Delete test packages after testing
if package.status in [PackageStatus.DRAFT, PackageStatus.REVOKED]:
    api.software.delete_package(package.package_id)
```

## Troubleshooting

### Cannot Delete Package

```python
# Must be DRAFT or REVOKED to delete
package = api.software.get_package(package_id)

if package.status == PackageStatus.RELEASED:
    api.software.revoke_package(package_id)
elif package.status == PackageStatus.PENDING:
    api.software.return_to_draft(package_id)

# Now can delete
api.software.delete_package(package_id)
```

### Zip Upload Fails

```python
# Ensure zip has proper structure
# Files must be in a folder, not at root
# Correct: mypackage.zip/installer/setup.exe
# Wrong:   mypackage.zip/setup.exe (at root)
```

### Status Transition Fails

```python
# Only valid transitions:
# Draft -> Pending (submit_for_review)
# Pending -> Draft (return_to_draft)
# Pending -> Released (release_package)
# Released -> Revoked (revoke_package)

# Cannot skip steps (e.g., Draft -> Released)
```

## Limitations

### Package File Download Not Supported

Downloading package files is not currently supported through the PyWATS API. 
Files can only be uploaded to packages, not downloaded.

To access package files, use the WATS web interface or Production Manager.

## Related Documentation

- [Process Module](PROCESS_MODULE.md) - Test/repair operations
- [Production Module](PRODUCTION_MODULE.md) - Production units
- [Asset Module](ASSET_MODULE.md) - Test station assets
