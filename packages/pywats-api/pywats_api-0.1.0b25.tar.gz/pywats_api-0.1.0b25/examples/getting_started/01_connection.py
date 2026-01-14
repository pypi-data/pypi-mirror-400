"""
Getting Started: Basic Connection

This example shows how to establish a connection to a WATS server.
"""
from pywats import pyWATS

# =============================================================================
# Basic Connection
# =============================================================================

# The simplest way to connect - provide URL and API token
api = pyWATS(
    base_url="https://your-wats-server.com",
    token="your-api-token"
)

# The token is typically a Base64-encoded "username:password" string
# You can generate it like this:
import base64
username = "your-username"
password = "your-password"
token = base64.b64encode(f"{username}:{password}".encode()).decode()

api = pyWATS(
    base_url="https://your-wats-server.com",
    token=token
)


# =============================================================================
# Connection with Options
# =============================================================================

from pywats.core import ErrorMode

# Connection with custom timeout and error handling
api = pyWATS(
    base_url="https://your-wats-server.com",
    token="your-api-token",
    timeout=60,  # 60 second timeout (default is 30)
    error_mode=ErrorMode.STRICT  # Raise exceptions on errors (default)
)

# Lenient mode - returns None instead of raising exceptions
api = pyWATS(
    base_url="https://your-wats-server.com",
    token="your-api-token",
    error_mode=ErrorMode.LENIENT
)


# =============================================================================
# Verify Connection
# =============================================================================

# Check connection by getting the server version
version = api.analytics.get_version()
print(f"Connected to WATS server version: {version}")

# Or try to get some data
try:
    products = api.product.get_products()
    print(f"Connection successful! Found {len(products)} products.")
except Exception as e:
    print(f"Connection failed: {e}")


# =============================================================================
# Environment Variables (Recommended for Production)
# =============================================================================

import os

api = pyWATS(
    base_url=os.environ.get("WATS_BASE_URL", "https://demo.wats.com"),
    token=os.environ.get("WATS_TOKEN", "")
)

# Set environment variables before running:
# Windows: set WATS_BASE_URL=https://your-server.com
# Linux/Mac: export WATS_BASE_URL=https://your-server.com
