#!/usr/bin/env python3
"""
List all SCIM users example

This script demonstrates how to retrieve and display all users from the Cato SCIM service.
Requires CATO_SCIM_URL and CATO_SCIM_TOKEN environment variables or a .env file.

Usage:
    python3 examples/list_users.py [--format csv|json|table]
"""

import sys
import os
import argparse
import json

# Add parent directory to import catoscim
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from catoscim import CatoSCIM


def print_users_table(users):
    """Print users in a formatted table."""
    if not users:
        print("No users found.")
        return
    
    print(f"{'ID':<25} {'Username':<30} {'Given Name':<15} {'Family Name':<15} {'Active':<8}")
    print("-" * 93)
    
    for user in users:
        user_id = user.get('id', 'N/A')[:24]
        username = user.get('userName', 'N/A')[:29]
        given_name = user.get('name', {}).get('givenName', 'N/A')[:14]
        family_name = user.get('name', {}).get('familyName', 'N/A')[:14]
        active = str(user.get('active', 'N/A'))
        
        print(f"{user_id:<25} {username:<30} {given_name:<15} {family_name:<15} {active:<8}")


def print_users_csv(users):
    """Print users in CSV format."""
    print("id,externalId,userName,givenName,familyName,created,active")
    for user in users:
        user_id = user.get('id', '')
        external_id = user.get('externalId', '')
        username = user.get('userName', '')
        given_name = user.get('name', {}).get('givenName', '')
        family_name = user.get('name', {}).get('familyName', '')
        created = user.get('created', '')
        active = user.get('active', '')
        
        print(f"{user_id},{external_id},{username},{given_name},{family_name},{created},{active}")


def main():
    parser = argparse.ArgumentParser(description="List all SCIM users")
    parser.add_argument(
        '--format', 
        choices=['csv', 'json', 'table'], 
        default='table',
        help='Output format (default: table)'
    )
    args = parser.parse_args()
    
    try:
        # Initialize CatoSCIM client
        client = CatoSCIM()
        print(f"Connecting to SCIM service at {client.baseurl[:50]}...", file=sys.stderr)
        
        # Get all users
        success, users = client.get_users()
        
        if not success:
            print(f"Error retrieving users: {users}", file=sys.stderr)
            sys.exit(1)
        
        print(f"Retrieved {len(users)} users", file=sys.stderr)
        
        # Output in requested format
        if args.format == 'csv':
            print_users_csv(users)
        elif args.format == 'json':
            print(json.dumps(users, indent=2))
        else:  # table
            print_users_table(users)
            
    except ValueError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        print("Ensure CATO_SCIM_URL and CATO_SCIM_TOKEN are set", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()