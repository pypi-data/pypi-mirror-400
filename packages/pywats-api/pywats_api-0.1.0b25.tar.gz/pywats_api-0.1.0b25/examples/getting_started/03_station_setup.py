"""
Getting Started: Station Configuration

This example shows how to configure test station identity.
"""
import os
from pywats import pyWATS
from pywats.core import Station

# =============================================================================
# Single Station Mode (Most Common)
# =============================================================================

# Define your test station
station = Station(
    name="TEST-STATION-01",       # Machine name (appears in reports)
    location="Lab A, Building 1",  # Physical location
    purpose="Production"           # Purpose: Production, Development, etc.
)

# Create API with station
api = pyWATS(
    base_url="https://your-wats-server.com",
    token="your-api-token",
    station=station
)

# The station name will automatically be included in submitted reports
print(f"Station configured: {api.station.name}")


# =============================================================================
# Station Without Location (Minimal)
# =============================================================================

station = Station(name="STATION-01")

api = pyWATS(
    base_url="https://your-wats-server.com",
    token="your-api-token",
    station=station
)


# =============================================================================
# Multi-Station Mode (Hub Configuration)
# =============================================================================

# For systems that manage multiple stations (e.g., a test hub)
api = pyWATS(
    base_url="https://your-wats-server.com",
    token="your-api-token"
)

# Register multiple stations
api.stations.add("line1", Station("PROD-LINE-1", "Building A", "Production"))
api.stations.add("line2", Station("PROD-LINE-2", "Building A", "Production"))
api.stations.add("dev", Station("DEV-STATION", "Lab", "Development"))

# Set active station
api.stations.set_active("line1")
print(f"Active station: {api.station.name}")

# Switch stations as needed
api.stations.set_active("line2")
print(f"Active station: {api.station.name}")


# =============================================================================
# Station from Environment
# =============================================================================

station_name = os.environ.get("WATS_STATION_NAME", "DEFAULT-STATION")
station_location = os.environ.get("WATS_STATION_LOCATION", "Unknown")

station = Station(
    name=station_name,
    location=station_location,
    purpose="Production"
)

api = pyWATS(
    base_url=os.environ.get("WATS_BASE_URL", "https://demo.wats.com"),
    token=os.environ.get("WATS_TOKEN", ""),
    station=station
)
