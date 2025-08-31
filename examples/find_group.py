#!/usr/bin/env python3
"""
Find group by name or ID example

This script demonstrates how to find a specific group by their display name or ID using the SCIM service.
Requires CATO_SCIM_URL and CATO_SCIM_TOKEN environment variables or a .env file.

Usage:
    python3 examples/find_group.py <group_name_or_id> [--by-id] [--format json|table]
"""

import sys
import os
import argparse
import json

# Add parent directory to import catoscim
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from catoscim import CatoSCIM


def print_group_table(group, client=None):
    """Print group details in a formatted table."""
    print(f"{'Field':<15} {'Value'}")
    print("-" * 60)
    
    print(f"{'ID':<15} {group.get('id', 'N/A')}")
    print(f"{'Display Name':<15} {group.get('displayName', 'N/A')}")
    print(f"{'External ID':<15} {group.get('externalId', 'N/A')}")
    print(f"{'Created':<15} {group.get('created', 'N/A')}")
    print(f"{'Last Modified':<15} {group.get('lastModified', 'N/A')}")
    
    members = group.get('members', [])
    print(f"{'Member Count':<15} {len(members)}")
    
    if members:
        print(f"{'Members':<15}")
        for i, member in enumerate(members):
            member_id = member.get('value', 'N/A')
            member_display = member.get('display', '')
            
            # If no display name and we have a client, try to look up the user
            if not member_display and client and member_id != 'N/A':
                try:
                    success, user = client.get_user(member_id)
                    if success:
                        member_display = user.get('userName', member_id)
                    else:
                        member_display = member_id
                except:
                    member_display = member_id
            elif not member_display:
                member_display = member_id
            
            prefix = "├─" if i < len(members) - 1 else "└─"
            if member_display == member_id:
                # Don't repeat the ID if it's the same as display
                print(f"{'  ' + prefix:<15} {member_display}")
            else:
                print(f"{'  ' + prefix:<15} {member_display} (ID: {member_id})")


def main():
    parser = argparse.ArgumentParser(description="Find a group by display name or ID")
    parser.add_argument('identifier', help='Group display name or group ID to search for')
    parser.add_argument(
        '--by-id', 
        action='store_true',
        help='Search by group ID instead of display name'
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
            print(f"Searching for group with ID '{args.identifier}' in SCIM service...", file=sys.stderr)
            
            # Find group by ID
            success, group = client.get_group(args.identifier)
            
            if not success:
                print(f"Error retrieving group: {group}", file=sys.stderr)
                sys.exit(1)
            
            print(f"Found group: {group.get('displayName')}", file=sys.stderr)
            
            # Output in requested format
            if args.format == 'json':
                print(json.dumps(group, indent=2))
            else:  # table
                print_group_table(group, client)
        else:
            print(f"Searching for group '{args.identifier}' in SCIM service...", file=sys.stderr)
            
            # Find group by display name
            success, groups = client.find_group(args.identifier)
            
            if not success:
                print(f"Error searching for group: {groups}", file=sys.stderr)
                sys.exit(1)
            
            if not groups:
                print(f"No group found with display name: {args.identifier}", file=sys.stderr)
                sys.exit(1)
            
            if len(groups) > 1:
                print(f"Warning: Found {len(groups)} groups with display name {args.identifier}", file=sys.stderr)
            
            # Get full group details with members
            group_id = groups[0]['id']
            success, group = client.get_group(group_id)
            
            if not success:
                print(f"Error retrieving full group details: {group}", file=sys.stderr)
                sys.exit(1)
            
            print(f"Found group: {group.get('displayName')}", file=sys.stderr)
            
            # Output in requested format
            if args.format == 'json':
                print(json.dumps(group, indent=2))
            else:  # table
                print_group_table(group, client)
            
    except ValueError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        print("Ensure CATO_SCIM_URL and CATO_SCIM_TOKEN are set", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()