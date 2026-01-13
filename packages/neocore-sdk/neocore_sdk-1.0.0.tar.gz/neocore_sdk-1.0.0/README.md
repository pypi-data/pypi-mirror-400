# NeoCore Security SDK

**Official Python client SDK for NeoCore API authentication using Ed25519 digital signatures.**

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)
## 🔐 Overview

This SDK provides **banking-grade security** for NeoCore API authentication using Ed25519 asymmetric cryptography. All requests are automatically signed with your private key, and the server verifies signatures using your registered public key.

### Key Features

- ✅ **Ed25519 Digital Signatures** - Industry-standard asymmetric cryptography
- ✅ **Automatic Request Signing** - Zero-configuration signing for all HTTP methods
- ✅ **Smart Key Discovery** - OS-specific default locations for private keys
- ✅ **Replay Attack Protection** - Timestamp and nonce validation
- ✅ **Zero-Trust Architecture** - Private key never leaves your machine
- ✅ **Simple, Intuitive API** - Pythonic interface for all operations
- ✅ **Comprehensive Error Handling** - Clear exception hierarchy

---

## 📦 Installation

```bash
pip install neocore-sdk
```

**Requirements:**
- Python 3.8 or higher
- `cryptography>=41.0.0`
- `requests>=2.31.0`

---

## 🚀 Quick Start

### 1. Generate Ed25519 Key Pair

```bash
# Using the SDK CLI (recommended)
neocore-keygen

# Or using OpenSSL
openssl genpkey -algorithm ED25519 -out ~/.neocore/p_a1b2c3.pem
openssl pkey -in ~/.neocore/p_a1b2c3.pem -pubout -out ~/.neocore/pub_a1b2c3.pem
```
c
This creates:
- `~/.neocore/p_a1b2c3.pem` - **Keep secret! Never share or commit to git**
- `~/.neocore/pub_a1b2c3.pem` - Safe to share with NeoCore API

### 2. Register Your Public Key

Register your public key with the NeoCore API (requires Firebase authentication):

```python
import requests
import uuid

# Read your public key
with open("~/.neocore/pub_a1b2c3.pem", "r") as f:
    public_key_pem = f.read()

# Get Firebase JWT from your authentication flow
firebase_jwt = "your-firebase-jwt-token"

# Generate unique key ID
key_id = str(uuid.uuid4())

# Register with NeoCore API
response = requests.post(
    "https://api.neosapien.xyz/api/v1/dev-keys",
    headers={"Authorization": f"Bearer {firebase_jwt}"},
    json={
        "key_id": key_id,
        "public_key_pem": public_key_pem
    }
)

# Save this key_id - you'll need it for all SDK requests
print(f"Your key_id: {key_id}")
```

### 3. Make Authenticated Requests

```python
from neocore_sdk import NeoCoreClient

# Initialize client (auto-discovers private key from default locations)
# Uses default NeoCore API URL: https://api.neosapien.xyz
client = NeoCoreClient(key_id="your-key-id-from-step-2")

# Make signed requests - that's it!
response = client.get("/api/v1/users")
print(response.json())
```

---

## 📖 Complete Usage Guide

### Initialize the Client

```python
from neocore_sdk import NeoCoreClient

# Basic initialization (uses default NeoCore API URL)
client = NeoCoreClient(key_id="your-key-id")

# Custom base URL (for different environments or custom deployments)
client = NeoCoreClient(
    key_id="your-key-id",
    base_url="https://custom-api.example.com"
)

# With custom private key path
client = NeoCoreClient(
    key_id="your-key-id",
    private_key_path="/custom/path/to/p_a1b2c3.pem"
)

# With custom timeout
client = NeoCoreClient(
    key_id="your-key-id",
    timeout=60  # seconds (default: 30)
)

# All options combined
client = NeoCoreClient(
    key_id="your-key-id",
    base_url="https://staging-api.neosapien.xyz",
    private_key_path="/secure/keys/staging_p_a1b2c3.pem",
    timeout=45
)
```

### HTTP Methods

All HTTP methods are supported with automatic signing:

#### GET Request

```python
# Simple GET
response = client.get("/api/v1/users")

# GET with query parameters
response = client.get("/api/v1/users", params={
    "page": 1,
    "limit": 20,
    "sort": "created_at",
    "order": "desc"
})
```

#### POST Request

```python
# POST with JSON body
response = client.post("/api/v1/users", data={
    "name": "John Doe",
    "email": "john@example.com",
    "role": "developer"
})

# POST with nested data
response = client.post("/api/v1/projects", data={
    "name": "AI Assistant",
    "metadata": {
        "tech_stack": ["Python", "FastAPI"],
        "status": "active"
    },
    "tags": ["ai", "api"]
})
```

#### PUT Request (Full Update)

```python
response = client.put("/api/v1/users/123", data={
    "name": "Jane Doe",
    "email": "jane@example.com",
    "role": "admin"
})
```

#### PATCH Request (Partial Update)

```python
# Update only specific fields
response = client.patch("/api/v1/users/123", data={
    "email": "newemail@example.com"
})
```

#### DELETE Request

```python
# Simple DELETE
response = client.delete("/api/v1/users/123")

# DELETE with query parameters
response = client.delete("/api/v1/sessions", params={
    "status": "expired",
    "older_than_days": 30
})
```

### Response Handling

All methods return a `requests.Response` object:

```python
response = client.get("/api/v1/users")

# Status code
print(response.status_code)  # 200, 401, 404, etc.

# JSON response
data = response.json()

# Raw text
text = response.text

# Headers
print(response.headers)

# Check if successful (2xx status)
if response.ok:
    print("Success!")
else:
    print(f"Error: {response.status_code}")
```

---

## 🔑 Private Key Management

### Default Key Locations

The SDK automatically searches for your private key in these locations (in order):

#### Linux/macOS
1. `~/.neocore/p_a1b2c3.pem` ⭐ **RECOMMENDED**
2. `~/.ssh/p_a1b2c3.pem`
3. `/etc/neocore/p_a1b2c3.pem`
4. `./p_a1b2c3.pem` (current directory)

#### Windows
1. `%USERPROFILE%\.neocore\p_a1b2c3.pem` ⭐ **RECOMMENDED**
2. `%APPDATA%\neocore\p_a1b2c3.pem`
3. `%PROGRAMDATA%\neocore\p_a1b2c3.pem`
4. `.\p_a1b2c3.pem` (current directory)

### Custom Key Path

```python
client = NeoCoreClient(
    key_id="your-key-id",
    private_key_path="/secure/vault/my-key.pem"
)
```

---

## 🛡️ Exception Handling

The SDK provides a comprehensive exception hierarchy for precise error handling.

### Exception Hierarchy

```
SecureSDKError (Base exception)
├── KeyLoadError (Key loading failures)
│   └── KeyNotFoundError (No key found in default locations)
├── SigningError (Signature generation failures)
├── APIConnectionError (HTTP connection failures)
└── CanonicalizationError (Request canonicalization failures)
```

### Import Exceptions

```python
from neocore_sdk import (
    NeoCoreClient,
    SecureSDKError,
    KeyLoadError,
    KeyNotFoundError,
    SigningError,
    APIConnectionError,
    CanonicalizationError
)
```

### Exception Examples

#### KeyLoadError

Raised when private key cannot be loaded or is invalid.

```python
try:
    client = NeoCoreClient(
        key_id="your-key-id",
        private_key_path="/invalid/path/p_a1b2c3.pem"
    )
except KeyLoadError as e:
    print(f"Failed to load private key: {e}")
    print("Solution: Check the key path and file permissions")
```

#### KeyNotFoundError

Raised when no private key is found in default locations (inherits from `KeyLoadError`).

```python
try:
    client = NeoCoreClient(
        key_id="your-key-id"
        # No private_key_path specified - will auto-discover
    )
except KeyNotFoundError as e:
    print(f"No private key found: {e}")
    print("Solution: Generate keys with: neocore-keygen")
except KeyLoadError as e:
    print(f"Key load error: {e}")
```

#### SigningError

Raised when signature generation fails.

```python
try:
    response = client.post("/api/v1/users", data={"name": "John"})
except SigningError as e:
    print(f"Failed to sign request: {e}")
    print("Solution: Verify your private key is valid")
```

#### APIConnectionError

Raised when HTTP connection to API fails.

```python
try:
    response = client.get("/api/v1/users")
except APIConnectionError as e:
    print(f"Connection failed: {e}")
    print("Solution: Check network connectivity and base_url")
```

#### CanonicalizationError

Raised when request canonicalization fails (rare).

```python
try:
    response = client.get("/api/v1/users")
except CanonicalizationError as e:
    print(f"Canonicalization failed: {e}")
    print("Solution: Contact support - this is unusual")
```

### Comprehensive Error Handling

```python
from neocore_sdk import (
    NeoCoreClient,
    KeyLoadError,
    KeyNotFoundError,
    SigningError,
    APIConnectionError,
    CanonicalizationError
)

try:
    # Initialize client
    client = NeoCoreClient(key_id="your-key-id")

    # Make request
    response = client.get("/api/v1/users", params={"page": 1})

    # Handle HTTP errors
    if response.status_code == 200:
        users = response.json()
        print(f"Found {len(users)} users")
    elif response.status_code == 401:
        print("Unauthorized: Check your key_id or signature")
    elif response.status_code == 403:
        print("Forbidden: Insufficient permissions")
    elif response.status_code == 404:
        print("Not found: Check endpoint path")
    elif response.status_code == 429:
        print("Rate limited: Too many requests")
    else:
        print(f"HTTP Error {response.status_code}: {response.text}")

except KeyNotFoundError as e:
    print(f"❌ No private key found: {e}")
    print("Run: neocore-keygen")

except KeyLoadError as e:
    print(f"❌ Key load error: {e}")
    print("Check file path and permissions")

except SigningError as e:
    print(f"❌ Signing failed: {e}")
    print("Verify your private key is valid")

except APIConnectionError as e:
    print(f"❌ Connection error: {e}")
    print("Check network and base_url")

except CanonicalizationError as e:
    print(f"❌ Canonicalization error: {e}")
    print("Contact support")

except Exception as e:
    print(f"❌ Unexpected error: {e}")
```

---

## 🔧 CLI Tools

The SDK includes command-line tools for key management.

### neocore-keygen

Generate a new Ed25519 key pair.

```bash
# Generate in default location (~/.neocore/)
neocore-keygen

# Generate in custom location
neocore-keygen --output-dir /path/to/keys

# Overwrite existing keys without prompting
neocore-keygen --force

# Combine options
neocore-keygen --output-dir /secure/keys --force
```

**Options:**
- `--output-dir DIR` - Directory to save keys (default: `~/.neocore`)
- `--force` - Overwrite existing keys without prompting

**Output:**
```
✅ Key pair generated successfully!
   Private key: p_a1b2c3.pem (Keep this SECRET!)
   Public key:  pub_a1b2c3.pem (Share with NeoCore API)
```

### neocore-verify-key

Verify an Ed25519 private key and extract public key.

```bash
# Verify default key
neocore-verify-key

# Verify custom key
neocore-verify-key /path/to/p_a1b2c3.pem
```

**Output:**
```
✅ Private key is valid!
   Algorithm: Ed25519
   Key file: /home/user/.neocore/p_a1b2c3.pem
   Permissions: 600 (Secure)

📋 Public Key:
-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEA...
-----END PUBLIC KEY-----
```

---

## 🔐 Security Features

### How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                      Client Side (SDK)                      │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  1. Prepare Request                                         │
│     - Method: GET, POST, etc.                               │
│     - Path: /api/v1/users                                   │
│     - Query: ?page=1&limit=10                               │
│     - Body: {"name": "John"}                                │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Generate Security Metadata                              │
│     - Timestamp: Unix seconds (e.g., 1704214800)            │
│     - Nonce: UUID v4 (e.g., a1b2c3d4-...)                   │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Build Canonical String                                  │
│     GET                                                     │
│     /api/v1/users                                           │
│     limit=10&page=1                                         │
│     e3b0c44... (SHA256 of body)                             │
│     1704214800                                              │
│     a1b2c3d4-...                                            │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  4. Sign with Private Key (Ed25519)                         │
│     signature = sign(canonical_string, private_key)         │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  5. Add Headers to Request                                  │
│     Content-Type: application/json                          │
│     X-Key-Id: your-key-id                                   │
│     X-Timestamp: 1704214800                                 │
│     X-Nonce: a1b2c3d4-...                                   │
│     X-Signature: abc123... (hex)                            │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  6. Send HTTP Request                                       │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                      Server Side (NeoCore API)              │
├─────────────────────────────────────────────────────────────┤
│  1. Extract X-Key-Id from headers                           │
│  2. Fetch public key from database                          │
│  3. Rebuild canonical string from request                   │
│  4. Verify signature using public key                       │
│  5. Validate timestamp (within time window)                 │
│  6. Check nonce uniqueness (prevent replay)                 │
│  7. ✅ Authorized → Process request                         │
│     ❌ Unauthorized → Return 401                            │
└─────────────────────────────────────────────────────────────┘
```

### Automatic Security Headers

Every request includes these headers (automatically added by SDK):

| Header | Description | Example |
|--------|-------------|---------|
| `Content-Type` | Request content type | `application/json` |
| `X-Key-Id` | Your registered key ID | `a1b2c3d4-uuid` |
| `X-Timestamp` | Unix timestamp (seconds) | `1704214800` |
| `X-Nonce` | Unique request ID (UUID v4) | `f1e2d3c4-uuid` |
| `X-Signature` | Ed25519 signature (hex) | `9a8b7c6d...` |

### Security Benefits

1. **Zero-Trust Architecture**
   - Private key never leaves your machine
   - Server never knows your secret
   - Database breach doesn't compromise credentials

2. **Request Integrity**
   - Signature covers method, path, query, body, timestamp, nonce
   - Any tampering invalidates signature
   - Man-in-the-middle attacks prevented

3. **Replay Attack Protection**
   - Timestamp validation (requests expire in 5 minutes)
   - Nonce uniqueness check (prevent duplicate requests)
   - Old requests automatically rejected

4. **Instant Revocation**
   - Server can revoke key_id instantly
   - No token expiration wait time
   - Granular access control per key

---

## 📋 API Reference

### NeoCoreClient

Main client class for making authenticated requests.

#### Constructor

```python
NeoCoreClient(
    key_id: str,
    base_url: str = "https://api.neosapien.xyz",
    private_key_path: Optional[str] = None,
    timeout: int = 30
)
```

**Parameters:**
- `key_id` (str): Your registered developer key ID (**required**)
- `base_url` (str): API base URL (default: `"https://api.neosapien.xyz"`)
  - Override for custom deployments, staging, or development environments
- `private_key_path` (Optional[str]): Path to private key PEM file. If `None`, searches default locations.
- `timeout` (int): Request timeout in seconds (default: 30)

**Raises:**
- `KeyLoadError`: If private key cannot be loaded
- `KeyNotFoundError`: If no key found in default locations

**Examples:**
```python
# Basic (uses default NeoCore API)
client = NeoCoreClient(key_id="a1b2c3d4-5678-90ab-cdef-1234567890ab")

# Custom base URL
client = NeoCoreClient(
    key_id="a1b2c3d4-5678-90ab-cdef-1234567890ab",
    base_url="https://staging-api.neosapien.xyz"
)
```

#### Methods

All methods automatically sign requests and return `requests.Response`.

##### get()

```python
get(endpoint: str, params: Optional[dict] = None) -> requests.Response
```

Send signed GET request.

**Parameters:**
- `endpoint` (str): API endpoint path
- `params` (Optional[dict]): Query parameters

**Returns:** `requests.Response`

**Example:**
```python
response = client.get("/api/v1/users", params={"page": 1})
```

##### post()

```python
post(endpoint: str, data: Optional[dict] = None) -> requests.Response
```

Send signed POST request.

**Parameters:**
- `endpoint` (str): API endpoint path
- `data` (Optional[dict]): JSON body data

**Returns:** `requests.Response`

**Example:**
```python
response = client.post("/api/v1/users", data={"name": "John"})
```

##### put()

```python
put(endpoint: str, data: Optional[dict] = None) -> requests.Response
```

Send signed PUT request (full update).

**Parameters:**
- `endpoint` (str): API endpoint path
- `data` (Optional[dict]): JSON body data

**Returns:** `requests.Response`

**Example:**
```python
response = client.put("/api/v1/users/123", data={"name": "Jane"})
```

##### patch()

```python
patch(endpoint: str, data: Optional[dict] = None) -> requests.Response
```

Send signed PATCH request (partial update).

**Parameters:**
- `endpoint` (str): API endpoint path
- `data` (Optional[dict]): JSON body data

**Returns:** `requests.Response`

**Example:**
```python
response = client.patch("/api/v1/users/123", data={"email": "new@email.com"})
```

##### delete()

```python
delete(endpoint: str, params: Optional[dict] = None) -> requests.Response
```

Send signed DELETE request.

**Parameters:**
- `endpoint` (str): API endpoint path
- `params` (Optional[dict]): Query parameters

**Returns:** `requests.Response`

**Example:**
```python
response = client.delete("/api/v1/users/123")
```

---

## 🎯 Best Practices

### 1. Key Security

```python
# ✅ GOOD: Keep private keys secure
# - Store in ~/.neocore/ with permissions 600
# - Never commit to git (add *.pem to .gitignore)
# - Use environment variables in production

# ❌ BAD: Don't hardcode key paths in source code
client = NeoCoreClient(
    key_id="key-123",
    private_key_path="/hardcoded/path/p_a1b2c3.pem"  # Bad!
)

# ✅ GOOD: Use environment variables
import os
client = NeoCoreClient(
    key_id=os.getenv("NEOCORE_KEY_ID"),
    base_url=os.getenv("NEOCORE_API_URL", "https://api.neosapien.xyz"),
    private_key_path=os.getenv("NEOCORE_PRIVATE_KEY_PATH")
)
```

### 2. Error Handling

```python
# ✅ GOOD: Catch specific exceptions
try:
    response = client.get("/api/v1/users")
except KeyNotFoundError:
    # Specific handling for missing key
    print("Generate keys with: neocore-keygen")
except APIConnectionError:
    # Specific handling for network issues
    print("Check your network connection")

# ❌ BAD: Catch generic exceptions
try:
    response = client.get("/api/v1/users")
except Exception as e:
    print(f"Something went wrong: {e}")
```

### 3. Response Handling

```python
# ✅ GOOD: Check status codes properly
response = client.get("/api/v1/users")
if response.status_code == 200:
    data = response.json()
    # Process data
elif response.status_code == 401:
    print("Unauthorized")
elif response.status_code == 404:
    print("Not found")

# ❌ BAD: Assume all responses are successful
response = client.get("/api/v1/users")
data = response.json()  # May fail if status is not 200
```

### 4. Key Rotation

```python
# Regularly rotate your keys
# 1. Generate new key pair
# 2. Register new public key with new key_id
# 3. Update your application to use new key_id
# 4. After verification, delete old key from server
# 5. Delete old private key from your system
```

---

## 🐛 Troubleshooting

### "No private key found"

**Error:**
```
KeyNotFoundError: No private key found in default locations
```

**Solution:**
```bash
# Generate keys
neocore-keygen

# Or specify custom path
client = NeoCoreClient(
    key_id="...",
    private_key_path="/custom/path/p_a1b2c3.pem"
)
```

### "Invalid signature"

**Error:**
```
HTTP 401: Invalid signature
```

**Causes & Solutions:**
1. **Wrong key_id**: Verify `key_id` matches registered public key
2. **Key mismatch**: Private key doesn't match registered public key
3. **Clock skew**: System time is incorrect (timestamp validation fails)
   ```bash
   # Sync system time
   sudo ntpdate -s time.nist.gov  # Linux/macOS
   ```

### "Connection error"

**Error:**
```
APIConnectionError: Failed to connect to https://api.example.com
```

**Solutions:**
1. Check network connectivity
2. Verify `base_url` is correct
3. Check if API server is running
4. Verify firewall/proxy settings

### "Permission denied" (Key file)

**Error:**
```
PermissionError: [Error no. 13] Permission denied: '/path/to/p_a1b2c3.pem'
```

**Solution:**
```bash
# Fix file permissions
chmod 600 ~/.neocore/p_a1b2c3.pem
```

---

## 📚 Examples

See the [examples](examples/) directory for more:

- [basic_usage.py](examples/basic_usage.py) - Simple usage examples
- [register_public_key.py](examples/register_public_key.py) - Key registration flow

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 🔗 Links

- **Documentation**: [https://docs.neosapien.xyz](https://docs.neosapien.xyz)
- **GitHub**: [https://github.com/neosapien/neocore-sdk](https://github.com/neosapien/neocore-sdk)
- **Issues**: [https://github.com/neosapien/neocore-sdk/issues](https://github.com/neosapien/neocore-sdk/issues)
- **PyPI**: [https://pypi.org/project/neocore-sdk](https://pypi.org/project/neocore-sdk)

---

## 💡 Support

For help and support:
- 📧 Email: support@neosapien.xyz
- 💬 GitHub Issues: [Report an issue](https://github.com/neosapien/neocore-sdk/issues)
- 📖 Documentation: [https://docs.neosapien.xyz](https://docs.neosapien.xyz)

---

## 🎉 Quick Reference

```python
# Install
pip install neocore-sdk

# Generate keys
neocore-keygen

# Import and use
from neocore_sdk import NeoCoreClient

# Initialize (uses default NeoCore API URL)
client = NeoCoreClient(key_id="your-key-id")

# Make requests
response = client.get("/api/v1/users")
response = client.post("/api/v1/users", data={"name": "John"})
response = client.put("/api/v1/users/123", data={"name": "Jane"})
response = client.patch("/api/v1/users/123", data={"email": "new@email.com"})
response = client.delete("/api/v1/users/123")

# Custom base URL (for staging/development)
staging_client = NeoCoreClient(
    key_id="staging-key-id",
    base_url="https://staging-api.neosapien.xyz"
)
```

---

Made by NeoSapien
