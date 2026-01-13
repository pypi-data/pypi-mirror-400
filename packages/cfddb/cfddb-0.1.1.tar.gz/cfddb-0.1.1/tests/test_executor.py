from unittest.mock import MagicMock

from botocore.exceptions import ClientError

from cfddb.dynamodb.tables import DynamoTableSpec
from cfddb.engine.executor import Executor
from cfddb.engine.planner import PlanAction


def test_create_table_success(mock_ddb_client):
    executor = Executor(mock_ddb_client)

    spec = DynamoTableSpec(
        TableName="SimpleTable",
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        GlobalSecondaryIndexes=[],
    )
    action = PlanAction("Create", spec)
    mock_ddb_client.ddb.create_table.return_value = {}
    executor.apply(MagicMock(actions=[action]))

    # Verify Boto3 was called, NOT the wrapper
    # Note: client.create() calls boto3.create_table(**payload)
    mock_ddb_client.ddb.create_table.assert_called_once()
    call_kwargs = mock_ddb_client.ddb.create_table.call_args.kwargs
    assert call_kwargs["TableName"] == "SimpleTable"


def test_create_table_retry_on_key_schema_too_big(mock_ddb_client):
    executor = Executor(mock_ddb_client)

    spec = DynamoTableSpec(
        TableName="ComplexTable",
        AttributeDefinitions=[
            {"AttributeName": "pk", "AttributeType": "S"},
            {"AttributeName": "sk", "AttributeType": "S"},
            {"AttributeName": "v1", "AttributeType": "S"},
        ],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "BadGSI",
                "KeySchema": [
                    {"AttributeName": "pk", "KeyType": "HASH"},
                    {"AttributeName": "sk", "KeyType": "HASH"},
                    {"AttributeName": "v1", "KeyType": "RANGE"},  # 3 keys
                ],
                "Projection": {"ProjectionType": "ALL"},
            }
        ],
    )
    action = PlanAction("Create", spec)

    error_response = {"Error": {"Code": "ValidationException", "Message": "Key Schema too big"}}

    # Mock Boto3: First call fails, Second call succeeds
    mock_ddb_client.ddb.create_table.side_effect = [
        ClientError(error_response, "CreateTable"),
        {},
    ]

    executor.apply(MagicMock(actions=[action]))

    # Assert called twice
    assert mock_ddb_client.ddb.create_table.call_count == 2

    # Check 2nd call arguments (the retry)
    args, kwargs = mock_ddb_client.ddb.create_table.call_args_list[1]

    # Ensure GlobalSecondaryIndexes is MISSING (deleted because list was empty)
    assert "GlobalSecondaryIndexes" not in kwargs

    # Ensure AttributeDefinitions were filtered (only 'pk' left)
    assert len(kwargs["AttributeDefinitions"]) == 1
    assert kwargs["AttributeDefinitions"][0]["AttributeName"] == "pk"


def test_create_table_calls_waiter(mock_ddb_client):
    executor = Executor(mock_ddb_client)
    spec = DynamoTableSpec(
        TableName="WaitTable",
        AttributeDefinitions=[],
        KeySchema=[],
        GlobalSecondaryIndexes=[],
    )
    action = PlanAction("Create", spec)

    # Mock the internal boto3 waiter
    mock_waiter = MagicMock()
    mock_ddb_client.ddb.get_waiter.return_value = mock_waiter
    mock_ddb_client.ddb.create_table.return_value = {}

    executor.apply(MagicMock(actions=[action]))

    # Assert Waiter was initialized and used
    mock_ddb_client.ddb.get_waiter.assert_called_with("table_exists")
    mock_waiter.wait.assert_called_once()
    assert mock_waiter.wait.call_args.kwargs["TableName"] == "WaitTable"


def test_delete_gsi_payload(mock_ddb_client):
    executor = Executor(mock_ddb_client)
    spec = DynamoTableSpec(
        TableName="PruneTable",
        AttributeDefinitions=[],
        KeySchema=[],
        GlobalSecondaryIndexes=[],
    )
    # Payload for delete is just the string name
    action = PlanAction("Delete_GSI", spec, payload="OldGSI")

    executor.apply(MagicMock(actions=[action]))

    # Verify we called update_table with correct DELETE payload
    mock_ddb_client.ddb.update_table.assert_called_once()
    kwargs = mock_ddb_client.ddb.update_table.call_args.kwargs

    assert kwargs["TableName"] == "PruneTable"
    assert kwargs["GlobalSecondaryIndexUpdates"][0]["Delete"]["IndexName"] == "OldGSI"
