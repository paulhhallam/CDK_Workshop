

from constructs import Construct
"""
AWS CDK Stack for a serverless application with API Gateway and hit counting.

This stack creates a Lambda function that handles HTTP requests through API Gateway,
tracks the number of hits using DynamoDB, and provides a web interface to view hit counts.

Components:
    - HelloHandler: Python Lambda function that processes incoming requests
    - HelloHitCounter: HitCounter construct that wraps the Lambda and tracks invocations
    - Endpoint: API Gateway REST API connected to the hit counter
    - ViewHitCounter: TableViewer for visualizing hit count metrics

Attributes:
    None
"""

from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
)

from cdk_dynamo_table_view import TableViewer
from hitcounter import HitCounter

class CdkWorkshopStack(Stack):
"""Stack for the CDK Workshop application."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        my_lambda = _lambda.Function(
            self, 'HelloHandler',
            runtime=_lambda.Runtime.PYTHON_3_13,
            code=_lambda.Code.from_asset('lambda'),
            handler='hello.handler',
        )

        hello_with_counter = HitCounter(
            self, 'HelloHitCounter',
            downstream=my_lambda,
        )

        apigw.LambdaRestApi(
            self, 'Endpoint',
            handler=hello_with_counter._handler,
        )   

        TableViewer(
            self, 'ViewHitCounter',
            title='Hello Hits',
            table=hello_with_counter.table
        )


