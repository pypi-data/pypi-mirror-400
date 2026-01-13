import boto3
from botocore.waiter import WaiterModel, create_waiter_with_client

from cfddb.dynamodb.tables import DynamoTableSpec


class DynamoClient:
    def __init__(self, endpoint, region, aws_access_key_id, aws_secret_access_key):
        self.ddb = boto3.client(
            "dynamodb",
            endpoint_url=endpoint,
            region_name=region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )

    def describe(self, table_name):
        try:
            return self.ddb.describe_table(TableName=table_name)["Table"]
        except self.ddb.exceptions.ResourceNotFoundException:
            return None

    def create(self, spec: DynamoTableSpec):
        specs = spec.create_payload()
        self.ddb.create_table(**specs)

    def add_gsis(self, table_name, attrs, updates):
        self.ddb.update_table(
            TableName=table_name,
            AttributeDefinitions=attrs,
            GlobalSecondaryIndexUpdates=updates,
        )

    def update_ttl(self, table_name, enabled, attr):
        self.ddb.update_time_to_live(
            TableName=table_name,
            TimeToLiveSpecification={"Enabled": enabled, "AttributeName": attr},
        )

    def list_tables(self):
        """
        Return a mapping of table_name -> table_description
        """
        tables = {}

        paginator = self.ddb.get_paginator("list_tables")
        for page in paginator.paginate():
            for table_name in page["TableNames"]:
                tables[table_name] = self.describe(table_name)
        return tables

    def describe_ttl(self, table_name):
        try:
            return self.ddb.describe_time_to_live(TableName=table_name)
        except self.ddb.exceptions.ResourceNotFoundException:
            return None

    def describe_pitr(self, table_name):
        try:
            return self.ddb.describe_continuous_backups(TableName=table_name)
        except Exception:
            # DynamoDB Local throws a 400 or 404 for this endpoint.
            # We return None to signal "Feature not available"
            return None

    def update_pitr(self, table_name, enabled):
        try:
            self.ddb.update_continuous_backups(
                TableName=table_name,
                PointInTimeRecoverySpecification={"PointInTimeRecoveryEnabled": enabled},
            )
        except Exception:
            print(
                f"[WARNING] Could not update PITR for {table_name}. DynamoDB Local might not support it."
            )

    def wait_for_gsi_active(self, table_name, gsi_name):
        waiter_config = {
            "version": 2,
            "waiters": {
                "GSIActive": {
                    "delay": 2,
                    "maxAttempts": 60,
                    "operation": "DescribeTable",
                    "acceptors": [
                        {
                            "matcher": "pathAll",
                            "argument": f"Table.GlobalSecondaryIndexes[?IndexName=='{gsi_name}'].IndexStatus",
                            "expected": "ACTIVE",
                            "state": "success",
                        },
                        {
                            "matcher": "pathAny",
                            "argument": "Table.TableStatus",
                            "expected": "DELETING",
                            "state": "failure",
                        },
                    ],
                }
            },
        }
        waiter_model = WaiterModel(waiter_config)
        custom_waiter = create_waiter_with_client("GSIActive", waiter_model, self.ddb)
        custom_waiter.wait(TableName=table_name)
