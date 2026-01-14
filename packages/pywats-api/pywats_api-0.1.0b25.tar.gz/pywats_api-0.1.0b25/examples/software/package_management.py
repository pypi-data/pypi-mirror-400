"""
Software Domain: Package Management

This example demonstrates software package distribution.
"""
import os
from datetime import datetime
from pywats import pyWATS

# =============================================================================
# Setup
# =============================================================================

api = pyWATS(
    base_url=os.environ.get("WATS_BASE_URL", "https://demo.wats.com"),
    token=os.environ.get("WATS_TOKEN", "")
)


# =============================================================================
# Get Software Packages
# =============================================================================

# Get all packages
packages = api.software.get_packages()

print(f"Found {len(packages)} software packages")
for pkg in packages[:5]:
    print(f"  {pkg.name} v{pkg.version} - {pkg.status}")


# =============================================================================
# Get Single Package
# =============================================================================

package = api.software.get_package("TEST-SOFTWARE-001")

if package:
    print(f"\nPackage: {package.name}")
    print(f"  Version: {package.version}")
    print(f"  Status: {package.status}")
    print(f"  Description: {package.description}")
    print(f"  Created: {package.created}")


# =============================================================================
# Create Software Package
# =============================================================================

from pywats.domains.software import SoftwarePackage

new_package = SoftwarePackage(
    name="Test Sequencer Update",
    version="2.1.0",
    description="Bug fixes and performance improvements",
    status="Draft"
)

result = api.software.create_package(new_package)
print(f"\nCreated package: {result.name} v{result.version}")


# =============================================================================
# Upload Package File
# =============================================================================

# Upload a zip file to a package
with open("test_sequencer_2.1.0.zip", "rb") as f:
    file_data = f.read()

api.software.upload_file(
    package_id="PKG-001",
    filename="test_sequencer_2.1.0.zip",
    data=file_data
)

print("Uploaded package file")


# =============================================================================
# Update Package Status
# =============================================================================

package = api.software.get_package("PKG-001")

if package:
    package.status = "Under Review"
    api.software.update_package(package)
    print(f"Updated package status to: Under Review")


# =============================================================================
# Release Workflow
# =============================================================================

def release_workflow(package_id: str):
    """Software release workflow."""
    print("=" * 50)
    print("Software Release Workflow")
    print("=" * 50)
    
    # 1. Get package
    print("\n1. Getting package...")
    package = api.software.get_package(package_id)
    print(f"   {package.name} v{package.version}")
    
    # 2. Submit for review
    print("\n2. Submitting for review...")
    package.status = "Under Review"
    api.software.update_package(package)
    
    # 3. Approve
    print("\n3. Approving package...")
    package.status = "Approved"
    package.approvedBy = "manager@company.com"
    package.approvedDate = datetime.now()
    api.software.update_package(package)
    
    # 4. Release
    print("\n4. Releasing package...")
    package.status = "Released"
    package.releasedDate = datetime.now()
    api.software.update_package(package)
    
    print(f"\n   ✓ Package released!")
    print("=" * 50)


# release_workflow("PKG-001")


# =============================================================================
# Download Package
# =============================================================================

# Download released package
file_data = api.software.download_file("PKG-001", "test_sequencer_2.1.0.zip")

with open("downloaded_package.zip", "wb") as f:
    f.write(file_data)

print("Downloaded package file")


# =============================================================================
# Get Packages by Status
# =============================================================================

# Get released packages
released = [p for p in api.software.get_packages() if p.status == "Released"]
print(f"\nReleased packages: {len(released)}")

# Get packages under review
under_review = [p for p in api.software.get_packages() if p.status == "Under Review"]
print(f"Under review: {len(under_review)}")
