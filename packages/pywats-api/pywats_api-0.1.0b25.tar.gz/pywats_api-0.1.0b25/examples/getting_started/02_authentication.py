"""
Getting Started: Authentication

This example shows different authentication methods for WATS.
"""
import base64
import os
from pywats import pyWATS

# =============================================================================
# Token Authentication (Recommended)
# =============================================================================

# WATS uses Basic authentication with a Base64-encoded token
# The token format is: base64("username:password")

# Option 1: Pre-encoded token (from WATS admin or environment)
api = pyWATS(
    base_url="https://your-wats-server.com",
    token="dXNlcm5hbWU6cGFzc3dvcmQ="  # Pre-encoded token
)

# Option 2: Encode credentials at runtime
username = "your-username"
password = "your-password"
token = base64.b64encode(f"{username}:{password}".encode()).decode()

api = pyWATS(
    base_url="https://your-wats-server.com",
    token=token
)


# =============================================================================
# Environment-Based Authentication (Production Best Practice)
# =============================================================================

# Never hardcode credentials in source code!
# Use environment variables instead.

api = pyWATS(
    base_url=os.environ.get("WATS_BASE_URL", "https://demo.wats.com"),
    token=os.environ.get("WATS_TOKEN", "")
)


# =============================================================================
# Helper Function for Credential Encoding
# =============================================================================

def create_wats_token(username: str, password: str) -> str:
    """Create a WATS API token from username and password."""
    credentials = f"{username}:{password}"
    return base64.b64encode(credentials.encode()).decode()


# Usage:
token = create_wats_token("myuser", "mypassword")
api = pyWATS(base_url="https://your-wats-server.com", token=token)


# =============================================================================
# Verify Authentication
# =============================================================================

# Test that authentication works
try:
    version = api.analytics.get_version()
    print(f"✓ Authentication successful (server version: {version})")
except Exception as e:
    print(f"✗ Authentication failed: {e}")
