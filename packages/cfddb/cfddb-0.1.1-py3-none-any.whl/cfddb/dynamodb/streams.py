import uuid


def mock_stream_arn(table_name):
    return f"arn:aws:dynamodb:local:000000000000:table/{table_name}/stream/{uuid.uuid4()}"
