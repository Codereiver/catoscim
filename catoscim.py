#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
catoscim.py - Unofficial Cato Networks SCIM SDK

DISCLAIMER: This is an unofficial, community-developed SDK for the Cato Networks SCIM API.
           This is NOT an official Cato Networks release and is provided with no guarantees 
           of support. For official support, contact Cato Networks directly.

Version: 0.0
Author: Peter Lee, 2 May 2023
License: Provided as-is for demonstration purposes

This script is supplied as a demonstration of how to access the Cato SCIM API with Python.
It is not an official Cato release and is provided with no guarantees of support. Error handling
is restricted to the bare minimum required for the script to work with the API, and may not be
sufficient for production environments.

All questions or feedback about the Cato SCIM API should be sent to api@catonetworks.com
"""

import csv
import datetime
import json
import logging
import os
import secrets
import ssl
import string
import sys
import time
import urllib.parse
import urllib.request
import warnings
from urllib.error import HTTPError, URLError

# Try to import dotenv, but don't fail if it's not available
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file if it exists
except ImportError:
    pass  # dotenv not installed, will use system environment variables only

# Set up module-level logger
logger = logging.getLogger(__name__)


class CatoSCIM:
    """
    CatoSCIM - Unofficial SDK for Cato Networks SCIM API
    
    This is an unofficial, community-developed wrapper for SCIM API calls.
    Not an official Cato Networks product.
    """


    def __init__(self, baseurl=None, token=None, log_level='WARNING', verify_ssl=True):
        '''
        Initialise a Cato SCIM object. Members are:

        baseurl
            The URL of the SCIM service, as specified in CMA.
            If not provided, will look for CATO_SCIM_URL environment variable.
        token
            The authentication token for SCIM access, as specified in CMA.
            If not provided, will look for CATO_SCIM_TOKEN environment variable.
        log_level
            Logging level as string: 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
            or as integer for backwards compatibility.
        verify_ssl
            Controls SSL certificate verification. Set to False only for development.
            Default is True for security.
        call_count
            Running count of API calls made to the Cato SCIM endpoint.
        '''

        self.baseurl = baseurl or os.environ.get('CATO_SCIM_URL')
        self.token = token or os.environ.get('CATO_SCIM_TOKEN')
        
        if not self.baseurl:
            raise ValueError("SCIM URL must be provided either as parameter or via CATO_SCIM_URL environment variable")
        if not self.token:
            raise ValueError("SCIM token must be provided either as parameter or via CATO_SCIM_TOKEN environment variable")
        
        self.verify_ssl = verify_ssl
        self.call_count = 0
        
        # Configure module logger
        if isinstance(log_level, int):
            # Backwards compatibility: 0=CRITICAL+1, 1=ERROR, 2=INFO, 3=DEBUG
            level_map = {0: logging.CRITICAL + 1, 1: logging.ERROR, 2: logging.INFO, 3: logging.DEBUG}
            logger.setLevel(level_map.get(log_level, logging.DEBUG))
        else:
            logger.setLevel(getattr(logging, log_level.upper(), logging.WARNING))
        
        # Issue security warning if SSL verification is disabled
        if not self.verify_ssl:
            warnings.warn(
                "SSL certificate verification is disabled. This is INSECURE and should "
                "only be used in development environments. Never disable SSL verification "
                "in production!",
                SecurityWarning,
                stacklevel=2
            )
            logger.warning("SSL certificate verification is disabled - this is insecure!")
        
        logger.debug(f"Initialized CatoSCIM with baseurl: {self.baseurl}")




    def send(self, method="GET", path="/", request_data=None):
        '''
        Makes a REST request to the SCIM API.

        Parameters:
            method
                HTTP method to use (GET, POST, PUT, PATCH)
            path
                Path to the REST command being called, e.g. "/Users"
            data
                Optional JSON format message body for POST, PUT, PATCH

        Returns a tuple where the first element is a Boolean value indicating success or failure,
        and the second element is a string from the response. This function is not normally called
        directly by the user, but will be called by other functions which handle pagination and
        return data to the user as a Python object.
        '''
        logger.info(f'Sending {method} request to {path}')
        body = None
        if request_data is not None:
            logger.debug(f'Request data: {request_data}')
            body = json.dumps(request_data).encode('ascii')

        #
        # Construct the request headers
        #
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type':'application/json'
        }

        #
        # Create and send the request
        #
        try:
            request = urllib.request.Request(
                url = self.baseurl+path,
                headers = headers,
                method = method,
                data = body
            )
            self.call_count += 1
            
            # Handle SSL verification based on configuration
            if self.verify_ssl:
                # Use default SSL verification (secure)
                response = urllib.request.urlopen(request)
            else:
                # Disable SSL verification (development only)
                logger.warning("SSL verification disabled - this is insecure!")
                context = ssl._create_unverified_context()
                response = urllib.request.urlopen(request, context=context)
            
            result_data = response.read()
        except HTTPError as e:
            body = e.read().decode('utf-8', 'replace')
            return False, {"status":e.code, "error":body}
        except URLError as e:
            logger.error(f'Error sending request: {e}')
            return False, {"reason":e.reason, "error":str(e)}
        except Exception as e:
            logger.error(f'Error sending request: {e}')
            return False, {"error":str(e)}
        logger.debug(f'Response data: {result_data}')
        if result_data == b'': # DELETE returns an empty response
            result_data = b'{}'
        return True, json.loads(result_data.decode('utf-8','replace'))


    def add_members(self, groupid, members):
        '''
        Adds multiple members to an existing group. The members parameter must be a list of dictionaries:

        "members": [
            {
                "value": "6283630dfd7ec758a8bf4b61"
            },
            {
                "value": "6283630dfd7ec758a8bf4b62"
            }
        ]

        So each member is a dictionary with a value and display field. The value is the user id.

        Returns a tuple consisting of a Boolean success flag, and the response.
        '''

        logger.info(f'Adding members to group {groupid}')

        #
        # create the data object
        #
        data = {
            "schemas": [
                "urn:ietf:params:scim:api:messages:2.0:PatchOp"
            ],
            "Operations": [
                {
                    "op": "add",
                    "path": "members",
                    "value": members
                }
            ]
        }
        #
        # send the request
        #
        success, result = self.send("PATCH", f'/Groups/{groupid}', data)
        return success, result


    def create_group(self, displayName, externalId, members=None):
        '''
        Creates a new group. Caller must supply the group name and external ID 
        but the member list is optional. If members are to be created, the format must look like this:

        "members": [
            {
                "value": "6283630dfd7ec758a8bf4b61"
            },
            {
                "value": "6283630dfd7ec758a8bf4b62"
            }
        ]

        So each member is a dictionary with a value and display field. The value is the user id.

        Returns a tuple consisting of a Boolean success flag, and the response string.
        '''

        logger.info(f'Creating group: {displayName} (externalId: {externalId})')

        # Handle mutable default argument safely
        if members is None:
            members = []

        #
        # create the data object
        #
        data = {
            "schemas": [
                "urn:ietf:params:scim:schemas:core:2.0:Group"
            ],
            "displayName": displayName,
            "externalId": externalId,
            "members": members
        }

        #
        # send the request
        #
        success, result = self.send("POST", "/Groups", data)
        return success, result


    def create_user(self, email, givenName, familyName, externalId, password=None, active=True):
        '''
        Creates a new user. Caller must supply the email, givenName, familyName and externalId.

        Returns a tuple consisting of a Boolean success flag, and the response string.
        '''

        logger.info(f'Creating user: {email}')

        #
        # generate a strong password if none supplied
        #
        if password is None:
            new_password = ""
            for i in range(10):
                new_password += secrets.choice(string.ascii_letters+string.digits)
        else:
            new_password = password

        #
        # create the data object
        #
        data = {
            "schemas": [
                "urn:ietf:params:scim:schemas:core:2.0:User"
            ],
            "userName": email,
            "name": {
                "givenName": givenName,
                "familyName": familyName
            },
            "emails": [
                {
                    "primary": True,
                    "value": email
                }
            ],
            "externalId": externalId,
            "password": new_password,
            "active": active
        }

        #
        # send the request
        #
        success, result = self.send("POST", "/Users", data)
        return success, result


    def disable_group(self, groupid):
        '''
        Disables the group matching the given groupid. This is the Cato ID, not the SCIM service ID.

        Returns a Boolean success flag and a dictionary with the error or response.
        '''
        logger.info(f'Disabling group: {groupid}')
        return self.send("DELETE", f'/Groups/{groupid}')


    def disable_user(self, userid):
        '''
        Disables the user matching the given userid. This is the Cato ID, not the SCIM service ID.

        Returns a Boolean success flag and a dictionary with the error or response.
        '''
        logger.info(f'Disabling user: {userid}')
        return self.send("DELETE", f'/Users/{userid}')


    def find_group(self, displayName):
        '''
        Returns a Boolean success flag and a list of any matching groups. It should only ever return 0 or 1 groups.
        '''
        logger.info(f'Finding group by name: {displayName}')
        groups = []
        iteration = 0
        while True:

            #
            # Send the query and bail if error
            #
            iteration += 1
            filter_string = urllib.parse.quote(f'displayName eq "{displayName}"')
            success, response = self.send("GET", f'/Groups?filter={filter_string}&startIndex={len(groups)}')
            if not success:
                logger.error(f'Error retrieving groups: {response}')
                return False, response

            logger.debug(f'Group search iteration {iteration}: current={len(groups)}, received={len(response["Resources"])}, total={response["totalResults"]}')

            #
            # add new groups to the list
            #
            for group in response["Resources"]:
                groups.append(group)

            #
            # check for stop condition
            #
            if len(groups) >= response["totalResults"]:
                break

        return True, groups


    def find_users(self, field, value):
        '''
        Returns a Boolean success flag and a list of any matching users as JSON objects. Keeps iterating until all users are
        retrieved. Supported fields are:
            - userName
            - email
            - givenName
            - familyName
        '''
        logger.info(f'Finding users by {field}: {value}')
        users = []
        iteration = 0
        while True:

            #
            # Send the query and bail if error
            #
            iteration += 1
            filter_string = urllib.parse.quote(f'{field} eq "{value}"')
            success, response = self.send("GET", f'/Users?filter={filter_string}&startIndex={len(users)}')
            if not success:
                logger.error(f'Error retrieving users: {response}')
                return False, response

            logger.debug(f'User search iteration {iteration}: current={len(users)}, received={len(response["Resources"])}, total={response["totalResults"]}')

            #
            # add new users to the list
            #
            for user in response["Resources"]:
                users.append(user)

            #
            # check for stop condition
            #
            if len(users) >= response["totalResults"]:
                break

        return True, users


    def get_group(self, groupid):
        '''
        Gets a group by their ID. This is the Cato ID, not the SCIM service ID.

        Returns a Boolean success flag and a dictionary with the error or user details.
        '''
        logger.info(f'Getting group: {groupid}')
        return self.send("GET", f'/Groups/{groupid}')


    def get_groups(self):
        '''
        Returns a Boolean success flag and a list of all groups as JSON objects. Keeps iterating until all groups are
        retrieved.
        '''
        logger.info('Fetching all groups')
        groups = []
        iteration = 0
        while True:

            #
            # Send the query and bail if error
            #
            iteration += 1
            success, response = self.send("GET", f'/Groups?startIndex={len(groups)}')
            if not success:
                logger.error(f'Error retrieving groups: {response}')
                return False, response

            logger.debug(f'Groups fetch iteration {iteration}: current={len(groups)}, received={len(response["Resources"])}, total={response["totalResults"]}')

            #
            # add new groups to the list
            #
            for group in response["Resources"]:
                groups.append(group)

            #
            # check for stop condition
            #
            if len(groups) >= response["totalResults"]:
                break

        return True, groups


    def get_user(self, userid):
        '''
        Gets a user by their ID. This is the Cato ID, not the SCIM service ID.

        Returns a Boolean success flag and a dictionary with the error or user details.
        '''
        logger.info(f'Getting user: {userid}')
        return self.send("GET", f'/Users/{userid}')


    def get_users(self):
        '''
        Returns a Boolean success flag and a list of all users as JSON objects. Keeps iterating until all users are
        retrieved.
        '''
        logger.info('Fetching all users')
        users = []
        iteration = 0
        while True:

            #
            # Send the query and bail if error
            #
            iteration += 1
            success, response = self.send("GET", f'/Users?startIndex={len(users)}')
            if not success:
                logger.error(f'Error retrieving users: {response}')
                return False, response

            logger.debug(f'Users fetch iteration {iteration}: current={len(users)}, received={len(response["Resources"])}, total={response["totalResults"]}')

            #
            # add new users to the list
            #
            for user in response["Resources"]:
                users.append(user)

            #
            # check for stop condition
            #
            if len(users) >= response["totalResults"]:
                break

        return True, users


    def remove_members(self, groupid, members):
        '''
        Removes multiple members from an existing group. The members parameter must be a list of dictionaries:

        "members": [
            {
                "value": "6283630dfd7ec758a8bf4b61"
            },
            {
                "value": "6283630dfd7ec758a8bf4b62"
            }
        ]

        So each member is a dictionary with a value and display field. The value is the user id.

        Returns a tuple consisting of a Boolean success flag, and the response.
        '''

        logger.info(f'Removing members from group {groupid}')        

        #
        # create the data object
        #
        data = {
            "schemas": [
                "urn:ietf:params:scim:api:messages:2.0:PatchOp"
            ],
            "Operations": [
                {
                    "op": "remove",
                    "path": "members",
                    "value": members
                }
            ]
        }
        #
        # send the request
        #
        success, result = self.send("PATCH", f'/Groups/{groupid}', data)
        return success, result


    def rename_group(self, groupid, new_name):
        '''
        Renames an existing group.

        Returns a tuple consisting of a Boolean success flag, and the response.
        '''

        logger.info(f'Renaming group {groupid}')


        #
        # create the data object
        #
        data = {
            "schemas": [
                "urn:ietf:params:scim:api:messages:2.0:PatchOp"
            ],
            "Operations": [
                {
                    "op": "replace",
                    "path": "displayName",
                    "value": new_name
                }
            ]
        }
        #
        # send the request
        #
        success, result = self.send("PATCH", f'/Groups/{groupid}', data)
        return success, result


    def update_group(self, groupid, group_data):
        '''
        Updates an existing group. The group_data object is the complete group object returned by SCIM, supplied as a
        Python dictionary. Example:

            group_data = {
                "schemas": [
                    "urn:ietf:params:scim:schemas:core:2.0:Group"
                ],
                "displayName": "TEST group",
                "members": [
                    {
                        "value": "6283630dfd7ec758a8bf4b61",
                        "display": "joe.chip@cato.com"
                    },
                    {
                        "value": "6283630dfd7ec758a8bf4b62",
                        "display": "bob.dilen@cato.com"
                    },
                ]
            }

        Returns a tuple consisting of a Boolean success flag, and the response.
        '''

        logger.info(f'Updating group {groupid}')

        #
        # send the request
        #
        success, result = self.send("PUT", f'/Groups/{groupid}', group_data)
        return success, result


    def update_user(self, userid, user_data):
        '''
        Updates an existing user. The user_data object is the complete user object returned by SCIM, supplied as a
        Python dictionary. Example:

            user_data = {
                "schemas": [
                    "urn:ietf:params:scim:schemas:core:2.0:User"
                ],
                "created": "2022-03-20T07:04:41.514Z",
                "lastModified": "2022-03-20T07:04:41.514Z",
                "id": "6236d20907a2c5128551028f",
                "externalId": "00u3bbaucx0satWBP357",
                "userName": "joe.chip@cato.com",
                "name": {
                    "givenName": "joe",
                    "familyName": "chip"
                },
                "active": true,
                "emails": [
                    {
                        "primary": true,
                        "value": "joe.chip@cato.com",
                        "type": "work"
                    }
                ],
                "phoneNumbers": [
                    {
                        "primary": true,
                        "type": "work",
                        "value": "0523444332"
                    }
                ],
                "displayName": "Joe Chip",
            }

        Returns a tuple consisting of a Boolean success flag, and the response string.
        '''

        logger.info(f'Updating user {userid}')

        #
        # send the request
        #
        success, result = self.send("PUT", f'/Users/{userid}', user_data)
        return success, result

