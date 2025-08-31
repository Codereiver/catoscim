#!/usr/bin/env python3
"""
List all SCIM groups example

This script demonstrates how to retrieve and display all groups from the Cato SCIM service.
Requires CATO_SCIM_URL and CATO_SCIM_TOKEN environment variables or a .env file.

Usage:
    python3 examples/list_groups.py [--format csv|json|table]
"""

import sys
import os
import argparse
import json

# Add parent directory to import catoscim
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from catoscim import CatoSCIM


def print_groups_table(groups):
    """Print groups in a formatted table."""
    if not groups:
        print("No groups found.")
        return
    
    print(f"{'ID':<25} {'Display Name':<30} {'External ID':<20} {'Members':<8}")
    print("-" * 83)
    
    for group in groups:
        group_id = group.get('id', 'N/A')[:24]
        display_name = group.get('displayName', 'N/A')[:29]
        external_id = group.get('externalId', 'N/A')[:19]
        member_count = len(group.get('members', []))
        
        print(f"{group_id:<25} {display_name:<30} {external_id:<20} {member_count:<8}")


def print_groups_csv(groups):
    """Print groups in CSV format."""
    print("id,displayName,externalId,member_count")
    for group in groups:
        group_id = group.get('id', '')
        display_name = group.get('displayName', '')
        external_id = group.get('externalId', '')
        member_count = len(group.get('members', []))
        
        print(f"{group_id},{display_name},{external_id},{member_count}")


def main():
    parser = argparse.ArgumentParser(description="List all SCIM groups")
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
        
        # Get all groups
        success, groups = client.get_groups()
        
        if not success:
            print(f"Error retrieving groups: {groups}", file=sys.stderr)
            sys.exit(1)
        
        print(f"Retrieved {len(groups)} groups", file=sys.stderr)
        
        # Output in requested format
        if args.format == 'csv':
            print_groups_csv(groups)
        elif args.format == 'json':
            print(json.dumps(groups, indent=2))
        else:  # table
            print_groups_table(groups)
            
    except ValueError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        print("Ensure CATO_SCIM_URL and CATO_SCIM_TOKEN are set", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()