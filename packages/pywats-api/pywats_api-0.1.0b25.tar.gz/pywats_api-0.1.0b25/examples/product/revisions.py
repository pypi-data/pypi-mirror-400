"""
Product Domain: Revision Management

This example demonstrates product revision operations.
"""
import os
from pywats import pyWATS

# =============================================================================
# Setup
# =============================================================================

api = pyWATS(
    base_url=os.environ.get("WATS_BASE_URL", "https://demo.wats.com"),
    token=os.environ.get("WATS_TOKEN", "")
)


# =============================================================================
# Get Product Revisions
# =============================================================================

# Get all revisions for a product
revisions = api.product.get_revisions("WIDGET-001")

print(f"Revisions for WIDGET-001:")
for rev in revisions:
    print(f"  Rev {rev.revision}: {rev.description or 'No description'}")
    if rev.effectiveDate:
        print(f"    Effective: {rev.effectiveDate}")


# =============================================================================
# Get Specific Revision
# =============================================================================

# Get a specific revision
revision = api.product.get_revision("WIDGET-001", "B")

if revision:
    print(f"Revision B details:")
    print(f"  Created: {revision.created}")
    print(f"  Description: {revision.description}")


# =============================================================================
# Create New Revision
# =============================================================================

from pywats.domains.product import ProductRevision

# Create a new revision
new_revision = ProductRevision(
    partNumber="WIDGET-001",
    revision="C",
    description="Added new feature X"
)

result = api.product.create_revision(new_revision)
print(f"Created revision: {result.revision}")


# =============================================================================
# Revision History Workflow
# =============================================================================

# Get product with all revisions
product = api.product.get_product("WIDGET-001")
revisions = api.product.get_revisions("WIDGET-001")

print(f"\nProduct: {product.partNumber} - {product.productName}")
print("Revision History:")
for rev in sorted(revisions, key=lambda r: r.revision):
    status = "CURRENT" if rev.revision == product.revision else ""
    print(f"  {rev.revision}: {rev.description or '-'} {status}")
