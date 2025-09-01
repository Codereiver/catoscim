#!/usr/bin/env python3
"""
Update user password example

This script demonstrates how to update a user's password by their username using the SCIM service.
Requires CATO_SCIM_URL and CATO_SCIM_TOKEN environment variables or a .env file.

Usage:
    python3 examples/update_password.py <username> <new_password>
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


def update_user_password(client, username, new_password):
    """Update a user's password."""
    # Find the user first
    user, error = find_user_by_username(client, username)
    if error:
        return False, error
    
    # Get the full user details
    success, full_user = client.get_user(user["id"])
    if not success:
        return False, f"Error retrieving user details: {full_user}"
    
    # Update the password in the user data
    full_user["password"] = new_password
    
    # Update the user
    success, result = client.update_user(user["id"], full_user)
    
    if not success:
        return False, f"Error updating user password: {result}"
    
    return True, f"Successfully updated password for user: {username}"


def main():
    parser = argparse.ArgumentParser(description="Update a user's password")
    parser.add_argument('username', help='Username of the user to update')
    parser.add_argument('password', help='New password for the user')
    
    args = parser.parse_args()
    
    try:
        # Initialize CatoSCIM client
        client = CatoSCIM()
        print(f"Updating password for user '{args.username}'...", file=sys.stderr)
        
        success, message = update_user_password(client, args.username, args.password)
        
        if not success:
            print(f"Error: {message}", file=sys.stderr)
            sys.exit(1)
        
        print(message)
        print(f"✓ Password updated successfully for {args.username}")
            
    except ValueError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        print("Ensure CATO_SCIM_URL and CATO_SCIM_TOKEN are set", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()