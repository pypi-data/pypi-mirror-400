from moto import mock_aws

from cfddb.dynamodb.client import DynamoClient
from cfddb.engine.executor import Executor
from cfddb.engine.planner import Planner

# Define a template that uses standard features (no multi-attribute keys)
# to verify the general "happy path" of your tool.
INTEGRATION_TEMPLATE = """
AWSTemplateFormatVersion: '2010-09-09'
Parameters:
  Env:
    Type: String
    Default: test

Resources:
  MotoTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub "cfddb-${Env}-Moto"
      AttributeDefinitions:
        - AttributeName: pk
          AttributeType: S
        - AttributeName: sk
          AttributeType: S
      KeySchema:
        - AttributeName: pk
          KeyType: HASH
        - AttributeName: sk
          KeyType: RANGE
      GlobalSecondaryIndexes:
        - IndexName: GSI1
          KeySchema:
            - AttributeName: sk
              KeyType: HASH
            - AttributeName: pk
              KeyType: RANGE
          Projection:
            ProjectionType: ALL
      BillingMode: PAY_PER_REQUEST
      # Moto supports TTL, so we can test this too
      TimeToLiveSpecification:
        AttributeName: expireAt
        Enabled: true
"""


@mock_aws
def test_end_to_end_with_moto(tmp_path):
    template_path = tmp_path / "moto.yaml"
    template_path.write_text(INTEGRATION_TEMPLATE)

    # Moto intercepts all boto3 calls, so credentials/endpoint don't matter,
    # but we pass dummy ones to satisfy the client init.
    client = DynamoClient(
        endpoint=None,
        region="eu-central-1",
        aws_access_key_id="testing",
        aws_secret_access_key="testing",
    )
    planner = Planner(
        template=template_path,
        parameter_overrides={"Env": "qa"},
        dynamodb_client=client,
    )

    plan = planner.create_plan()

    # Expect: Create Table + Update TTL
    assert len(plan.actions) == 2
    assert plan.actions[0].type == "Create"
    assert plan.actions[1].type == "Update_TTL"

    executor = Executor(client)
    executor.apply(plan)

    table_name = "cfddb-qa-Moto"
    desc = client.ddb.describe_table(TableName=table_name)["Table"]
    assert desc["TableStatus"] == "ACTIVE"
    assert desc["GlobalSecondaryIndexes"][0]["IndexName"] == "GSI1"

    ttl = client.ddb.describe_time_to_live(TableName=table_name)
    assert ttl["TimeToLiveDescription"]["TimeToLiveStatus"] == "ENABLED"

    # Run the planner again. Since the table exists and TTL is enabled,
    # it should produce 0 actions.
    plan_v2 = planner.create_plan()

    assert len(plan_v2.actions) == 0
