#!/usr/bin/env python3
"""
Find user by username or ID example

This script demonstrates how to find a specific user by their username or ID using the SCIM service.
Requires CATO_SCIM_URL and CATO_SCIM_TOKEN environment variables or a .env file.

Usage:
    python3 examples/find_user.py <username_or_id> [--by-id] [--format json|table]
"""

import sys
import os
import argparse
import json

# Add parent directory to import catoscim
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from catoscim import CatoSCIM


def print_user_table(user):
    """Print user details in a formatted table."""
    print(f"{'Field':<15} {'Value'}")
    print("-" * 50)
    
    print(f"{'ID':<15} {user.get('id', 'N/A')}")
    print(f"{'Username':<15} {user.get('userName', 'N/A')}")
    print(f"{'External ID':<15} {user.get('externalId', 'N/A')}")
    
    name = user.get('name', {})
    if name:
        print(f"{'Given Name':<15} {name.get('givenName', 'N/A')}")
        print(f"{'Family Name':<15} {name.get('familyName', 'N/A')}")
    
    emails = user.get('emails', [])
    if emails:
        for i, email in enumerate(emails):
            label = 'Email' if i == 0 else f'Email {i+1}'
            print(f"{label:<15} {email.get('value', 'N/A')} ({'Primary' if email.get('primary') else 'Secondary'})")
    
    print(f"{'Active':<15} {user.get('active', 'N/A')}")
    print(f"{'Created':<15} {user.get('created', 'N/A')}")
    print(f"{'Last Modified':<15} {user.get('lastModified', 'N/A')}")


def main():
    parser = argparse.ArgumentParser(description="Find a user by username or ID")
    parser.add_argument('identifier', help='Username or user ID to search for')
    parser.add_argument(
        '--by-id', 
        action='store_true',
        help='Search by user ID instead of username'
    )
    parser.add_argument(
        '--format', 
        choices=['json', 'table'], 
        default='table',
        help='Output format (default: table)'
    )
    args = parser.parse_args()
    
    try:
        # Initialize CatoSCIM client
        client = CatoSCIM()
        
        if args.by_id:
            print(f"Searching for user with ID '{args.identifier}' in SCIM service...", file=sys.stderr)
            
            # Find user by ID
            success, user = client.get_user(args.identifier)
            
            if not success:
                print(f"Error retrieving user: {user}", file=sys.stderr)
                sys.exit(1)
            
            print(f"Found user: {user.get('userName')}", file=sys.stderr)
            
            # Output in requested format
            if args.format == 'json':
                print(json.dumps(user, indent=2))
            else:  # table
                print_user_table(user)
        else:
            print(f"Searching for user '{args.identifier}' in SCIM service...", file=sys.stderr)
            
            # Find user by username
            success, users = client.find_users("userName", args.identifier)
            
            if not success:
                print(f"Error searching for user: {users}", file=sys.stderr)
                sys.exit(1)
            
            if not users:
                print(f"No user found with username: {args.identifier}", file=sys.stderr)
                sys.exit(1)
            
            if len(users) > 1:
                print(f"Warning: Found {len(users)} users with username {args.identifier}", file=sys.stderr)
            
            user = users[0]
            print(f"Found user: {user.get('userName')}", file=sys.stderr)
            
            # Output in requested format
            if args.format == 'json':
                print(json.dumps(user, indent=2))
            else:  # table
                print_user_table(user)
            
    except ValueError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        print("Ensure CATO_SCIM_URL and CATO_SCIM_TOKEN are set", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()