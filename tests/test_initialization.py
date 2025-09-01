"""
Test for CatoSCIM class initialization.

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


def test_catoscim_initialization_with_environment_credentials():
    """
    Test that CatoSCIM initializes correctly with credentials from environment.
    This test requires valid CATO_SCIM_URL and CATO_SCIM_TOKEN to be set.
    """
    # Get credentials from environment
    expected_url = os.environ.get('CATO_SCIM_URL')
    expected_token = os.environ.get('CATO_SCIM_TOKEN')
    
    # Fail if credentials are not available
    if not expected_url or not expected_token:
        pytest.fail("CATO_SCIM_URL and CATO_SCIM_TOKEN must be set in environment or .env file")
    
    # Initialize CatoSCIM using environment variables
    client = CatoSCIM()
    
    # Verify URL and token match environment variables
    assert client.baseurl == expected_url
    assert client.token == expected_token
    
    # Verify default values are set correctly
    assert client.verify_ssl == True
    assert client.call_count == 0
    
    print(f"✓ CatoSCIM initialized with URL: {client.baseurl[:30]}...")
    print(f"✓ Token is set (length: {len(client.token)} characters)")
    print(f"✓ SSL verification enabled: {client.verify_ssl}")
    print(f"✓ Initial call_count: {client.call_count}")