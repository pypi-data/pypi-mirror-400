from unittest.mock import MagicMock

import pytest

from cfddb.dynamodb.client import DynamoClient


@pytest.fixture
def mock_ddb_client():
    """Returns a REAL DynamoClient with a MOCKED internal boto3 client."""
    client = DynamoClient("http://localhost", "local", "key", "secret")
    client.ddb = MagicMock()  # Mock the internal boto3
    return client
