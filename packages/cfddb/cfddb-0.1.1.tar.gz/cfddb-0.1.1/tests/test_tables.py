import pytest
from pydantic import ValidationError

from cfddb.dynamodb.tables import DynamoTableSpec


def test_valid_table_spec():
    data = {
        "TableName": "TestTable",
        "AttributeDefinitions": [{"AttributeName": "id", "AttributeType": "S"}],
        "KeySchema": [{"AttributeName": "id", "KeyType": "HASH"}],
        "BillingMode": "PAY_PER_REQUEST",
    }
    spec = DynamoTableSpec.from_cfn(data)
    assert spec.TableName == "TestTable"
    assert len(spec.AttributeDefinitions) == 1


def test_missing_required_field():
    data = {"TableName": "Incomplete"}
    with pytest.raises(ValidationError):
        DynamoTableSpec.from_cfn(data)


def test_create_payload_removes_empty_gsi():
    data = {
        "TableName": "TestTable",
        "AttributeDefinitions": [{"AttributeName": "id", "AttributeType": "S"}],
        "KeySchema": [{"AttributeName": "id", "KeyType": "HASH"}],
        "GlobalSecondaryIndexes": [],
    }
    spec = DynamoTableSpec.from_cfn(data)
    payload = spec.create_payload()
    assert "GlobalSecondaryIndexes" not in payload


def test_gsi_attribute_filtering():
    """Ensures we only pick attributes used by the GSI."""
    data = {
        "TableName": "TestTable",
        "AttributeDefinitions": [
            {"AttributeName": "pk", "AttributeType": "S"},
            {"AttributeName": "unused", "AttributeType": "S"},
            {"AttributeName": "gsi_pk", "AttributeType": "S"},
        ],
        "KeySchema": [{"AttributeName": "pk", "KeyType": "HASH"}],
        "GlobalSecondaryIndexes": [
            {
                "IndexName": "GSI1",
                "KeySchema": [{"AttributeName": "gsi_pk", "KeyType": "HASH"}],
                "Projection": {"ProjectionType": "ALL"},
            }
        ],
    }
    spec = DynamoTableSpec.from_cfn(data)
    gsi = spec.GlobalSecondaryIndexes[0]

    filtered_attrs = spec.gsi_attribute_definitions(gsi)

    assert len(filtered_attrs) == 1
    assert filtered_attrs[0]["AttributeName"] == "gsi_pk"
