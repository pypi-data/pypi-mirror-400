"""
Product Domain: Product Groups

This example demonstrates product group operations.
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
# Get Product Groups
# =============================================================================

# Get all product groups from analytics service
groups = api.analytics.get_product_groups()

print("Product Groups:")
for group in groups:
    print(f"  {group.name}")


# =============================================================================
# Filter Products by Group
# =============================================================================

from pywats.domains.report import WATSFilter

# Create filter for a specific product group
filter_data = WATSFilter(productGroup="Consumer Electronics")

# Use filter in analytics queries
yield_data = api.analytics.get_dynamic_yield(filter_data)

print(f"Yield data for 'Consumer Electronics' group: {len(yield_data)} data points")


# =============================================================================
# Products in a Group
# =============================================================================

# Get all products and filter by group (if group info is available)
products = api.product.get_products()

# Group products by some criteria
product_groups = {}
for product in products:
    # Use first 3 chars of part number as group (example)
    prefix = product.partNumber[:3] if product.partNumber else "UNK"
    if prefix not in product_groups:
        product_groups[prefix] = []
    product_groups[prefix].append(product)

print("\nProducts by prefix:")
for prefix, prods in product_groups.items():
    print(f"  {prefix}: {len(prods)} products")
