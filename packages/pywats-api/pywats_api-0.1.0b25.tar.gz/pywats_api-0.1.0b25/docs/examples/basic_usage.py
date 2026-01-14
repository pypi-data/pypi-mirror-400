"""
PyWATS Basic Usage Example

This example demonstrates basic usage of the PyWATS library for interacting 
with the WATS API.

Setup:
    Set environment variables before running:
    - WATS_BASE_URL: Your WATS server URL (e.g., https://your-server.wats.com)
    - WATS_AUTH_TOKEN: Your base64-encoded authentication token
    
    Or modify the credentials below directly.
    
    Run: python basic_usage.py
"""

import os

from pywats import pyWATS, WATSFilter


def main():
    # Initialize the API
    # Option 1: Use environment variables
    base_url = os.getenv("WATS_BASE_URL")
    token = os.getenv("WATS_AUTH_TOKEN")
    
    # Option 2: Or set credentials directly (for testing)
    # base_url = "https://your-server.wats.com"
    # token = "your_base64_encoded_token"
    
    if not base_url or not token:
        print("Error: Please set WATS_BASE_URL and WATS_AUTH_TOKEN environment variables")
        print("  Or modify the credentials in this script directly")
        return
    
    api = pyWATS(base_url=base_url, token=token)

    print("PyWATS Basic Usage Example")
    print("=" * 50)

    # =========================================================================
    # Test Connection
    # =========================================================================

    print("\n1. Testing Connection...")
    if api.test_connection():
        print("   ✓ Connection successful!")
        version = api.get_version()
        print(f"   Server version: {version}")
    else:
        print("   ✗ Connection failed!")
        return

    # =========================================================================
    # Product Operations
    # =========================================================================

    print("\n2. Product Operations")
    print("-" * 50)

    # Get all products
    print("   Getting all products...")
    products = api.product.get_products()
    print(f"   Found {len(products)} products")

    if products:
        for p in products[:3]:
            print(f"   - {p.part_number}: {p.name}")

    # =========================================================================
    # Asset Operations
    # =========================================================================

    print("\n3. Asset Operations")
    print("-" * 50)

    # Get asset types
    print("   Getting asset types...")
    asset_types = api.asset.get_asset_types()
    print(f"   Found {len(asset_types)} asset types")

    for at in asset_types[:3]:
        print(f"   - {at.type_name}")


    # =========================================================================
    # Report Operations
    # =========================================================================

    print("\n4. Report Operations")
    print("-" * 50)

    # Query recent UUT report headers
    print("   Querying recent UUT reports...")
    filter = WATSFilter(top_count=10)
    headers = api.report.query_uut_headers(filter)
    print(f"   Found {len(headers)} report headers")

    if headers:
        for h in headers[:3]:
            print(f"   - {h.serial_number} | {h.part_number} | {h.status}")


    



    # =========================================================================
    # App Statistics
    # =========================================================================

    print("\n5. Statistics Operations")
    print("-" * 50)

    # Get processes
    print("   Getting processes...")
    processes = api.analytics.get_processes()
    print(f"   Found {len(processes)} processes")

    for p in processes[:5]:
        print(f"   - [{p.process_code}] {p.process_name}")

    print("\n" + "=" * 50)
    print("Example completed successfully!")


if __name__ == "__main__":
    main()
