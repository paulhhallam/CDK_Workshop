
"""
HitCounter Construct

A reusable AWS CDK Construct that deploys a Lambda-based hit counter in front of a downstream
Lambda function. Each invocation of the hit-counter Lambda increments a counter stored in a
DynamoDB table and then invokes the specified downstream function. This pattern is useful for
recording invocation metrics or rate-limiting/pre-processing before forwarding requests.

Behavior
- Creates a DynamoDB table named "Hits" with partition key "path" (string) and AWS-managed
    encryption.
- Deploys a Lambda function (the "hit counter handler") with environment variables:
        - DOWNSTREAM_FUNCTION_NAME: name of the downstream Lambda to invoke
        - HITS_TABLE_NAME: name of the DynamoDB table used for hit storage
- Grants the handler read/write permissions on the DynamoDB table and invoke permission on the
    downstream function.
- Adds an explicit invoke permission entry on the downstream function scoped by the caller
    account and the handler's ARN (to limit the allowed invokers).

Parameters
- scope (Construct): The parent CDK construct.
- id (str): The logical ID of this construct within the CDK app.
- downstream (_lambda.IFunction): The downstream Lambda function that will be invoked by the
    hit counter handler.
- **kwargs: Additional keyword args forwarded to the Construct base class.

Attributes (exposed as read-only properties)
- handler (_lambda.Function): The deployed Lambda function that performs counting and forwards
    requests to the downstream function.
- table (ddb.Table): The DynamoDB table used to store hit counts keyed by "path".

Usage example
        hit_counter = HitCounter(self, "MyHitCounter", downstream=my_downstream_function)
        # Read the handler or table if further configuration is needed:
        # lambda_fn = hit_counter.handler
        # hits_table = hit_counter.table

Notes and considerations
- The construct assumes the handler code is provided in the 'lambda' asset directory and that the
    handler entry point is 'hitcount.handler'.
- Ensure IAM principals and account values are correctly available in the deployment environment
    (the construct consults the CDK app's root account/node to scope permissions).
- Adjust runtime and asset packaging to match your handler implementation and CDK runtime support.
"""

from constructs import Construct
from aws_cdk import (
    aws_lambda as _lambda,
    aws_dynamodb as ddb,
    aws_iam as iam,
)

class HitCounter(Construct):
"""Lambda function that counts hits to a downstream function."""

    @property
    def handler(self):
"""Function handler."""
       return self._handler

    @property
    def table(self):
"""Hits table."""
       return self._table

    def __init__(self, scope: Construct, id: str, downstream: _lambda.IFunction, **kwargs):
        super().__init__(scope, id, **kwargs)
"""Construct a HitCounter."""

        self._table = ddb.Table(
            self, 'Hits',
            partition_key={'name': 'path', 'type': ddb.AttributeType.STRING},
            encryption=ddb.TableEncryption.AWS_MANAGED
        )   

       self._handler = _lambda.Function(
            self, 'HitCounterHandler',
            runtime=_lambda.Runtime.PYTHON_3_13,
            code=_lambda.Code.from_asset('lambda'),
            handler='hitcount.handler',
            environment={
                'DOWNSTREAM_FUNCTION_NAME': downstream.function_name,
                'HITS_TABLE_NAME': self._table.table_name,
            }
        )

        self._table.grant_read_write_data(self._handler)
        downstream.grant_invoke(self._handler)

        # Grant invoke permission with source account condition
        downstream.add_permission(
            'AllowHitCounterInvoke',
            principal=iam.ServicePrincipal('lambda.amazonaws.com'),
            action='lambda:InvokeFunction',
            source_account=self.node.root.account,
            source_arn=self._handler.function_arn
        )
        self._table.grant_read_write_data(self._handler)

