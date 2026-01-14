import pytest
import boto3
from moto import mock_s3

from rcplus_alloy_common.airflow.hooks import SilentS3Hook


@pytest.fixture(autouse=True)
def moto_s3():
    mock = mock_s3()
    mock.start()
    # create bucket
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket="test-bucket")
    for i in range(1000):
        s3.put_object(
            Bucket="test-bucket",
            Key=f"key{i}",
            Body=bytes(f"key{i}", encoding="utf-8"),
        )
    yield
    mock.stop()


def test_delete_objects(caplog):
    hook = SilentS3Hook()
    hook.delete_objects(
        bucket="test-bucket",
        keys=[f"key{i}" for i in range(1000)]
    )

    # assert that the bucket is empty
    keys = hook.list_keys(bucket_name="test-bucket")
    assert len(keys) == 0

    # assert that no log is extreamly long
    for record in caplog.records:
        assert len(record.message) < 300
