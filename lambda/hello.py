
"""
AWS Lambda handler function for HTTP requests.

This function processes incoming API Gateway events and returns a formatted
HTTP response with the requested path information.

Args:
    event (dict): The Lambda event object containing request data from API Gateway.
                  Expected to include a 'path' key with the request path.
    context (object): The Lambda context object providing runtime information
                      and methods for interacting with CloudWatch Logs.

Returns:
    dict: An HTTP response object with:
        - statusCode (int): HTTP status code (200 for success)
        - headers (dict): Response headers including Content-Type
        - body (str): Response body containing a greeting and the request path
"""

import json

def handler(event, context):
    """Sample Lambda function handler."""

    print('request: {}'.format(json.dumps(event)))
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/plain'
        },
        'body': 'Hello, CDK! You have hit {}\n'.format(event['path'])
    }