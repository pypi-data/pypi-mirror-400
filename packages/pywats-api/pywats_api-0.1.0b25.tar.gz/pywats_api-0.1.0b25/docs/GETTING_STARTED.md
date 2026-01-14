# Getting Started Guide

Complete guide to installing, configuring, and initializing pyWATS.

## Table of Contents

- [Installation](#installation)
- [API Initialization](#api-initialization)
- [Authentication](#authentication)
- [Logging Configuration](#logging-configuration)
- [Exception Handling](#exception-handling)
- [Client Installation](#client-installation)

---

## Installation

### Library Only (API Access)

For Python scripts and applications using the WATS API:

```bash
pip install pywats-api
```

### With GUI Client

For desktop applications with Qt-based GUI (Windows, macOS, Linux):

```bash
pip install pywats-api[client]
```

### Headless Client

For servers, Raspberry Pi, and embedded systems (no Qt/GUI):

```bash
pip install pywats-api[client-headless]
```

### With MCP Server

For AI assistant integration:

```bash
pip install pywats-api[mcp]
```

### Development Installation

From source for development:

```bash
git clone https://github.com/olreppe/pyWATS.git
cd pyWATS
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
pip install -e ".[dev]"
```

---

## API Initialization

### Basic Initialization

```python
from pywats import pyWATS

# Initialize with credentials
api = pyWATS(
    base_url="https://your-wats-server.com",
    token="your_base64_token"  # Base64 of "username:password"
)

# Test connection
if api.test_connection():
    print(f"Connected! Server version: {api.get_version()}")
```

### Using Environment Variables

```python
import os
from pywats import pyWATS

# Set environment variables
os.environ['WATS_BASE_URL'] = 'https://your-wats-server.com'
os.environ['WATS_AUTH_TOKEN'] = 'your_base64_token'

# Initialize from environment
api = pyWATS()  # Automatically reads from environment
```

Or create a `.env` file:

```env
WATS_BASE_URL=https://your-wats-server.com
WATS_AUTH_TOKEN=your_base64_token
```

```python
from dotenv import load_dotenv
from pywats import pyWATS

load_dotenv()  # Load from .env file
api = pyWATS()
```

### Configuration Options

```python
from pywats import pyWATS
from pywats.core.exceptions import ErrorMode

api = pyWATS(
    base_url="https://your-wats-server.com",
    token="your_token",
    
    # Optional: Custom timeout (default: 30 seconds)
    timeout=60,
    
    # Optional: Process cache refresh interval (default: 300 seconds)
    process_refresh_interval=600,
    
    # Optional: Error handling mode (default: STRICT)
    error_mode=ErrorMode.STRICT  # or ErrorMode.LENIENT
)
```

### Error Handling Modes

The library supports two error handling modes that control how missing data and 404 responses are handled:

#### STRICT Mode (Default - Recommended for Production)

```python
from pywats import pyWATS
from pywats.core.exceptions import ErrorMode

api = pyWATS(
    base_url="https://your-wats-server.com",
    token="your_token",
    error_mode=ErrorMode.STRICT  # Default, can be omitted
)
```

**Behavior:**
- **404 errors** → Raises `NotFoundError`
- **Empty responses** (200 with no data) → Raises `EmptyResponseError`
- **All 4xx/5xx errors** → Raises appropriate exception
- **If no exception** → You have valid data (guaranteed)

**Use STRICT when:**
- Writing production code that needs certainty
- Validating data existence
- Critical operations where failures must be explicit
- You want type safety (no None checks needed)

**Example:**
```python
from pywats import NotFoundError

try:
    product = api.product.get_product("WIDGET-001")
    # If we reach here, product is DEFINITELY valid
    print(f"Found: {product.part_number}")
except NotFoundError:
    print("Product doesn't exist - handle explicitly")
```

#### LENIENT Mode (Recommended for Scripts/Exploration)

```python
from pywats import pyWATS
from pywats.core.exceptions import ErrorMode

api = pyWATS(
    base_url="https://your-wats-server.com",
    token="your_token",
    error_mode=ErrorMode.LENIENT
)
```

**Behavior:**
- **404 errors** → Returns `None` (no exception)
- **Empty responses** → Returns `None` (no exception)
- **Actual errors** (5xx, 400, 401, 403, 409) → Still raises exceptions
- **Must check for None** before using returned data

**Use LENIENT when:**
- Writing exploratory scripts
- Querying optional data
- Batch processing where some items may not exist
- You want simpler code with less try/except boilerplate

**Example:**
```python
# Simpler code - no try/except needed for missing data
product = api.product.get_product("WIDGET-001")

if product is None:
    print("Product doesn't exist")
else:
    print(f"Found: {product.part_number}")
```

#### Mode Comparison

| Aspect | STRICT Mode | LENIENT Mode |
|--------|-------------|--------------|
| **404 Response** | Raises `NotFoundError` | Returns `None` |
| **Empty Response** | Raises `EmptyResponseError` | Returns `None` |
| **Server Error (5xx)** | Raises `ServerError` | Raises `ServerError` |
| **Validation Error (400)** | Raises `ValidationError` | Raises `ValidationError` |
| **Auth Error (401)** | Raises `AuthenticationError` | Raises `AuthenticationError` |
| **Permission Error (403)** | Raises `AuthorizationError` | Raises `AuthorizationError` |
| **Conflict (409)** | Raises `ConflictError` | Raises `ConflictError` |
| **Return Type** | `Model` or raises | `Model | None` |
| **None Checks** | Not needed | Required |
| **Best For** | Production code | Scripts/exploration |

#### Choosing the Right Mode

```python
# Production code - use STRICT for explicit error handling
from pywats.core.exceptions import ErrorMode

api_prod = pyWATS(..., error_mode=ErrorMode.STRICT)

try:
    product = api_prod.product.get_product(part_number)
    # Guaranteed to have valid product here
    process_product(product)
except NotFoundError as e:
    log_error(f"Product not found: {e}")
    send_alert(...)
except ValidationError as e:
    log_error(f"Invalid data: {e}")

# Exploratory script - use LENIENT for simpler code
api_explore = pyWATS(..., error_mode=ErrorMode.LENIENT)

for part_number in candidate_parts:
    product = api_explore.product.get_product(part_number)
    if product:  # Simple None check
        print(f"Found: {product.part_number}")
    # Missing products are silently skipped
```

### Station Configuration

Configure test station identity:

```python
from pywats import pyWATS, Station, StationConfig, Purpose

# Configure station
station = Station(
    config=StationConfig(
        station_name="ICT-01",
        location="Production Line A"
    )
)

# Initialize with station
api = pyWATS(
    base_url="https://your-wats-server.com",
    token="your_token",
    station=station
)

# Station is automatically used in reports
from pywats.tools.test_uut import TestUUT

uut = TestUUT(
    part_number="WIDGET-001",
    serial_number="SN-12345",
    revision="A",
    operator="John Doe",
    purpose=Purpose.TEST  # or 10
)
# Station info automatically filled from api.station
```

---

## Authentication

### Token Generation

pyWATS uses Base64-encoded credentials:

```python
import base64

username = "your_username"
password = "your_password"

# Create token
credentials = f"{username}:{password}"
token = base64.b64encode(credentials.encode()).decode()

print(f"Token: {token}")
```

### Using in API

```python
from pywats import pyWATS

api = pyWATS(
    base_url="https://your-wats-server.com",
    token=token  # Use generated token
)
```

### Token Security

**Best Practices:**

1. **Never hardcode credentials** in source code
2. **Use environment variables** for production
3. **Use .env files** for development (add to .gitignore)
4. **Rotate tokens** regularly
5. **Use separate tokens** for different environments

```python
# ❌ DON'T DO THIS
api = pyWATS(base_url="https://...", token="dXNlcjpwYXNz")

# ✅ DO THIS
import os
api = pyWATS(
    base_url=os.getenv('WATS_BASE_URL'),
    token=os.getenv('WATS_AUTH_TOKEN')
)
```

---

## Logging Configuration

### Quick Debug Mode

Enable detailed logging for troubleshooting:

```python
from pywats import pyWATS, enable_debug_logging

# Enable debug logging before creating API instance
enable_debug_logging()

api = pyWATS(base_url="...", token="...")
```

This shows:
- HTTP requests and responses
- API calls to WATS server
- Data serialization/deserialization
- Repository and service operations

### Custom Logging Configuration

```python
import logging
from pywats import pyWATS

# Configure logging your way
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pywats.log'),
        logging.StreamHandler()
    ]
)

# Set pyWATS logger to DEBUG
logging.getLogger('pywats').setLevel(logging.DEBUG)

# Or be more specific
logging.getLogger('pywats.http_client').setLevel(logging.DEBUG)
logging.getLogger('pywats.domains.product').setLevel(logging.INFO)

api = pyWATS(base_url="...", token="...")
```

### Log Levels

| Level | Use Case | Output |
|-------|----------|--------|
| DEBUG | Development, troubleshooting | All details including HTTP requests |
| INFO | Normal operation | Important operations and status |
| WARNING | Production monitoring | Warnings and potential issues |
| ERROR | Minimal logging | Errors only |

### Example Log Output

```
2026-01-08 14:30:15 - pywats.http_client - INFO - GET https://wats.example.com/api/Product/1234
2026-01-08 14:30:15 - pywats.http_client - DEBUG - Response: 200 OK (1234 bytes)
2026-01-08 14:30:15 - pywats.domains.product - DEBUG - Retrieved product: WIDGET-001
```

### Disable Logging

```python
import logging

# Disable all pyWATS logging
logging.getLogger('pywats').setLevel(logging.CRITICAL)
```

---

## Exception Handling

### Exception Hierarchy

pyWATS provides a comprehensive exception hierarchy for precise error handling:

```
PyWATSError                      # Base exception for all pyWATS errors
├── AuthenticationError          # Authentication failed (401)
├── AuthorizationError           # Permission denied (403)
├── NotFoundError                # Resource not found (404)
├── ValidationError              # Invalid request data (400)
├── ConflictError                # Resource conflict (409)
├── EmptyResponseError           # Empty response in STRICT mode (200 with no data)
├── ServerError                  # Server-side error (5xx)
├── ConnectionError              # Network/connection failure
└── TimeoutError                 # Request timeout
```

All exceptions include:
- **message**: Human-readable error description
- **operation**: Name of the operation that failed (e.g., "get_product")
- **details**: Additional context without HTTP internals
- **cause**: Original exception if wrapping another error

### Basic Error Handling

```python
from pywats import pyWATS, PyWATSError, AuthenticationError

try:
    api = pyWATS(base_url="https://...", token="...")
    product = api.product.get_product("WIDGET-001")
    
except AuthenticationError:
    print("Invalid credentials - check your token")
    
except PyWATSError as e:
    print(f"WATS API error: {e}")
    print(f"Operation: {e.operation}")
    print(f"Details: {e.details}")
    
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Comprehensive Exception Handling

```python
from pywats import (
    pyWATS, 
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ValidationError,
    ConflictError,
    EmptyResponseError,
    ServerError,
    ConnectionError,
    TimeoutError,
    PyWATSError
)

try:
    api = pyWATS(base_url="https://...", token="...")
    product = api.product.get_product("WIDGET-001")
    
except AuthenticationError as e:
    # 401 - Invalid credentials
    print(f"Authentication failed: {e.message}")
    # Action: Verify token, re-authenticate
    
except AuthorizationError as e:
    # 403 - No permission
    print(f"Permission denied: {e.message}")
    # Action: Check user permissions, request access
    
except NotFoundError as e:
    # 404 - Resource doesn't exist (STRICT mode only)
    print(f"Not found: {e.resource_type} '{e.identifier}'")
    # Action: Verify identifier, create resource
    
except ValidationError as e:
    # 400 - Invalid request data
    print(f"Validation error: {e.message}")
    if e.field:
        print(f"  Field: {e.field}")
    if e.value:
        print(f"  Value: {e.value}")
    # Action: Fix input data, check API documentation
    
except ConflictError as e:
    # 409 - Resource conflict
    print(f"Conflict: {e.message}")
    # Action: Resolve conflict, retry with updated data
    
except EmptyResponseError as e:
    # 200 with empty body (STRICT mode only)
    print(f"Empty response: {e.message}")
    # Action: Verify query parameters, switch to LENIENT mode
    
except ServerError as e:
    # 5xx - Server-side error
    print(f"Server error: {e.message}")
    if e.status_code:
        print(f"  Status: {e.status_code}")
    # Action: Retry, contact support if persistent
    
except ConnectionError as e:
    # Network failure
    print(f"Connection failed: {e.message}")
    # Action: Check network, verify URL
    
except TimeoutError as e:
    # Request timeout
    print(f"Request timed out: {e.message}")
    # Action: Increase timeout, check network
    
except PyWATSError as e:
    # Catch-all for other errors
    print(f"WATS error: {e.message}")
    print(f"Operation: {e.operation}")
    print(f"Details: {e.details}")
```

### Error Mode Impact on Exceptions

The `error_mode` parameter affects which exceptions are raised:

```python
from pywats import pyWATS, NotFoundError, EmptyResponseError
from pywats.core.exceptions import ErrorMode

# STRICT mode - raises exceptions for missing data
api_strict = pyWATS(..., error_mode=ErrorMode.STRICT)

try:
    product = api_strict.product.get_product("UNKNOWN")
except NotFoundError:
    # This WILL be raised in STRICT mode
    print("Product not found")

try:
    product = api_strict.product.get_product("EMPTY-RESULT")
except EmptyResponseError:
    # This WILL be raised in STRICT mode
    print("Query returned no data")

# LENIENT mode - returns None for missing data
api_lenient = pyWATS(..., error_mode=ErrorMode.LENIENT)

product = api_lenient.product.get_product("UNKNOWN")
# Returns None - no NotFoundError raised

if product is None:
    print("Product not found or empty")
```

**Exception Matrix by Mode:**

| Error Type | STRICT Mode | LENIENT Mode |
|------------|-------------|--------------|
| 404 Not Found | Raises `NotFoundError` | Returns `None` |
| Empty Response | Raises `EmptyResponseError` | Returns `None` |
| 400 Validation | Raises `ValidationError` | Raises `ValidationError` |
| 401 Auth | Raises `AuthenticationError` | Raises `AuthenticationError` |
| 403 Permission | Raises `AuthorizationError` | Raises `AuthorizationError` |
| 409 Conflict | Raises `ConflictError` | Raises `ConflictError` |
| 5xx Server Error | Raises `ServerError` | Raises `ServerError` |
| Network Failure | Raises `ConnectionError` | Raises `ConnectionError` |
| Timeout | Raises `TimeoutError` | Raises `TimeoutError` |
```

### Retry Logic

```python
import time
from pywats import pyWATS, ConnectionError, ServerError

def get_product_with_retry(api, part_number, max_retries=3):
    """Get product with automatic retry on network errors"""
    
    for attempt in range(max_retries):
        try:
            return api.product.get_product(part_number)
            
        except (ConnectionError, ServerError) as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Retry {attempt + 1}/{max_retries} after {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise  # Re-raise on final attempt
    
    return None

# Use it
try:
    product = get_product_with_retry(api, "WIDGET-001")
except PyWATSError as e:
    print(f"Failed after retries: {e}")
```

### Validation Errors

```python
from pywats import ValidationError
from pywats.tools.test_uut import TestUUT

try:
    # Invalid data
    uut = TestUUT(
        part_number="",  # Empty part number - will raise ValidationError
        serial_number="SN-12345",
        revision="A"
    )
    
except ValidationError as e:
    print(f"Validation failed: {e}")
    # Handle gracefully - prompt user, use defaults, etc.
```

---

## Client Installation

### GUI Client (Desktop)

#### Prerequisites

- Python 3.10 or later
- Qt6 support (Windows, macOS, Linux with display)

#### Installation

```bash
# Install with client support
pip install pywats-api[client]

# Launch GUI
python -m pywats_client
```

Or from command line:

```bash
pywats-client
```

#### First-Time Setup

1. Launch the client
2. Go to **Setup** tab
3. Configure:
   - Server URL: `https://your-wats-server.com`
   - API Token: Your Base64 token
   - Station Name: `YOUR-STATION-01`
4. Click **Save**
5. Click **Test Connection**

See **[GUI Configuration Guide](../src/pywats_client/GUI_CONFIGURATION.md)** for detailed setup.

---

### Headless Client (No GUI)

For servers, Raspberry Pi, and embedded systems.

#### Installation

```bash
# Install headless client (no Qt)
pip install pywats-api[client-headless]
```

#### Initialize Configuration

```bash
# Interactive setup
pywats-client config init

# Or non-interactive
pywats-client config init \
    --server-url https://wats.example.com \
    --api-token YOUR_TOKEN \
    --station-name RASPBERRY-PI-01 \
    --non-interactive
```

#### Test Connection

```bash
pywats-client test-connection
```

#### Start Service

```bash
# Foreground (for testing)
pywats-client start

# With HTTP API for remote management
pywats-client start --api --api-port 8765

# As daemon (Linux/Unix)
pywats-client start --daemon
```

#### Configuration File

Location:
- **Windows:** `%APPDATA%\pyWATS_Client\config.json`
- **Linux/Mac:** `~/.config/pywats_client/config.json`

Example:

```json
{
  "service_address": "https://wats.example.com",
  "api_token": "your_token",
  "station_name": "RASPBERRY-PI-01",
  "log_level": "INFO"
}
```

#### CLI Commands

```bash
# Configuration
pywats-client config show
pywats-client config get station_name
pywats-client config set log_level DEBUG

# Service control
pywats-client status
pywats-client start
pywats-client stop

# Converters
pywats-client converters list
pywats-client converters enable my_converter
```

See **[Headless Operation Guide](../src/pywats_client/control/HEADLESS_GUIDE.md)** for complete documentation.

---

## Complete Example

Putting it all together:

```python
"""
Complete example of pyWATS initialization with logging and error handling
"""

import os
import logging
from dotenv import load_dotenv
from pywats import (
    pyWATS,
    enable_debug_logging,
    PyWATSError,
    AuthenticationError,
    Station,
    StationConfig,
    Purpose
)

def initialize_api():
    """Initialize pyWATS API with proper configuration"""
    
    # Load environment variables
    load_dotenv()
    
    # Enable debug logging if in debug mode
    if os.getenv('DEBUG', 'false').lower() == 'true':
        enable_debug_logging()
    else:
        # Configure INFO level logging
        logging.basicConfig(level=logging.INFO)
    
    # Get credentials from environment
    base_url = os.getenv('WATS_BASE_URL')
    token = os.getenv('WATS_AUTH_TOKEN')
    
    if not base_url or not token:
        raise ValueError("WATS_BASE_URL and WATS_AUTH_TOKEN must be set")
    
    # Configure station
    station = Station(
        config=StationConfig(
            station_name=os.getenv('WATS_STATION_NAME', 'DEFAULT-STATION'),
            location=os.getenv('WATS_LOCATION', 'Default Location')
        )
    )
    
    # Initialize API
    try:
        api = pyWATS(
            base_url=base_url,
            token=token,
            station=station,
            timeout=int(os.getenv('WATS_TIMEOUT', '30'))
        )
        
        # Test connection
        if api.test_connection():
            version = api.get_version()
            logging.info(f"Connected to WATS server version: {version}")
            return api
        else:
            raise ConnectionError("Connection test failed")
            
    except AuthenticationError:
        logging.error("Authentication failed - check credentials")
        raise
        
    except PyWATSError as e:
        logging.error(f"Failed to initialize WATS API: {e}")
        raise

# Use it
if __name__ == "__main__":
    try:
        api = initialize_api()
        
        # Now use the API
        products = api.product.get_products()
        print(f"Found {len(products)} products")
        
    except Exception as e:
        logging.exception("Application error")
        exit(1)
```

---

## See Also

- [Domain Guides](INDEX.md) - API documentation for each domain
- [GUI Configuration](../src/pywats_client/GUI_CONFIGURATION.md) - GUI client setup
- [Headless Operation](../src/pywats_client/control/HEADLESS_GUIDE.md) - Headless client setup
- [Examples](../examples/) - Working code examples
