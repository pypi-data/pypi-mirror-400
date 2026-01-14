"""
Product Domain: Basic Operations

This example demonstrates basic product CRUD operations.
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
# List Products
# =============================================================================

# Get all products
products = api.product.get_products()
print(f"Found {len(products)} products")

for product in products[:5]:  # First 5
    print(f"  {product.part_number}: {product.name}")


# =============================================================================
# Get Single Product
# =============================================================================

# Get product by part number
product = api.product.get_product("WIDGET-001")

if product:
    print(f"Product: {product.part_number}")
    print(f"  Name: {product.name}")
    print(f"  Description: {product.description}")


# =============================================================================
# Search Products
# =============================================================================

# Search by pattern (if supported)
results = api.product.search_products("WIDGET")
print(f"Found {len(results)} products matching 'WIDGET'")


# =============================================================================
# Create Product
# =============================================================================

from pywats.domains.product import Product

# Create a new product
new_product = Product(
    part_number="NEW-PRODUCT-001",
    name="New Test Product",
    description="A product created via the API"
)

result = api.product.save(new_product)
print(f"Created product: {result.part_number}")


# =============================================================================
# Update Product
# =============================================================================

# Get existing product
product = api.product.get_product("NEW-PRODUCT-001")

if product:
    # Modify fields
    product.description = "Updated description"
    
    # Save changes
    api.product.save(product)
    print(f"Updated product: {product.part_number}")


# =============================================================================
# Delete Product
# =============================================================================

# Delete by part number (use with caution!)
# api.product.delete_product("NEW-PRODUCT-001")
# print("Product deleted")
