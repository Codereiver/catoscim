#!/usr/bin/env python3
"""
Manage group membership example

This script demonstrates how to add or remove users from groups in the Cato SCIM service.
Requires CATO_SCIM_URL and CATO_SCIM_TOKEN environment variables or a .env file.

Usage:
    python3 examples/group_membership.py add <group_name> <username>
    python3 examples/group_membership.py remove <group_name> <username>
    python3 examples/group_membership.py list <group_name>
"""

import sys
import os
import argparse
import json

# Add parent directory to import catoscim
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from catoscim import CatoSCIM


def find_group_by_name(client, group_name):
    """Find a group by display name."""
    success, groups = client.find_group(group_name)
    if not success:
        return None, f"Error searching for group: {groups}"
    
    if not groups:
        return None, f"No group found with name: {group_name}"
    
    if len(groups) > 1:
        return None, f"Multiple groups found with name: {group_name}"
    
    return groups[0], None


def find_user_by_username(client, username):
    """Find a user by username."""
    success, users = client.find_users("userName", username)
    if not success:
        return None, f"Error searching for user: {users}"
    
    if not users:
        return None, f"No user found with username: {username}"
    
    if len(users) > 1:
        return None, f"Multiple users found with username: {username}"
    
    return users[0], None


def add_member(client, group_name, username):
    """Add a user to a group."""
    # Find the group
    group, error = find_group_by_name(client, group_name)
    if error:
        return False, error
    
    # Find the user
    user, error = find_user_by_username(client, username)
    if error:
        return False, error
    
    # Add the user to the group
    members = [{"value": user["id"], "display": user["userName"]}]
    success, result = client.add_members(group["id"], members)
    
    if not success:
        return False, f"Error adding user to group: {result}"
    
    return True, f"Successfully added {username} to group {group_name}"


def remove_member(client, group_name, username):
    """Remove a user from a group."""
    # Find the group
    group, error = find_group_by_name(client, group_name)
    if error:
        return False, error
    
    # Find the user
    user, error = find_user_by_username(client, username)
    if error:
        return False, error
    
    # Remove the user from the group
    members = [{"value": user["id"], "display": user["userName"]}]
    success, result = client.remove_members(group["id"], members)
    
    if not success:
        return False, f"Error removing user from group: {result}"
    
    return True, f"Successfully removed {username} from group {group_name}"


def list_members(client, group_name):
    """List all members of a group."""
    # Find the group
    group, error = find_group_by_name(client, group_name)
    if error:
        return False, error
    
    # Get full group details with members
    success, full_group = client.get_group(group["id"])
    if not success:
        return False, f"Error retrieving group details: {full_group}"
    
    members = full_group.get("members", [])
    if not members:
        return True, f"Group '{group_name}' has no members"
    
    member_list = []
    for member in members:
        member_id = member.get("value")
        member_display = member.get("display", "")
        
        # If no display name, try to look up the user
        if not member_display and member_id:
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
        
        member_list.append({
            "id": member_id,
            "display": member_display
        })
    
    return True, {"group": group_name, "members": member_list}


def main():
    parser = argparse.ArgumentParser(description="Manage group membership")
    parser.add_argument('action', choices=['add', 'remove', 'list'], help='Action to perform')
    parser.add_argument('group_name', help='Group display name')
    parser.add_argument('username', nargs='?', help='Username (required for add/remove)')
    
    args = parser.parse_args()
    
    if args.action in ['add', 'remove'] and not args.username:
        parser.error(f"username is required for {args.action} action")
    
    try:
        # Initialize CatoSCIM client
        client = CatoSCIM()
        print(f"Performing {args.action} operation on group '{args.group_name}'...", file=sys.stderr)
        
        if args.action == 'add':
            success, message = add_member(client, args.group_name, args.username)
        elif args.action == 'remove':
            success, message = remove_member(client, args.group_name, args.username)
        else:  # list
            success, message = list_members(client, args.group_name)
        
        if not success:
            print(f"Error: {message}", file=sys.stderr)
            sys.exit(1)
        
        if args.action == 'list' and isinstance(message, dict):
            print(f"Members of group '{message['group']}':")
            for member in message['members']:
                print(f"  - {member['display']} (ID: {member['id']})")
        else:
            print(message)
            
    except ValueError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        print("Ensure CATO_SCIM_URL and CATO_SCIM_TOKEN are set", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()