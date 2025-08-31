# CatoSCIM Examples

This directory contains standalone example scripts that demonstrate how to use the CatoSCIM SDK for common tasks. All scripts are designed to be called from the command line and require valid SCIM credentials.

## Prerequisites

Before running any examples, ensure you have:

1. **Credentials configured**: Set environment variables or create a `.env` file:
   ```bash
   export CATO_SCIM_URL="https://scimservice.catonetworks.com:4443/scim/v2/YOUR_ACCOUNT/YOUR_INSTANCE"
   export CATO_SCIM_TOKEN="your-scim-token-here"
   ```

2. **Dependencies installed**:
   ```bash
   pip install -r requirements.txt
   ```

## Available Examples

### 1. List Users (`list_users.py`)
List all users in the SCIM service with various output formats.

```bash
# Display users in a formatted table (default)
python3 examples/list_users.py

# Output as CSV
python3 examples/list_users.py --format csv

# Output as JSON
python3 examples/list_users.py --format json
```

### 2. List Groups (`list_groups.py`)
List all groups in the SCIM service with various output formats.

```bash
# Display groups in a formatted table (default)
python3 examples/list_groups.py

# Output as CSV
python3 examples/list_groups.py --format csv

# Output as JSON
python3 examples/list_groups.py --format json
```

### 3. Find User (`find_user.py`)
Search for a specific user by username or ID.

```bash
# Find user by username (default)
python3 examples/find_user.py john.doe@example.com

# Find user by ID
python3 examples/find_user.py 507f1f77bcf86cd799439011 --by-id

# Output user details as JSON
python3 examples/find_user.py john.doe@example.com --format json

# Find by ID and output as JSON
python3 examples/find_user.py 507f1f77bcf86cd799439011 --by-id --format json
```

### 4. Find Group (`find_group.py`)
Search for a specific group by display name or ID.

```bash
# Find group by display name (default)
python3 examples/find_group.py "Engineering Team"

# Find group by ID
python3 examples/find_group.py 507f1f77bcf86cd799439011 --by-id

# Output group details as JSON
python3 examples/find_group.py "Marketing Team" --format json

# Find by ID and output as JSON
python3 examples/find_group.py 507f1f77bcf86cd799439011 --by-id --format json
```

### 5. Create User (`create_user.py`)
Create a new user in the SCIM service.

```bash
# Create user with auto-generated password
python3 examples/create_user.py jane.doe@example.com Jane Doe ext-123

# Create user with specific password
python3 examples/create_user.py jane.doe@example.com Jane Doe ext-123 --password "SecurePass123!"

# Create inactive user
python3 examples/create_user.py jane.doe@example.com Jane Doe ext-123 --inactive
```

### 6. Group Membership (`group_membership.py`)
Manage group membership by adding/removing users or listing group members.

```bash
# Add user to group
python3 examples/group_membership.py add "Engineering Team" john.doe@example.com

# Remove user from group
python3 examples/group_membership.py remove "Engineering Team" john.doe@example.com

# List all members of a group
python3 examples/group_membership.py list "Engineering Team"
```

## Output and Error Handling

All examples follow these conventions:

- **Status messages** are written to stderr
- **Data output** is written to stdout
- **Exit codes**: 0 for success, 1 for errors
- **Error messages** include helpful context

This design allows for easy scripting and piping:

```bash
# Save user list to file
python3 examples/list_users.py --format csv > users.csv

# Count users silently
user_count=$(python3 examples/list_users.py --format csv 2>/dev/null | tail -n +2 | wc -l)
echo "Total users: $user_count"
```

## Script Structure

All example scripts follow a consistent pattern:

1. **Argument parsing** with helpful usage messages
2. **Credential validation** with clear error messages
3. **API operations** with proper error handling
4. **Formatted output** appropriate for the use case
5. **Proper exit codes** for scripting integration

## Security Notes

- Scripts never log or display authentication tokens
- Credential errors provide guidance without exposing sensitive data
- All scripts validate input parameters before making API calls

## Extending the Examples

To create new examples:

1. Copy an existing script as a template
2. Follow the established patterns for imports, error handling, and output
3. Add proper argument parsing with `argparse`
4. Include helpful documentation and usage examples
5. Make the script executable with `chmod +x`