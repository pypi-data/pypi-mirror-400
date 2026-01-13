from unittest.mock import MagicMock

import pytest

from cfddb.engine.planner import Planner


@pytest.fixture
def mock_parser():
    parser = MagicMock()
    # Default behavior: Return a basic valid table spec
    parser.parse.return_value = {
        "MyTable": {
            "Type": "AWS::DynamoDB::Table",
            "Properties": {
                "TableName": "MyTable",
                "AttributeDefinitions": [{"AttributeName": "id", "AttributeType": "S"}],
                "KeySchema": [{"AttributeName": "id", "KeyType": "HASH"}],
                "TimeToLiveSpecification": {"AttributeName": "ttl", "Enabled": True},
            },
        }
    }
    return parser


def test_plan_create_new_table(mock_ddb_client, mock_parser, mocker):
    mocker.patch("cfddb.engine.planner.CFNParser")
    mocker.patch.object(mock_ddb_client, "list_tables", return_value={})
    mocker.patch.object(mock_ddb_client, "describe_ttl", return_value={})

    planner = Planner("dummy_path", "local", mock_ddb_client)
    planner.parser = mock_parser
    plan = planner.create_plan()

    assert len(plan.actions) == 2
    assert plan.actions[0].type == "Create"
    assert plan.actions[0].spec.TableName == "MyTable"
    assert plan.actions[1].type == "Update_TTL"


def test_plan_idempotent_no_changes(mock_ddb_client, mock_parser, mocker):
    mocker.patch("cfddb.engine.planner.CFNParser")
    mocker.patch.object(
        mock_ddb_client,
        "list_tables",
        return_value={"MyTable": {"TableName": "MyTable", "GlobalSecondaryIndexes": []}},
    )
    mocker.patch.object(
        mock_ddb_client,
        "describe_ttl",
        return_value={
            "TimeToLiveDescription": {
                "TimeToLiveStatus": "ENABLED",
                "AttributeName": "ttl",
            }
        },
    )
    mocker.patch.object(mock_ddb_client, "describe_pitr", return_value=None)

    planner = Planner("dummy_path", "local", mock_ddb_client)
    planner.parser = mock_parser

    plan = planner.create_plan()

    assert len(plan.actions) == 0


def test_plan_gsi_drift_add(mock_ddb_client, mock_parser, mocker):
    mocker.patch("cfddb.engine.planner.CFNParser")
    mock_parser.parse.return_value["MyTable"]["Properties"]["GlobalSecondaryIndexes"] = [
        {
            "IndexName": "NewGSI",
            "KeySchema": [{"AttributeName": "gsi_pk", "KeyType": "HASH"}],
            "Projection": {"ProjectionType": "ALL"},
        }
    ]
    mocker.patch.object(
        mock_ddb_client,
        "list_tables",
        return_value={"MyTable": {"TableName": "MyTable", "GlobalSecondaryIndexes": []}},
    )
    mocker.patch.object(
        mock_ddb_client,
        "describe_ttl",
        return_value={
            "TimeToLiveDescription": {
                "TimeToLiveStatus": "ENABLED",
                "AttributeName": "ttl",
            }
        },
    )
    mocker.patch.object(mock_ddb_client, "describe_pitr", return_value=None)

    planner = Planner("dummy_path", "local", mock_ddb_client)
    planner.parser = mock_parser

    plan = planner.create_plan()

    assert len(plan.actions) == 1
    assert plan.actions[0].type == "Add_GSI"
    assert plan.actions[0].payload.IndexName == "NewGSI"


def test_plan_ttl_drift_needs_update(mock_ddb_client, mock_parser, mocker):
    mocker.patch("cfddb.engine.planner.CFNParser")
    mock_parser.parse.return_value["MyTable"]["Properties"]["TimeToLiveSpecification"] = {
        "AttributeName": "expireAt",
        "Enabled": True,
    }

    mocker.patch.object(
        mock_ddb_client,
        "list_tables",
        return_value={"MyTable": {"TableName": "MyTable"}},
    )
    mocker.patch.object(
        mock_ddb_client,
        "describe_ttl",
        return_value={"TimeToLiveDescription": {"TimeToLiveStatus": "DISABLED"}},
    )
    mocker.patch.object(mock_ddb_client, "describe_pitr", return_value=None)

    planner = Planner("dummy", "local", mock_ddb_client)
    planner.parser = mock_parser
    plan = planner.create_plan()

    assert len(plan.actions) == 1
    assert plan.actions[0].type == "Update_TTL"
    assert plan.actions[0].payload.Enabled is True


def test_plan_pitr_ignore_if_unsupported(mock_ddb_client, mock_parser, mocker):
    mocker.patch("cfddb.engine.planner.CFNParser")
    mock_parser.parse.return_value["MyTable"]["Properties"]["TimeToLiveSpecification"] = None
    mock_parser.parse.return_value["MyTable"]["Properties"]["PointInTimeRecoverySpecification"] = {
        "PointInTimeRecoveryEnabled": True
    }
    mock_parser.parse.return_value["MyTable"]["Properties"]["StreamSpecification"] = {
        "StreamViewType": "NEW_IMAGE"
    }
    mocker.patch.object(
        mock_ddb_client,
        "list_tables",
        return_value={"MyTable": {"TableStatus": "ACTIVE"}},
    )
    mocker.patch.object(mock_ddb_client, "describe_ttl", return_value={})
    mocker.patch.object(mock_ddb_client, "describe_pitr", return_value=None)

    planner = Planner("dummy", "local", mock_ddb_client)
    planner.parser = mock_parser
    plan = planner.create_plan()
    assert len(plan.actions) == 0
