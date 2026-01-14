"""
Demonstration of pyWATS logging capabilities.

This script shows how to:
1. Use pyWATS with default (quiet) logging
2. Enable debug logging for troubleshooting
3. Configure custom logging formats
"""

import logging
from pywats import pyWATS, enable_debug_logging


def demo_default_logging():
    """By default, pyWATS is quiet - no console output."""
    print("=== Demo 1: Default Behavior (Quiet) ===")
    print("pyWATS uses logging but doesn't configure handlers.")
    print("This means no console output by default.\n")
    
    # Note: This would normally connect to a real server
    # api = pyWATS(base_url="https://your-server.com", token="your-token")
    # products = api.product.get_products()
    print("✓ Library code runs silently\n")


def demo_debug_logging():
    """Enable debug logging for troubleshooting."""
    print("=== Demo 2: Debug Mode ===")
    print("Enable debug logging with enable_debug_logging()\n")
    
    # Enable debug logging
    enable_debug_logging()
    
    print("Now you would see detailed logs:")
    print("  2025-12-12 10:30:45 - pywats.http_client - INFO - Initializing HttpClient: https://...")
    print("  2025-12-12 10:30:45 - pywats.http_client - DEBUG - Timeout: 30s, SSL verify: True")
    print("  2025-12-12 10:30:45 - pywats.http_client - DEBUG - GET https://.../api/Product")
    print("  2025-12-12 10:30:46 - pywats.http_client - DEBUG - Response: 200 (1523 bytes)")
    print()


def demo_custom_logging():
    """Configure custom logging for production use."""
    print("=== Demo 3: Custom Logging Configuration ===")
    print("For production, configure logging properly:\n")
    
    # Custom logging configuration
    logging.basicConfig(
        level=logging.INFO,
        format='[%(levelname)s] %(name)s - %(message)s',
        handlers=[
            logging.FileHandler('pywats.log'),
            logging.StreamHandler()
        ]
    )
    
    # Control pyWATS logging level separately
    logging.getLogger('pywats').setLevel(logging.WARNING)
    
    print("✓ Configured file + console logging")
    print("✓ Set pyWATS to WARNING level (only important messages)")
    print("✓ Your app logs at INFO level\n")


def demo_per_module_control():
    """Control logging for specific pyWATS modules."""
    print("=== Demo 4: Per-Module Control ===")
    print("Control logging for specific parts of pyWATS:\n")
    
    # Enable INFO for most modules
    logging.getLogger('pywats').setLevel(logging.INFO)
    
    # But DEBUG for HTTP client (to see network traffic)
    logging.getLogger('pywats.http_client').setLevel(logging.DEBUG)
    
    # Disable logging for specific domains
    logging.getLogger('pywats.domains.product').setLevel(logging.WARNING)
    
    print("✓ Main: INFO level")
    print("✓ HTTP Client: DEBUG level (see all requests)")
    print("✓ Product domain: WARNING level (quiet)")
    print()


if __name__ == "__main__":
    print("pyWATS Logging Demonstration")
    print("=" * 50)
    print()
    
    demo_default_logging()
    demo_debug_logging()
    demo_custom_logging()
    demo_per_module_control()
    
    print("=" * 50)
    print("Summary:")
    print("- Library is quiet by default (good for libraries)")
    print("- Use enable_debug_logging() for quick debugging")
    print("- Configure properly for production use")
    print("- Control individual module logging levels")
