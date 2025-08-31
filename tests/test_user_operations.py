"""
Test for CatoSCIM user operations.

These tests require valid SCIM credentials to be available either through:
- Environment variables: CATO_SCIM_URL and CATO_SCIM_TOKEN
- A .env file in the project root

Tests will fail if valid credentials are not provided.
"""

import os
import sys
import pytest

# Add parent directory to path to import catoscim
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from catoscim import CatoSCIM


def test_get_users_returns_at_least_one_user():
    """
    Test that get_users() successfully retrieves users from the SCIM service.
    This test requires valid credentials and expects at least one user to exist.
    """
    # Get credentials from environment
    if not os.environ.get('CATO_SCIM_URL') or not os.environ.get('CATO_SCIM_TOKEN'):
        pytest.fail("CATO_SCIM_URL and CATO_SCIM_TOKEN must be set in environment or .env file")
    
    # Initialize CatoSCIM client
    client = CatoSCIM()
    
    # Call get_users() function
    success, users = client.get_users()
    
    # Verify the call was successful
    assert success is True, f"get_users() failed with error: {users}"
    
    # Verify at least one user was returned
    assert isinstance(users, list), "get_users() should return a list"
    assert len(users) >= 1, "Expected at least one user to be returned from SCIM service"
    
    # Verify user objects have expected structure
    first_user = users[0]
    assert "id" in first_user, "User should have an 'id' field"
    assert "userName" in first_user, "User should have a 'userName' field"
    
    # Verify call_count was incremented
    assert client.call_count > 0, "call_count should be incremented after API call"
    
    print(f"✓ Successfully retrieved {len(users)} users from SCIM service")
    print(f"✓ First user ID: {first_user['id']}")
    print(f"✓ First user name: {first_user['userName']}")
    print(f"✓ API call count: {client.call_count}")