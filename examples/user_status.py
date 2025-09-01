#!/usr/bin/env python3
"""
Enable/disable user example

This script demonstrates how to enable or disable a user by their username using the SCIM service.
Requires CATO_SCIM_URL and CATO_SCIM_TOKEN environment variables or a .env file.

Usage:
    python3 examples/user_status.py <action> <username>
    
Actions:
    enable   - Enable (activate) the user account
    disable  - Disable (deactivate) the user account
    status   - Show current status of the user account
"""

import sys
import os
import argparse

# Add parent directory to import catoscim
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from catoscim import CatoSCIM


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


def get_user_status(client, username):
    """Get the current status of a user."""
    # Find the user first
    user, error = find_user_by_username(client, username)
    if error:
        return False, error
    
    # Get the full user details
    success, full_user = client.get_user(user["id"])
    if not success:
        return False, f"Error retrieving user details: {full_user}"
    
    is_active = full_user.get("active", False)
    status = "enabled" if is_active else "disabled"
    
    return True, {
        "username": username,
        "user_id": user["id"],
        "status": status,
        "active": is_active
    }


def update_user_status(client, username, enable=True):
    """Enable or disable a user."""
    # Find the user first
    user, error = find_user_by_username(client, username)
    if error:
        return False, error
    
    # Get the full user details
    success, full_user = client.get_user(user["id"])
    if not success:
        return False, f"Error retrieving user details: {full_user}"
    
    # Check current status
    current_status = full_user.get("active", False)
    action = "enable" if enable else "disable"
    
    if current_status == enable:
        status_word = "enabled" if enable else "disabled"
        return True, f"User {username} is already {status_word}"
    
    # Update the active status
    full_user["active"] = enable
    
    # Update the user
    success, result = client.update_user(user["id"], full_user)
    
    if not success:
        return False, f"Error {action}ing user: {result}"
    
    status_word = "enabled" if enable else "disabled"
    return True, f"Successfully {status_word} user: {username}"


def main():
    parser = argparse.ArgumentParser(description="Enable, disable, or check status of a user")
    parser.add_argument('action', choices=['enable', 'disable', 'status'], 
                       help='Action to perform: enable, disable, or status')
    parser.add_argument('username', help='Username of the user to modify')
    
    args = parser.parse_args()
    
    try:
        # Initialise CatoSCIM client
        client = CatoSCIM()
        
        if args.action == 'status':
            print(f"Checking status for user '{args.username}'...", file=sys.stderr)
            success, result = get_user_status(client, args.username)
            
            if not success:
                print(f"Error: {result}", file=sys.stderr)
                sys.exit(1)
            
            print(f"User: {result['username']}")
            print(f"Status: {result['status']}")
            print(f"Active: {result['active']}")
            
        else:
            action_word = "Enabling" if args.action == 'enable' else "Disabling"
            print(f"{action_word} user '{args.username}'...", file=sys.stderr)
            
            enable = (args.action == 'enable')
            success, message = update_user_status(client, args.username, enable)
            
            if not success:
                print(f"Error: {message}", file=sys.stderr)
                sys.exit(1)
            
            print(message)
            status_symbol = "✓" if enable else "✗"
            action_past = "enabled" if enable else "disabled"
            print(f"{status_symbol} User {args.username} has been {action_past}")
            
    except ValueError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        print("Ensure CATO_SCIM_URL and CATO_SCIM_TOKEN are set", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()