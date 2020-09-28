"""
**********************************************************************************************************************
 *  Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved                                            *
 *                                                                                                                    *
 *  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated      *
 *  documentation files (the "Software"), to deal in the Software without restriction, including without limitation   *
 *  the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and  *
 *  to permit persons to whom the Software is furnished to do so.                                                     *
 *                                                                                                                    *
 *  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO  *
 *  THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE    *
 *  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF         *
 *  CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS *
 *  IN THE SOFTWARE.                                                                                                  *
 **********************************************************************************************************************
"""

import logging
import os
import json
from salesforce import Salesforce

def lambda_handler(event, context):
    # Uncomment the following line for debugging
    # print(event)

    # Establsih an empty response
    response = {}
    # Set the default result to success
    response.update({'result':'success'})

    # Handle EventBridge pings that keep the function warm
    if 'source' in event:
        response.update({'statusCode': 200,'response' : 'warm', 'event' : 'EventBridge ping'})
        return response

    # Extract passed params and build query
    try:
        sf_user_field = os.environ['sf_user_field']
        sf_phone_field = os.environ['sf_phone_field']
        sf_follow_field = os.environ['sf_follow_field']
        sf_deployment_mode = os.environ['sf_deployment_mode']
        sf_username = event['Details']['Parameters']['username']

        if sf_deployment_mode == 'cti':
            sf_query = "SELECT Id, " + sf_phone_field + ", " + sf_follow_field + " FROM User WHERE " + sf_user_field + " ='" + sf_username + "'"

        elif sf_deployment_mode == 'scv':
            sf_username = sf_username.split('@',1)[0]
            sf_query = "SELECT " + sf_phone_field + ", " + sf_follow_field + " FROM User WHERE Id = '" + sf_username + "'"

        # Login to Salesforce
        try:
            sf = Salesforce()
            sf.sign_in()

            # Do the Query
            try:
                query_result = sf.query(query=sf_query)

                # Prep the response
                response.update({'Callback' : query_result[0][sf_phone_field]})
                response.update({'FollowMe' : str(query_result[0][sf_follow_field])})

            except:
                response.update({'result':'fail', 'code' : 'SF Query Fail'})

        except:
            response.update({'result':'fail', 'code' : 'SF Login Fail'})

    except:
        response.update({'result':'fail', 'code' : 'Query failed to build'})

    return response
