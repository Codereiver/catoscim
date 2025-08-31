"""
Test for CatoSCIM group operations.

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


def test_get_groups_returns_at_least_one_group():
    """
    Test that get_groups() successfully retrieves groups from the SCIM service.
    This test requires valid credentials and expects at least one group to exist.
    """
    # Get credentials from environment
    if not os.environ.get('CATO_SCIM_URL') or not os.environ.get('CATO_SCIM_TOKEN'):
        pytest.fail("CATO_SCIM_URL and CATO_SCIM_TOKEN must be set in environment or .env file")
    
    # Initialize CatoSCIM client
    client = CatoSCIM()
    
    # Call get_groups() function
    success, groups = client.get_groups()
    
    # Verify the call was successful
    assert success is True, f"get_groups() failed with error: {groups}"
    
    # Verify at least one group was returned
    assert isinstance(groups, list), "get_groups() should return a list"
    assert len(groups) >= 1, "Expected at least one group to be returned from SCIM service"
    
    # Verify group objects have expected structure
    first_group = groups[0]
    assert "id" in first_group, "Group should have an 'id' field"
    assert "displayName" in first_group, "Group should have a 'displayName' field"
    assert "members" in first_group, "Group should have a 'members' field"
    assert isinstance(first_group["members"], list), "Group members should be a list"
    
    # Verify call_count was incremented
    assert client.call_count > 0, "call_count should be incremented after API call"
    
    print(f"✓ Successfully retrieved {len(groups)} groups from SCIM service")
    print(f"✓ First group ID: {first_group['id']}")
    print(f"✓ First group name: {first_group['displayName']}")
    print(f"✓ First group member count: {len(first_group['members'])}")
    print(f"✓ API call count: {client.call_count}")