
""" 
    AWS Lambda handler that tracks page hits and invokes a downstream Lambda function.
    This function updates a DynamoDB table to increment hit counts for a given path,
    then invokes another Lambda function with the same event payload.

    Args:
        event (dict): The Lambda event object containing:
            - path (str): The request path to track hits for
        context (LambdaContext): The Lambda context object
        
    Returns:
        dict: The parsed JSON response from the downstream Lambda function invocation
        
    Environment Variables:
        HITS_TABLE_NAME (str): Name of the DynamoDB table to store hit counts
        DOWNSTREAM_FUNCTION_NAME (str): Name of the downstream Lambda function to invoke
        
    Side Effects:
        - Updates DynamoDB table with incremented hit count for the path
        - Invokes another Lambda function asynchronously
        - Logs the incoming request and downstream response
"""

import json
import os

import boto3

ddb = boto3.resource('dynamodb')
table = ddb.Table(os.environ['HITS_TABLE_NAME'])
_lambda = boto3.client('lambda')

def handler(event, context):
    """ Lambda function handler to count hits and invoke downstream function. """
    print('request: {}'.format(json.dumps(event)))
    table.update_item(
        Key={'path': event['path']},
        UpdateExpression='ADD hits :incr',
        ExpressionAttributeValues={':incr': 1}
    )

    resp = _lambda.invoke(
        FunctionName=os.environ['DOWNSTREAM_FUNCTION_NAME'],
        Payload=json.dumps(event)
    )

    body = resp['Payload'].read()

    print('downstream response: {}'.format(body))
    return json.loads(body)
