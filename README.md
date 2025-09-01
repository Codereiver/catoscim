# CatoSCIM SDK

> ⚠️ **DISCLAIMER**: This is an unofficial, community-developed SDK for the Cato Networks SCIM API. This is NOT an official Cato Networks release and is provided with no guarantees of support. For official support, contact Cato Networks directly at api@catonetworks.com.

A simple Python SDK for interacting with the Cato Networks SCIM (System for Cross-domain Identity Management) service. This SDK provides a Python library for programmatic access and includes example command-line scripts for common tasks.

## Features

- **Secure by Default**: SSL/TLS verification enabled by default
- **Pure Python**: Uses only Python standard library with minimal dependencies
- **Environment Configuration**: Supports `.env` files and environment variables
- **SDK Library**: Import and use as a Python library in your applications
- **Comprehensive API Coverage**: Supports all major SCIM operations for users and groups
- **Example Scripts**: Ready-to-use command-line examples for common tasks
- **Professional Logging**: Uses Python's logging module with configurable levels
- **Security Reviewed**: Comprehensive security review with fixes implemented

## Installation

1. **Clone or download** this repository
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure credentials** (see Configuration section below)

## Quick Start

```python
from catoscim import CatoSCIM

# Initialize with environment variables (recommended)
client = CatoSCIM()  # SSL verification enabled by default

# List all users
success, users = client.get_users()
if success:
    print(f"Found {len(users)} users")
```

## Configuration

The SDK requires SCIM service credentials. You can provide these in several ways:

### Environment Variables
```bash
export CATO_SCIM_URL="https://scimservice.catonetworks.com:4443/scim/v2/YOUR_ACCOUNT/YOUR_INSTANCE"
export CATO_SCIM_TOKEN="your-scim-token-here"
```

### .env File
Create a `.env` file in the project root:
```bash
CATO_SCIM_URL=https://scimservice.catonetworks.com:4443/scim/v2/YOUR_ACCOUNT/YOUR_INSTANCE
CATO_SCIM_TOKEN=your-scim-token-here
```

### Explicit Parameters
```python
from catoscim import CatoSCIM
client = CatoSCIM(baseurl="https://your-url", token="your-token")
```

## Using as a Python SDK

### Basic Usage

```python
from catoscim import CatoSCIM

# Initialize client (uses environment variables or .env file)
# SSL verification is enabled by default for security
client = CatoSCIM()

# For development environments with self-signed certificates (NOT for production!)
# client = CatoSCIM(verify_ssl=False)  # Will show security warning

# Get all users
success, users = client.get_users()
if success:
    for user in users:
        print(f"User: {user['userName']} (ID: {user['id']})")
else:
    print(f"Error: {users}")
```

### User Operations

```python
# Create a new user
success, user = client.create_user(
    email="john.doe@example.com",
    givenName="John",
    familyName="Doe",
    externalId="ext-123",
    password="SecurePassword123!",  # Optional
    active=True  # Optional, defaults to True
)

# Find user by username
success, users = client.find_users("userName", "john.doe@example.com")

# Get user by ID
success, user = client.get_user("user-id-123")

# Update user
user_data = {
    "userName": "john.doe@example.com",
    "active": False
}
success, result = client.update_user("user-id-123", user_data)

# Disable user
success, result = client.disable_user("user-id-123")
```

### Group Operations

```python
# Get all groups
success, groups = client.get_groups()

# Create a new group
success, group = client.create_group(
    displayName="Engineering Team",
    externalId="eng-team-001",
    members=[]  # Optional
)

# Find group by name
success, groups = client.find_group("Engineering Team")

# Get group by ID
success, group = client.get_group("group-id-123")

# Add members to group
members = [{"value": "user-id-123"}]
success, result = client.add_members("group-id-123", members)

# Remove members from group
success, result = client.remove_members("group-id-123", members)

# Rename group
success, result = client.rename_group("group-id-123", "New Team Name")

# Disable group
success, result = client.disable_group("group-id-123")
```

### Error Handling

All SDK methods return a tuple `(success, result)`:
- `success`: Boolean indicating if the operation succeeded
- `result`: Either the response data (on success) or error information (on failure)

```python
success, users = client.get_users()
if not success:
    print(f"Error code: {users.get('status')}")
    print(f"Error message: {users.get('error')}")
    return

# Process successful result
for user in users:
    print(user['userName'])
```

## Example Scripts

The `examples/` directory contains ready-to-use command-line scripts for common tasks:

### 1. List Users
```bash
# Table format (default)
python3 examples/list_users.py

# CSV format
python3 examples/list_users.py --format csv

# JSON format
python3 examples/list_users.py --format json
```

### 2. List Groups
```bash
python3 examples/list_groups.py
python3 examples/list_groups.py --format csv
```

### 3. Find User
```bash
# Find by username
python3 examples/find_user.py john.doe@example.com

# Find by user ID
python3 examples/find_user.py 507f1f77bcf86cd799439011 --by-id
```

### 4. Find Group
```bash
# Find by display name
python3 examples/find_group.py "Engineering Team"

# Find by group ID
python3 examples/find_group.py 507f1f77bcf86cd799439011 --by-id
```

### 5. Create User
```bash
# With auto-generated password
python3 examples/create_user.py jane.doe@example.com Jane Doe ext-123

# With specific password
python3 examples/create_user.py jane.doe@example.com Jane Doe ext-123 --password "Pass123!"

# Create inactive user
python3 examples/create_user.py jane.doe@example.com Jane Doe ext-123 --inactive
```

### 6. Update User Password
```bash
# Update a user's password
python3 examples/update_password.py john.doe@example.com "NewSecurePassword123!"
```

### 7. Enable/Disable User
```bash
# Check user status
python3 examples/user_status.py status john.doe@example.com

# Enable (activate) user
python3 examples/user_status.py enable john.doe@example.com

# Disable (deactivate) user
python3 examples/user_status.py disable john.doe@example.com
```

### 8. Group Membership Management
```bash
# Add user to group
python3 examples/group_membership.py add "Engineering Team" john.doe@example.com

# Remove user from group
python3 examples/group_membership.py remove "Engineering Team" john.doe@example.com

# List group members
python3 examples/group_membership.py list "Engineering Team"
```

## Testing

Run the test suite to verify your configuration:

```bash
# Run all tests
pytest tests/

# Run specific test files
pytest tests/test_initialization.py -v
pytest tests/test_user_operations.py -v
pytest tests/test_group_operations.py -v
```

Tests require valid SCIM credentials and will fail if credentials are not properly configured.

## API Reference

### CatoSCIM Class

#### Constructor
```python
CatoSCIM(baseurl=None, token=None, log_level=0, verify_ssl=True)
```
- `baseurl`: SCIM service URL (optional if `CATO_SCIM_URL` is set)
- `token`: Authentication token (optional if `CATO_SCIM_TOKEN` is set)
- `log_level`: Logging level (0=none, 1-3=increasing verbosity)
- `verify_ssl`: SSL certificate verification (default=True, set to False only for development)

#### Properties
- `baseurl`: The SCIM service URL
- `token`: The authentication token
- `log_level`: Current logging level (0=none, 1=ERROR, 2=INFO, 3=DEBUG)
- `verify_ssl`: SSL verification status (True/False)
- `call_count`: Number of API calls made
- `start`: Timestamp when client was initialized
- `logger`: Python logger instance for this client

#### Methods

**User Operations:**
- `get_users()` → `(bool, list)` - Get all users
- `get_user(userid)` → `(bool, dict)` - Get user by ID
- `find_users(field, value)` → `(bool, list)` - Search users
- `create_user(email, givenName, familyName, externalId, password=None, active=True)` → `(bool, dict)`
- `update_user(userid, user_data)` → `(bool, dict)`
- `disable_user(userid)` → `(bool, dict)`

**Group Operations:**
- `get_groups()` → `(bool, list)` - Get all groups
- `get_group(groupid)` → `(bool, dict)` - Get group by ID
- `find_group(displayName)` → `(bool, list)` - Search groups
- `create_group(displayName, externalId, members=[])` → `(bool, dict)`
- `update_group(groupid, group_data)` → `(bool, dict)`
- `rename_group(groupid, new_name)` → `(bool, dict)`
- `disable_group(groupid)` → `(bool, dict)`
- `add_members(groupid, members)` → `(bool, dict)`
- `remove_members(groupid, members)` → `(bool, dict)`

## Security Notes

- **SSL Verification**: Enabled by default for security. Can be disabled for development only with `verify_ssl=False`
- **Credentials**: Store in environment variables or `.env` file, never in code
- **Passwords**: Auto-generated using `secrets` module for cryptographic strength
- **Tokens**: Never logged or displayed in error messages
- **Development Mode**: When `verify_ssl=False`, a security warning is displayed

## Error Handling

The SDK uses minimal error handling as noted in the code comments. HTTP errors, URL errors, and connection issues are caught and returned as error responses.

Common error patterns:
```python
success, result = client.some_operation()
if not success:
    if 'status' in result:
        # HTTP error
        print(f"HTTP {result['status']}: {result['error']}")
    elif 'reason' in result:
        # URL/connection error
        print(f"Connection error: {result['reason']}")
    else:
        # Other error
        print(f"Error: {result['error']}")
```

## Project Structure

```
catoscim/
├── catoscim.py           # Main SDK implementation
├── examples/              # Standalone example scripts
│   ├── list_users.py
│   ├── list_groups.py
│   ├── find_user.py
│   ├── find_group.py
│   ├── create_user.py
│   ├── update_password.py
│   ├── user_status.py
│   └── group_membership.py
├── tests/                 # Test suite
│   ├── test_initialization.py
│   ├── test_user_operations.py
│   └── test_group_operations.py
├── .env.example          # Environment variable template
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── CLAUDE.local.md      # Technical documentation
└── SECURITY_REVIEW.md   # Security analysis and recommendations
```