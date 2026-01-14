# Product Domain

The Product domain manages product catalog data including product definitions, revisions, bills of materials (BOM), product groups, vendors, and box build templates. This domain is essential for defining WHAT you manufacture before you can track units in production.

## Table of Contents

- [Quick Start](#quick-start)
- [Core Concepts](#core-concepts)
- [Product Operations](#product-operations)
- [Revision Management](#revision-management)
- [Bill of Materials (BOM)](#bill-of-materials-bom)
- [Box Build Templates](#box-build-templates)
- [Product Groups](#product-groups)
- [Tags and Metadata](#tags-and-metadata)
- [Vendors](#vendors)
- [Product Categories](#product-categories)
- [Advanced Usage](#advanced-usage)
- [API Reference](#api-reference)

---

## Quick Start

```python
from pywats import pyWATS

# Initialize the API
api = pyWATS(
    base_url="https://your-wats-server.com",
    token="your-api-token"
)

# Get all products
products = api.product.get_products()
for product in products:
    print(f"{product.part_number}: {product.name}")

# Get a specific product with full details
product = api.product.get_product("WIDGET-001")
print(f"Product: {product.name}")
print(f"State: {product.state}")

# Create a new product
new_product = api.product.create_product(
    part_number="WIDGET-002",
    name="Advanced Widget",
    description="Next generation widget with AI capabilities"
)

# Create a revision
revision = api.product.create_revision(
    part_number="WIDGET-002",
    revision="A",
    name="Initial Release",
    description="First production version"
)
```

---

## Core Concepts

### Product
A **Product** represents a manufactured item in your catalog. It's identified by a unique part number and can have multiple revisions.

**Key attributes:**
- `part_number`: Unique identifier (e.g., "WIDGET-001")
- `name`: Human-readable product name
- `description`: Detailed description
- `state`: ACTIVE or INACTIVE
- `non_serial`: If True, units don't have serial numbers

### Product Revision
A **ProductRevision** represents a specific version or iteration of a product. Different revisions might have different components, specifications, or manufacturing processes.

**Key attributes:**
- `part_number`: Parent product identifier
- `revision`: Revision identifier (e.g., "A", "1.0", "rev2")
- `name`: Revision name
- `description`: What changed in this revision
- `state`: ACTIVE or INACTIVE

### Product View
A simplified view of a product containing only essential fields. Used for listings where full detail isn't needed.

---

## Product Operations

### List All Products

```python
# Get simplified product views (faster, less data)
products = api.product.get_products()
for product in products:
    print(f"{product.part_number}: {product.name} [{product.state}]")

# Get full product details (includes all fields)
products_full = api.product.get_products_full()
for product in products_full:
    print(f"{product.part_number}")
    print(f"  ID: {product.product_id}")
    print(f"  Created: {product.created}")
    print(f"  Modified: {product.modified}")
```

### Get Active Products Only

```python
# Filter for active products only
active_products = api.product.get_active_products()
print(f"Found {len(active_products)} active products")
```

### Get Specific Product

```python
# Get product by part number
product = api.product.get_product("WIDGET-001")

if product:
    print(f"Product: {product.name}")
    print(f"Part Number: {product.part_number}")
    print(f"State: {product.state}")
    print(f"Non-Serial: {product.non_serial}")
    print(f"Current Revision: {product.revision}")
else:
    print("Product not found")
```

### Create New Product

```python
from pywats.domains.product import ProductState

# Create a basic product
new_product = api.product.create_product(
    part_number="MAIN-BOARD-001",
    name="Main Circuit Board",
    description="Primary control board for XYZ system",
    state=ProductState.ACTIVE
)

# Create a non-serial product (consumables, bulk items)
consumable = api.product.create_product(
    part_number="SCREW-M3-10MM",
    name="M3 x 10mm Screw",
    description="Stainless steel machine screw",
    non_serial=True,  # No serial number tracking
    state=ProductState.ACTIVE
)

# Create with custom XML data for key-value storage
product_with_metadata = api.product.create_product(
    part_number="WIDGET-003",
    name="Special Widget",
    xml_data='<data><color>blue</color><weight>1.5kg</weight></data>'
)
```

### Update Existing Product

```python
# Get the product
product = api.product.get_product("WIDGET-001")

# Modify fields
product.name = "Updated Widget Name"
product.description = "New and improved description"
product.state = ProductState.ACTIVE

# Save changes
updated_product = api.product.update_product(product)
print(f"Updated: {updated_product.part_number}")
```

### Bulk Create/Update Products

```python
from pywats.domains.product import Product

# Create multiple products at once
products = [
    Product(
        part_number="BATCH-001",
        name="Batch Product 1",
        state=ProductState.ACTIVE
    ),
    Product(
        part_number="BATCH-002",
        name="Batch Product 2",
        state=ProductState.ACTIVE
    ),
    Product(
        part_number="BATCH-003",
        name="Batch Product 3",
        state=ProductState.ACTIVE
    )
]

# Bulk save
saved_products = api.product.bulk_save_products(products)
print(f"Created {len(saved_products)} products")
```

### Check Product State

```python
product = api.product.get_product("WIDGET-001")

# Check if product is active
if api.product.is_active(product):
    print("Product is active and can be used in production")
else:
    print("Product is inactive")
```

---

## Revision Management

### List Product Revisions

```python
# Get all revisions for a product
revisions = api.product.get_revisions("WIDGET-001")

print("Revision History:")
for rev in sorted(revisions, key=lambda r: r.revision):
    print(f"  {rev.revision}: {rev.description or 'No description'}")
    if rev.effective_date:
        print(f"    Effective: {rev.effective_date}")
```

### Get Specific Revision

```python
# Get a specific revision
revision = api.product.get_revision("WIDGET-001", "B")

if revision:
    print(f"Revision: {revision.revision}")
    print(f"Name: {revision.name}")
    print(f"Description: {revision.description}")
    print(f"State: {revision.state}")
    print(f"Created: {revision.created}")
```

### Create New Revision

```python
# Create a new revision
new_revision = api.product.create_revision(
    part_number="WIDGET-001",
    revision="C",
    name="Cost Reduction",
    description="Redesigned for lower manufacturing cost",
    state=ProductState.ACTIVE
)

print(f"Created revision: {new_revision.revision}")
```

### Update Revision

```python
# Get the revision
revision = api.product.get_revision("WIDGET-001", "B")

# Modify
revision.description = "Updated description"
revision.name = "Updated Name"

# Save
updated_revision = api.product.update_revision(revision)
```

### Bulk Create/Update Revisions

```python
from pywats.domains.product import ProductRevision

# Get the product first to get product_id
product = api.product.get_product("WIDGET-001")

# Create multiple revisions
revisions = [
    ProductRevision(
        part_number="WIDGET-001",
        revision="D",
        name="Rev D",
        description="Feature enhancement",
        product_id=product.product_id
    ),
    ProductRevision(
        part_number="WIDGET-001",
        revision="E",
        name="Rev E",
        description="Bug fix",
        product_id=product.product_id
    )
]

# Bulk save
saved_revisions = api.product.bulk_save_revisions(revisions)
print(f"Created {len(saved_revisions)} revisions")
```

---

## Bill of Materials (BOM)

The BOM defines the components and raw materials needed to manufacture a product revision.

### Get BOM

```python
# Get BOM as raw WSBF XML string
bom_xml = api.product.get_bom("WIDGET-001", "A")
if bom_xml:
    print(f"BOM XML length: {len(bom_xml)} characters")

# Get BOM as structured list of items
bom_items = api.product.get_bom_items("WIDGET-001", "A")

print(f"Bill of Materials for WIDGET-001 Rev A:")
for item in bom_items:
    print(f"  {item.part_number} Rev {item.revision}")
    print(f"    Quantity: {item.quantity}")
    print(f"    Reference: {item.reference_designator or 'N/A'}")
    print(f"    Description: {item.description or 'N/A'}")
```

### Update BOM

```python
from pywats.domains.product import BomItem

# Define BOM items
bom_items = [
    BomItem(
        part_number="RESISTOR-10K",
        revision="A",
        quantity=5,
        reference_designator="R1,R2,R3,R4,R5",
        description="10K ohm resistor"
    ),
    BomItem(
        part_number="CAPACITOR-100UF",
        revision="A",
        quantity=2,
        reference_designator="C1,C2",
        description="100uF electrolytic capacitor"
    ),
    BomItem(
        part_number="IC-MICROCONTROLLER",
        revision="B",
        quantity=1,
        reference_designator="U1",
        description="Main microcontroller"
    )
]

# Update the BOM
success = api.product.update_bom(
    part_number="WIDGET-001",
    revision="A",
    bom_items=bom_items,
    description="Updated BOM for cost reduction"
)

if success:
    print("BOM updated successfully")
```

---

## Box Build Templates

⚠️ **INTERNAL API - Subject to change**

Box build templates define PRODUCT-LEVEL relationships - what subunits are REQUIRED to build a product. This is different from production-level assembly (which is in the Production domain).

**Use Cases:**
- Define product structure (parent-child relationships)
- Specify which subassemblies make up a final product
- Track component quantities needed

**Important:** This is a DESIGN-TIME definition. To attach actual physical units during production, use `api.production.add_child_to_assembly()`.

### Get Box Build Template

```python
# Get or create a box build template
template = api.product_internal.get_box_build("MAIN-ASSEMBLY", "A")

print(f"Box Build Template for {template.part_number} Rev {template.revision}")
print(f"Current subunits: {len(template.subunits)}")
```

### Add Subunits to Template

```python
# Get the template
template = api.product_internal.get_box_build("MAIN-ASSEMBLY", "A")

# Add subunits (components that make up this product)
template.add_subunit("PCBA-001", "A", quantity=1)
template.add_subunit("PSU-MODULE", "B", quantity=1)
template.add_subunit("ENCLOSURE", "A", quantity=1)
template.add_subunit("CABLE-ASSY", "C", quantity=3)

# Save changes to server
template.save()
print(f"Template updated with {len(template.subunits)} subunits")
```

### List Template Subunits

```python
template = api.product_internal.get_box_build("MAIN-ASSEMBLY", "A")

print("Required subunits:")
for subunit in template.subunits:
    print(f"  {subunit.child_part_number} Rev {subunit.child_revision}")
    print(f"    Quantity: {subunit.quantity}")
```

### Update Subunit Quantity

```python
template = api.product_internal.get_box_build("MAIN-ASSEMBLY", "A")

# Update quantity for a subunit
template.update_subunit("CABLE-ASSY", "C", quantity=5)  # Changed from 3 to 5

# Save changes
template.save()
```

### Remove Subunit from Template

```python
template = api.product_internal.get_box_build("MAIN-ASSEMBLY", "A")

# Remove a subunit
template.remove_subunit("CABLE-ASSY", "C")

# Save changes
template.save()
```

### Complete Box Build Example

```python
# Define a complete product structure
template = api.product_internal.get_box_build("LAPTOP-X1", "A")

# Add all required components
template.add_subunit("MOTHERBOARD", "A", quantity=1)
template.add_subunit("SCREEN-15INCH", "B", quantity=1)
template.add_subunit("KEYBOARD-US", "A", quantity=1)
template.add_subunit("BATTERY-PACK", "C", quantity=1)
template.add_subunit("RAM-8GB", "A", quantity=2)  # 2 x 8GB modules
template.add_subunit("SSD-512GB", "A", quantity=1)

# Save all at once
template.save()

print(f"Laptop structure defined with {len(template.subunits)} components")
```

---

## Product Groups

Product groups allow you to organize products into logical categories for reporting and filtering.

### List All Product Groups

```python
# Get all product groups
groups = api.product.get_groups()

print("Product Groups:")
for group in groups:
    print(f"  {group.name}: {group.description or 'No description'}")
```

### Filter Product Groups

```python
# Get groups with OData filter
groups = api.product.get_groups(
    filter_str="contains(name,'Electronics')",
    top=10
)
```

### Get Groups for Specific Product

```python
# Get all groups that include this product
groups = api.product.get_groups_for_product("WIDGET-001", "A")

print(f"Product WIDGET-001 Rev A belongs to {len(groups)} groups:")
for group in groups:
    print(f"  - {group.name}")
```

---

## Tags and Metadata

Tags provide key-value metadata storage for products and revisions. Useful for custom attributes, classifications, or integration data.

### Product Tags

```python
# Get all tags for a product
tags = api.product.get_product_tags("WIDGET-001")

print("Product Tags:")
for tag in tags:
    print(f"  {tag['key']}: {tag['value']}")

# Add a single tag
api.product.add_product_tag(
    part_number="WIDGET-001",
    key="ManufacturingLocation",
    value="Factory-A"
)

# Set multiple tags at once (replaces all existing tags)
new_tags = [
    {"key": "Category", "value": "Electronics"},
    {"key": "RoHS", "value": "Compliant"},
    {"key": "LeadTime", "value": "2-weeks"}
]

api.product.set_product_tags("WIDGET-001", new_tags)
```

### Revision Tags

```python
# Get tags for a specific revision
tags = api.product.get_revision_tags("WIDGET-001", "B")

print("Revision Tags:")
for tag in tags:
    print(f"  {tag['key']}: {tag['value']}")

# Add a revision-specific tag
api.product.add_revision_tag(
    part_number="WIDGET-001",
    revision="B",
    key="ECO",
    value="ECO-2024-0542"
)

# Set multiple revision tags
revision_tags = [
    {"key": "ApprovalDate", "value": "2024-06-15"},
    {"key": "ApprovedBy", "value": "J.Smith"}
]

api.product.set_revision_tags("WIDGET-001", "B", revision_tags)
```

---

## Vendors

Manage vendor information for procurement and supply chain tracking.

### List Vendors

```python
# Get all vendors
vendors = api.product.get_vendors()

print("Vendors:")
for vendor in vendors:
    print(f"  {vendor.get('name', 'Unknown')}")
    print(f"    Contact: {vendor.get('contact', 'N/A')}")
    print(f"    Email: {vendor.get('email', 'N/A')}")
```

### Create/Update Vendor

```python
# Create a new vendor
vendor_data = {
    "name": "Acme Components Inc.",
    "contact": "John Doe",
    "email": "sales@acmecomponents.com",
    "phone": "+1-555-0123",
    "address": "123 Industrial Pkwy, Tech City, TC 12345"
}

saved_vendor = api.product.save_vendor(vendor_data)
print(f"Created vendor: {saved_vendor.get('name')}")

# Update existing vendor (include vendor ID)
vendor_data = {
    "vendorId": "existing-vendor-id",
    "name": "Acme Components Inc.",
    "contact": "Jane Smith",  # Updated contact
    "email": "newsales@acmecomponents.com"  # Updated email
}

updated_vendor = api.product.save_vendor(vendor_data)
```

### Delete Vendor

```python
# Delete a vendor
success = api.product.delete_vendor("vendor-id-to-delete")

if success:
    print("Vendor deleted")
```

---

## Product Categories

⚠️ **INTERNAL API - Subject to change**

Categories provide another way to classify products.

### Get Product Categories

```python
# Get all categories
categories = api.product_internal.get_product_categories()

print("Product Categories:")
for category in categories:
    print(f"  {category.get('name', 'Unknown')}")
    print(f"    ID: {category.get('id')}")
```

### Assign Categories to Product

```python
# Set categories for a product (by category IDs)
category_ids = [
    "cat-id-1",
    "cat-id-2",
    "cat-id-3"
]

api.product_internal.set_product_categories("WIDGET-001", category_ids)
print("Categories assigned to product")
```

---

## Advanced Usage

### Complete Product Lifecycle

```python
from pywats.domains.product import ProductState

# 1. Create the product
product = api.product.create_product(
    part_number="NEW-WIDGET",
    name="Next Generation Widget",
    description="Revolutionary new design",
    state=ProductState.ACTIVE
)

# 2. Create initial revision
revision = api.product.create_revision(
    part_number="NEW-WIDGET",
    revision="A",
    name="Prototype",
    description="Initial prototype version",
    state=ProductState.ACTIVE
)

# 3. Define BOM
from pywats.domains.product import BomItem

bom = [
    BomItem(part_number="COMPONENT-1", revision="A", quantity=2),
    BomItem(part_number="COMPONENT-2", revision="B", quantity=1),
]

api.product.update_bom("NEW-WIDGET", "A", bom)

# 4. Add to product group
groups = api.product.get_groups(filter_str="name eq 'New Products'")
# (Groups are managed via WATS UI or separate API)

# 5. Add metadata tags
api.product.add_product_tag("NEW-WIDGET", "Status", "In Development")
api.product.add_revision_tag("NEW-WIDGET", "A", "TestPhase", "Alpha")

print("Product lifecycle setup complete!")
```

### Product Family Management

```python
# Define a product family with common base
base_products = ["WIDGET-BASE", "WIDGET-PLUS", "WIDGET-PRO"]

for pn in base_products:
    # Check if product exists
    existing = api.product.get_product(pn)
    
    if not existing:
        # Create if doesn't exist
        product = api.product.create_product(
            part_number=pn,
            name=f"{pn} Product",
            state=ProductState.ACTIVE
        )
        
        # Create initial revision
        api.product.create_revision(
            part_number=pn,
            revision="A",
            name="Initial Release"
        )
        
        # Tag with family membership
        api.product.add_product_tag(pn, "ProductFamily", "Widget Series")
        
        print(f"Created {pn}")
    else:
        print(f"{pn} already exists")
```

### Migration/Import Helper

```python
def import_products_from_csv(csv_file_path):
    """Import products from CSV file"""
    import csv
    
    products = []
    
    with open(csv_file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            product = api.product.create_product(
                part_number=row['part_number'],
                name=row['name'],
                description=row.get('description', ''),
                state=ProductState.ACTIVE
            )
            
            if product:
                # Create default revision
                api.product.create_revision(
                    part_number=row['part_number'],
                    revision=row.get('revision', 'A'),
                    name=row.get('revision_name', 'Initial')
                )
                
                products.append(product)
    
    return products

# Use it
imported = import_products_from_csv('products.csv')
print(f"Imported {len(imported)} products")
```

---

## API Reference

### ProductService Methods

#### Product Operations
- `get_products()` → `List[ProductView]` - Get all products as simplified views
- `get_products_full()` → `List[Product]` - Get all products with full details
- `get_product(part_number)` → `Optional[Product]` - Get specific product
- `create_product(...)` → `Optional[Product]` - Create new product
- `update_product(product)` → `Optional[Product]` - Update existing product
- `bulk_save_products(products)` → `List[Product]` - Bulk create/update
- `is_active(product)` → `bool` - Check if product is active
- `get_active_products()` → `List[ProductView]` - Get only active products

#### Revision Operations
- `get_revision(part_number, revision)` → `Optional[ProductRevision]` - Get specific revision
- `get_revisions(part_number)` → `List[ProductRevision]` - Get all revisions for product
- `create_revision(...)` → `Optional[ProductRevision]` - Create new revision
- `update_revision(revision)` → `Optional[ProductRevision]` - Update existing revision
- `bulk_save_revisions(revisions)` → `List[ProductRevision]` - Bulk create/update

#### BOM Operations
- `get_bom(part_number, revision)` → `Optional[str]` - Get BOM as WSBF XML
- `get_bom_items(part_number, revision)` → `List[BomItem]` - Get BOM as structured items
- `update_bom(part_number, revision, bom_items, description)` → `bool` - Update BOM

#### Group Operations
- `get_groups(filter_str, top)` → `List[ProductGroup]` - Get product groups
- `get_groups_for_product(part_number, revision)` → `List[ProductGroup]` - Get groups for product

#### Tag Operations
- `get_product_tags(part_number)` → `List[Dict[str, str]]` - Get product tags
- `set_product_tags(part_number, tags)` → `Optional[Product]` - Set product tags
- `add_product_tag(part_number, key, value)` → `Optional[Product]` - Add single tag
- `get_revision_tags(part_number, revision)` → `List[Dict[str, str]]` - Get revision tags
- `set_revision_tags(part_number, revision, tags)` → `Optional[ProductRevision]` - Set revision tags
- `add_revision_tag(part_number, revision, key, value)` → `Optional[ProductRevision]` - Add single tag

#### Vendor Operations
- `get_vendors()` → `List[Dict[str, Any]]` - Get all vendors
- `save_vendor(vendor_data)` → `Optional[Dict[str, Any]]` - Create/update vendor
- `delete_vendor(vendor_id)` → `bool` - Delete vendor

### ProductServiceInternal Methods (⚠️ Subject to change)

#### Box Build Operations
- `get_box_build(part_number, revision)` → `BoxBuildTemplate` - Get/create template
- `get_bom(part_number, revision)` → `List[BomItem]` - Get BOM items
- `set_bom(part_number, revision, bom_items)` → `bool` - Set BOM items

#### Category Operations
- `get_product_categories()` → `List[Dict[str, Any]]` - Get all categories
- `set_product_categories(part_number, category_ids)` → `bool` - Assign categories

### Models

#### Product
- `product_id`: UUID (auto-generated)
- `part_number`: str (required, unique)
- `name`: Optional[str]
- `description`: Optional[str]
- `revision`: Optional[str] (current/default revision)
- `state`: ProductState (ACTIVE/INACTIVE)
- `non_serial`: bool (default False)
- `xml_data`: Optional[str] (custom metadata)
- `created`: Optional[datetime]
- `modified`: Optional[datetime]

#### ProductRevision
- `product_revision_id`: UUID (auto-generated)
- `product_id`: UUID (links to Product)
- `part_number`: str
- `revision`: str (required)
- `name`: Optional[str]
- `description`: Optional[str]
- `state`: ProductState
- `effective_date`: Optional[datetime]
- `xml_data`: Optional[str]
- `created`: Optional[datetime]
- `modified`: Optional[datetime]

#### BomItem
- `part_number`: str
- `revision`: str
- `quantity`: int
- `reference_designator`: Optional[str]
- `description`: Optional[str]

#### ProductView
- `part_number`: str
- `name`: Optional[str]
- `non_serial`: Optional[bool]
- `state`: Optional[ProductState]

#### ProductGroup
- `product_group_id`: UUID
- `name`: str
- `description`: Optional[str]

---

## Best Practices

1. **Always create a revision** - Even for the first version, create revision "A" or "1.0"

2. **Use meaningful part numbers** - Use a consistent naming scheme (e.g., "WIDGET-001", "PCB-MAIN-V2")

3. **Set product state** - Mark obsolete products as INACTIVE rather than deleting them

4. **Use tags for custom attributes** - Instead of modifying the database schema, use tags

5. **Bulk operations for efficiency** - When importing or updating many products, use bulk methods

6. **BOM accuracy** - Keep BOMs up-to-date as product revisions change

7. **Box Build vs BOM** - Use BOM for component lists, Box Build for structural relationships

8. **Document revisions** - Always include meaningful descriptions when creating revisions

9. **Non-serial products** - Mark consumables, bulk items, or non-tracked items as `non_serial=True`

10. **Version control** - Use revision tags to track ECOs, approval dates, and change history

---

## Common Workflows

### New Product Introduction (NPI)

```python
# 1. Create product definition
product = api.product.create_product(
    part_number="NEW-PRODUCT",
    name="New Product Name",
    description="Product description"
)

# 2. Create engineering sample revision
api.product.create_revision(
    part_number="NEW-PRODUCT",
    revision="ES",
    name="Engineering Sample",
    description="Pre-production samples"
)

# 3. Tag as NPI
api.product.add_product_tag("NEW-PRODUCT", "Phase", "NPI")
api.product.add_revision_tag("NEW-PRODUCT", "ES", "Status", "Engineering Validation")

# 4. When ready for production, create production revision
production_rev = api.product.create_revision(
    part_number="NEW-PRODUCT",
    revision="A",
    name="Production Release",
    description="First production version"
)

# 5. Update tags
api.product.add_product_tag("NEW-PRODUCT", "Phase", "Production")
api.product.add_revision_tag("NEW-PRODUCT", "A", "Status", "Released")
```

### Product Obsolescence

```python
# Mark product as inactive (don't delete - preserve history)
product = api.product.get_product("OLD-WIDGET")
product.state = ProductState.INACTIVE
api.product.update_product(product)

# Tag with obsolescence info
api.product.add_product_tag("OLD-WIDGET", "Obsolete", "true")
api.product.add_product_tag("OLD-WIDGET", "ObsoleteDate", "2024-12-31")
api.product.add_product_tag("OLD-WIDGET", "Replacement", "NEW-WIDGET")
```

---

## Troubleshooting

### Product not found
```python
product = api.product.get_product("WIDGET-001")
if not product:
    print("Product doesn't exist - create it first")
```

### Revision creation fails
```python
# Make sure the product exists first
product = api.product.get_product("WIDGET-001")
if not product:
    print("Create the product before creating revisions")
else:
    revision = api.product.create_revision("WIDGET-001", "A", ...)
```

### BOM update fails
```python
# Ensure the product revision exists
revision = api.product.get_revision("WIDGET-001", "A")
if not revision:
    print("Create the product revision first")
else:
    api.product.update_bom("WIDGET-001", "A", bom_items)
```

---

## See Also

- [Production Domain](PRODUCTION.md) - Managing units in production
- [Report Domain](REPORT.md) - Querying test results
- [Asset Domain](ASSET.md) - Managing test equipment and tools
