#!/usr/bin/env python3
"""
Create new SCIM user example

This script demonstrates how to create a new user in the Cato SCIM service.
Requires CATO_SCIM_URL and CATO_SCIM_TOKEN environment variables or a .env file.

Usage:
    python3 examples/create_user.py <email> <given_name> <family_name> <external_id> [--password PASSWORD] [--inactive]
"""

import sys
import os
import argparse
import json

# Add parent directory to import catoscim
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from catoscim import CatoSCIM


def main():
    parser = argparse.ArgumentParser(description="Create a new SCIM user")
    parser.add_argument('email', help='User email address')
    parser.add_argument('given_name', help='User given name (first name)')
    parser.add_argument('family_name', help='User family name (last name)')
    parser.add_argument('external_id', help='External ID for the user')
    parser.add_argument('--password', help='User password (auto-generated if not provided)')
    parser.add_argument('--inactive', action='store_true', help='Create user as inactive')
    args = parser.parse_args()
    
    try:
        # Initialize CatoSCIM client
        client = CatoSCIM()
        print(f"Creating user '{args.email}' in SCIM service...", file=sys.stderr)
        
        # Create the user
        success, result = client.create_user(
            email=args.email,
            givenName=args.given_name,
            familyName=args.family_name,
            externalId=args.external_id,
            password=args.password,
            active=not args.inactive
        )
        
        if not success:
            print(f"Error creating user: {result}", file=sys.stderr)
            sys.exit(1)
        
        print(f"Successfully created user: {result.get('userName')}", file=sys.stderr)
        print(f"User ID: {result.get('id')}", file=sys.stderr)
        print(f"Active: {result.get('active')}", file=sys.stderr)
        
        # Output the full user object as JSON
        print(json.dumps(result, indent=2))
            
    except ValueError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        print("Ensure CATO_SCIM_URL and CATO_SCIM_TOKEN are set", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()