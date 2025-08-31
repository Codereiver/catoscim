# catoscim.py
#
# Version: 0.0
# Author: Peter Lee, 2 May 2023
#
# Changes since 0.0:
#   - 
#
# This script is supplied as a demonstration of how to access the Cato SCIM API with Python. It
# is not an official Cato release and is provided with no guarantees of support. Error handling
# is restricted to the bare minimum required for the script to work with the API, and may not be
# sufficient for production environments.
#
# All questions or feedback should be sent to api@catonetworks.com

import csv
import datetime
import json
import os
import secrets
import ssl
import string
import sys
import time
import urllib.parse
import urllib.request
from urllib.error import HTTPError, URLError

# Try to import dotenv, but don't fail if it's not available
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file if it exists
except ImportError:
    pass  # dotenv not installed, will use system environment variables only


class CatoSCIM:
    '''
    class CatoSCIM

    Wrapper for SCIM API calls. Initialisation
    '''


    def __init__(self, baseurl=None, token=None, log_level=0):
        '''
        Initialise a Cato SCIM object. Members are:

        baseurl
            The URL of the SCIM service, as specified in CMA.
            If not provided, will look for CATO_SCIM_URL environment variable.
        token
            The authentication token for SCIM access, as specified in CMA.
            If not provided, will look for CATO_SCIM_TOKEN environment variable.
        log_level
            Controls the printing of log messages. Messages with a level >= this value
            will be printed. Set to 0 (default) to print no log.
        call_count
            Running count of API calls made to the Cato SCIM endpoint.
        '''

        self.baseurl = baseurl or os.environ.get('CATO_SCIM_URL')
        self.token = token or os.environ.get('CATO_SCIM_TOKEN')
        
        if not self.baseurl:
            raise ValueError("SCIM URL must be provided either as parameter or via CATO_SCIM_URL environment variable")
        if not self.token:
            raise ValueError("SCIM token must be provided either as parameter or via CATO_SCIM_TOKEN environment variable")
        
        self.log_level = log_level
        self.call_count = 0
        self.start = datetime.datetime.utcnow()


    def log(self,level,*items):
        '''
        Prints a log message, but only if the message level >= CatoSCIM.log_level. By default this
        is 0 and all log messages have a level > 0, so the default is for no log messages to be printed.
        '''
        if level <= self.log_level:
            print(f'LOG{level} {datetime.datetime.utcnow()} +{self.elapsed()} {self.call_count}>',*items)


    def elapsed(self):
        '''
        Returns a datetime.timedelta of the elapsed time from __init__ to now.
        '''
        return datetime.datetime.utcnow()-self.start


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
        self.log(2,f'send {method} {path}')
        body = None
        if request_data is not None:
            self.log(3, f'data:\n{request_data}')
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
            no_verify = ssl._create_unverified_context()
            response = urllib.request.urlopen(request, context=no_verify)
            result_data = response.read()
        except HTTPError as e:
            body = e.read().decode('utf-8', 'replace')
            return False, {"status":e.code, "error":body}
        except URLError as e:
            self.log(1,f'Error sending request: {e}')
            return False, {"reason":e.reason, "error":str(e)}
        except Exception as e:
            self.log(1,f'Error sending request: {e}')
            return False, {"error":str(e)}
        self.log(3,f'result_data: {result_data}')
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

        #
        # log the function call
        #
        self.log(1, f'add_members({groupid})')

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


    def create_group(self, displayName, externalId, members=[]):
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

        #
        # log the function call
        #
        self.log(1, f'create_group({displayName}, {externalId})')

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

        #
        # log the function call
        #
        self.log(1, f'create_user({email})')

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
        self.log(1,f'disable_group({groupid})')
        return self.send("DELETE", f'/Groups/{groupid}')


    def disable_user(self, userid):
        '''
        Disables the user matching the given userid. This is the Cato ID, not the SCIM service ID.

        Returns a Boolean success flag and a dictionary with the error or response.
        '''
        self.log(1,f'disable_user({userid})')
        return self.send("DELETE", f'/Users/{userid}')


    def find_group(self, displayName):
        '''
        Returns a Boolean success flag and a list of any matching groups. It should only ever return 0 or 1 groups.
        '''
        self.log(1,f'find_group({displayName})')
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
                self.log(1, f'Error retrieving users: {response}')
                return False, response

            #
            # log
            #
            self.log(1,f'Iteration:{iteration} Current_count:{len(groups)} Received_count:{len(response["Resources"])} totalResults:{response["totalResults"]}')

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
        self.log(1,f'find_users({field},{value})')
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
                self.log(1, f'Error retrieving users: {response}')
                return False, response

            #
            # log
            #
            self.log(1,f'Iteration:{iteration} Current_count:{len(users)} Received_count:{len(response["Resources"])} totalResults:{response["totalResults"]}')

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
        self.log(1,f'get_group({groupid})')
        return self.send("GET", f'/Groups/{groupid}')


    def get_groups(self):
        '''
        Returns a Boolean success flag and a list of all groups as JSON objects. Keeps iterating until all groups are
        retrieved.
        '''
        self.log(1,"get_groups()")
        groups = []
        iteration = 0
        while True:

            #
            # Send the query and bail if error
            #
            iteration += 1
            success, response = self.send("GET", f'/Groups?startIndex={len(groups)}')
            if not success:
                self.log(1, f'Error retrieving groups: {response}')
                return False, response

            #
            # log
            #
            self.log(1,f'Iteration:{iteration} Current_count:{len(groups)} Received_count:{len(response["Resources"])} totalResults:{response["totalResults"]}')

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
        self.log(1,f'get_user({userid})')
        return self.send("GET", f'/Users/{userid}')


    def get_users(self):
        '''
        Returns a Boolean success flag and a list of all users as JSON objects. Keeps iterating until all users are
        retrieved.
        '''
        self.log(1,"get_users()")
        users = []
        iteration = 0
        while True:

            #
            # Send the query and bail if error
            #
            iteration += 1
            success, response = self.send("GET", f'/Users?startIndex={len(users)}')
            if not success:
                self.log(1, f'Error retrieving users: {response}')
                return False, response

            #
            # log
            #
            self.log(1,f'Iteration:{iteration} Current_count:{len(users)} Received_count:{len(response["Resources"])} totalResults:{response["totalResults"]}')

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

        #
        # log the function call
        #
        self.log(1, f'remove_members({groupid})')        

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

        #
        # log the function call
        #
        self.log(1, f'rename_group({groupid})')


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

        #
        # log the function call
        #
        self.log(1, f'update_group({groupid})')

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

        #
        # log the function call
        #
        self.log(1, f'update_user({userid})')

        #
        # send the request
        #
        success, result = self.send("PUT", f'/Users/{userid}', user_data)
        return success, result

