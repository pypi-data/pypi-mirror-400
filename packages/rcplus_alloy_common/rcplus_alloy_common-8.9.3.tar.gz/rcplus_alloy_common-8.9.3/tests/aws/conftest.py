import os
from datetime import datetime, timezone

import pytest
import boto3

from moto import mock_dynamodb, mock_s3, mock_glue, mock_athena


@pytest.fixture
def mock_s3_bucket():
    with mock_s3():
        client = boto3.client("s3")
        client.create_bucket(Bucket="test")
        yield client


@pytest.fixture
def mock_athena_backend():
    with mock_athena():
        client = boto3.client("athena")
        client.create_work_group(
            Name=os.environ["WR_WORKGROUP"],
            Configuration={
                "ResultConfiguration": {
                    "OutputLocation": "s3://test/athena_results",
                },
                "EnforceWorkGroupConfiguration": False,
            },
        )
        yield client


@pytest.fixture
def mock_athena_backend_enforced():
    with mock_athena():
        client = boto3.client("athena")
        client.create_work_group(
            Name=os.environ["WR_WORKGROUP"],
            Configuration={
                "ResultConfiguration": {
                    "OutputLocation": "s3://test/athena_results",
                },
                "EnforceWorkGroupConfiguration": True,
            },
        )
        yield client


@pytest.fixture
def mock_glue_database():
    with mock_glue():
        client = boto3.client("glue")
        client.create_database(
            DatabaseInput={
                "Name": os.environ["WR_DATABASE"],
            }
        )
        yield client


@pytest.fixture
def mock_dynamodb_table():
    with mock_dynamodb():
        client = boto3.client("dynamodb")
        client.create_table(
            TableName="test",
            KeySchema=[
                {"AttributeName": "id", "KeyType": "HASH"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "id", "AttributeType": "S"},
            ],
            ProvisionedThroughput={"ReadCapacityUnits": 1, "WriteCapacityUnits": 1},
        )
        client.put_item(
            TableName="test",
            Item={
                "id": {"S": "recent_timestamp"},
                "p_timestamp": {"S": datetime.now(tz=timezone.utc).isoformat()},
            },
        )
        client.put_item(
            TableName="test",
            Item={
                "id": {"S": "old_timestamp"},
                "p_timestamp": {"S": "2021-01-01T00:00:00+00:00"},
            },
        )
        client.put_item(
            TableName="test",
            Item={
                "id": {"S": "no_timestamp"},
            },
        )
        client.put_item(
            TableName="test",
            Item={
                "id": {"S": "another_timestamp"},
                "p_timestamp_2": {"S": "2021-01-01T00:00:00+00:00"},
            },
        )
        yield client
