from datetime import datetime

import boto3
import pytest
import botocore
from moto import mock_s3

from airflow.models.dag import DAG
from airflow.exceptions import AirflowException

from rcplus_alloy_common.airflow.locking import (
    AlloyAcquireLockOperator, AlloyReleaseLockOperator, AlloyWaitAcquireLockSensor, AlloyWaitReleaseLockSensor
)


@pytest.fixture(autouse=True)
def moto_s3():
    mock = mock_s3()
    mock.start()

    # create bucket
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket="test-bucket")
    s3.put_object(Bucket="test-bucket", Key=".lock", Body=b"test_lock")
    s3.put_object(Bucket="test-bucket", Key="test-tenant/.lock", Body=b"test_lock")
    yield
    mock.stop()


@pytest.mark.parametrize(
    "tenant",
    [
        "test-tenant",
        None,
    ],
)
def test_acquire_lock_failure(tenant):
    with DAG(dag_id="test_dag", start_date=datetime(2020, 1, 1)):
        with pytest.raises(AirflowException) as exc_info:
            AlloyAcquireLockOperator(
                task_id="test_acquire_lock",
                bucket="test-bucket",
                lock_key="",
                tenant=tenant,
            )
        assert "Required parameters: bucket, lock_key" in str(exc_info.value)


@pytest.mark.parametrize(
    "tenant",
    [
        "test-tenant",
        None,
    ],
)
def test_acquire_lock_success(tenant):
    with DAG(dag_id="test_dag", start_date=datetime(2020, 1, 1)):
        operator = AlloyAcquireLockOperator(
            task_id="test_acquire_lock",
            bucket="test-bucket",
            lock_id="test_lock",
            lock_key=".lock_new",
            tenant=tenant,
        )
        operator.execute({})
        s3 = boto3.client("s3")
        status = s3.head_object(Bucket="test-bucket", Key=operator.lock_key)
        assert status
        if tenant:
            assert operator.lock_key.startswith(f"{tenant}/")


@pytest.mark.parametrize(
    "tenant",
    [
        "test-tenant",
        None,
    ],
)
def test_release_lock_failure(tenant):
    with DAG(dag_id="test_dag", start_date=datetime(2020, 1, 1)):
        with pytest.raises(AirflowException) as exc_info:
            AlloyReleaseLockOperator(
                task_id="test_release_lock",
                bucket="test-bucket",
                lock_key="",
                tenant=tenant,
            )
        assert "Required parameters: bucket, lock_key" in str(exc_info.value)


@pytest.mark.parametrize(
    "tenant",
    [
        "test-tenant",
        None,
    ],
)
def test_release_lock_success(tenant):
    with DAG(dag_id="test_dag", start_date=datetime(2020, 1, 1)):
        operator = AlloyReleaseLockOperator(
            task_id="test_release_lock",
            bucket="test-bucket",
            tenant=tenant,
            lock_id="test_lock",
            lock_key=".lock",
        )
        operator.execute({})
        s3 = boto3.client("s3")
        # Check that the lock was deleted
        with pytest.raises(botocore.exceptions.ClientError) as exc_info:
            s3.head_object(Bucket="test-bucket", Key=operator.lock_key)

        # Check the other lock wasn't deleted
        if tenant:
            status = s3.head_object(Bucket="test-bucket", Key=".lock")
            assert status
        else:
            status = s3.head_object(Bucket="test-bucket", Key="test-tenant/.lock")
            assert status

        assert exc_info.value.response["Error"]["Code"] == "404"


@pytest.mark.parametrize(
    "tenant",
    [
        "test-tenant",
        None,
    ],
)
def test_release_lock_success_not_exists(tenant, caplog):
    with DAG(dag_id="test_dag", start_date=datetime(2020, 1, 1)):
        operator = AlloyReleaseLockOperator(
            task_id="test_release_lock",
            bucket="test-bucket",
            lock_id="test_lock",
            lock_key=".lock.not.exists",
            tenant=tenant,
        )

        operator.execute({})
        # check that the info message was logged
        found = False
        for x in caplog.records:
            expected_message = f"The lock s3://{operator.bucket}/{operator.lock_key} is released already"
            if x.levelname == "INFO" and expected_message in x.message:
                found = True
                break

        assert found


@pytest.mark.parametrize(
    "tenant",
    [
        "test-tenant",
        None,
    ],
)
def test_release_lock_failure_wrong_id(tenant, caplog):
    with DAG(dag_id="test_dag", start_date=datetime(2020, 1, 1)):
        operator = AlloyReleaseLockOperator(
            task_id="test_release_lock",
            bucket="test-bucket",
            tenant=tenant,
            lock_id="test_lock_2",
            lock_key=".lock",
        )

        with pytest.raises(AirflowException) as exc_info:
            operator.execute({})

        expected_message = (
            f"Failed to release the lock s3://{operator.bucket}/{operator.lock_key} because its "
            f"lock_id is test_lock but expected {operator.lock_id}"
        )
        assert expected_message == exc_info.value.args[0]


@pytest.mark.parametrize(
    "tenant",
    [
        "test-tenant",
        None,
    ],
)
def test_wait_acquire_lock_sensor_existing_owned(tenant):
    with DAG(dag_id="test_dag", start_date=datetime(2020, 1, 1)):
        sqs_sensor = AlloyWaitAcquireLockSensor(
            task_id="test_wait_lock",
            lock_id="test_lock",
            tenant=tenant,
            bucket_key=".lock",
            bucket_name="test-bucket",
        )
        assert sqs_sensor.poke({}) is True
        s3 = boto3.client("s3")
        status = s3.head_object(Bucket="test-bucket", Key=sqs_sensor.bucket_key)
        assert status


@pytest.mark.parametrize(
    "tenant",
    [
        "test-tenant",
        None,
    ],
)
def test_wait_acquire_lock_sensor_existing_not_owned(tenant):
    with DAG(dag_id="test_dag", start_date=datetime(2020, 1, 1)):
        sqs_sensor = AlloyWaitAcquireLockSensor(
            task_id="test_wait_lock",
            bucket_key=".lock",
            bucket_name="test-bucket",
            tenant=tenant,
        )
        assert sqs_sensor.poke({}) is False
        s3 = boto3.client("s3")
        status = s3.head_object(Bucket="test-bucket", Key=sqs_sensor.bucket_key)
        assert status


@pytest.mark.parametrize(
    "tenant",
    [
        "test-tenant",
        None,
    ],
)
def test_wait_acquire_lock_sensor_not_exists(tenant, caplog):
    with DAG(dag_id="test_dag", start_date=datetime(2020, 1, 1)):
        sqs_sensor = AlloyWaitAcquireLockSensor(
            task_id="test_wait_lock",
            bucket_key=".lock_2",
            bucket_name="test-bucket",
            tenant=tenant,
        )
        assert sqs_sensor.poke({}) is True

        found = False
        for x in caplog.records:
            expected_message = f"Acquired the lock s3://{sqs_sensor.bucket_name}/{sqs_sensor.bucket_key}"
            if x.levelname == "INFO" and expected_message in x.message:
                found = True
                break

        assert found


@pytest.mark.parametrize(
    "tenant",
    [
        "test-tenant",
        None,
    ],
)
def test_wait_release_lock_owned_sensor(tenant, caplog):
    with DAG(dag_id="test_dag", start_date=datetime(2020, 1, 1)):
        sqs_sensor = AlloyWaitReleaseLockSensor(
            task_id="test_wait_release",
            lock_id="test_lock",
            bucket_key=".lock",
            bucket_name="test-bucket",
            tenant=tenant,
        )
        assert sqs_sensor.poke({}) is True
        s3 = boto3.client("s3")
        # Check that the lock was deleted
        with pytest.raises(botocore.exceptions.ClientError) as exc_info:
            s3.head_object(Bucket="test-bucket", Key=sqs_sensor.bucket_key)
        assert exc_info.value.response["Error"]["Code"] == "404"


@pytest.mark.parametrize(
    "tenant",
    [
        "test-tenant",
        None,
    ],
)
def test_wait_release_lock_not_owned_sensor(tenant, caplog):
    with DAG(dag_id="test_dag", start_date=datetime(2020, 1, 1)):
        sqs_sensor = AlloyWaitReleaseLockSensor(
            task_id="test_wait_release",
            bucket_key=".lock",
            bucket_name="test-bucket",
            tenant=tenant,
        )
        assert sqs_sensor.poke({}) is False
        s3 = boto3.client("s3")
        # Check that the lock still exists
        status = s3.head_object(Bucket="test-bucket", Key=sqs_sensor.bucket_key)
        assert status


@pytest.mark.parametrize(
    "tenant",
    [
        "test-tenant",
        None,
    ],
)
def test_acquire_lock_op_key_already_prefixed(tenant):
    with DAG(dag_id="test_dag", start_date=datetime(2020, 1, 1)):
        operator = AlloyAcquireLockOperator(
            task_id="test_acquire_lock",
            bucket="test-bucket",
            lock_id="test_lock",
            lock_key="test-tenant/.lock",
            tenant=tenant,
        )
        assert operator.lock_key == "test-tenant/.lock"


@pytest.mark.parametrize(
    "tenant",
    [
        "test-tenant",
        None,
    ],
)
def test_release_lock_op_key_already_prefixed(tenant):
    with DAG(dag_id="test_dag", start_date=datetime(2020, 1, 1)):
        operator = AlloyReleaseLockOperator(
            task_id="test_release_lock",
            bucket="test-bucket",
            lock_id="test_lock",
            lock_key="test-tenant/.lock",
            tenant=tenant,
        )
        assert operator.lock_key == "test-tenant/.lock"


@pytest.mark.parametrize(
    "tenant",
    [
        "test-tenant",
        None,
    ],
)
def test_wait_acquire_lock_sensor_key_already_prefixed(tenant):
    with DAG(dag_id="test_dag", start_date=datetime(2020, 1, 1)):
        sensor = AlloyWaitAcquireLockSensor(
            task_id="test_wait_lock",
            bucket_key="test-tenant/.lock",
            bucket_name="test-bucket",
            tenant=tenant,
        )
        assert sensor.bucket_key == "test-tenant/.lock"


@pytest.mark.parametrize(
    "tenant",
    [
        "test-tenant",
        None,
    ],
)
def test_wait_release_lock_sensor_key_already_prefixed(tenant):
    with DAG(dag_id="test_dag", start_date=datetime(2020, 1, 1)):
        sensor = AlloyWaitReleaseLockSensor(
            task_id="test_wait_release",
            lock_id="test_lock",
            bucket_key="test-tenant/.lock",
            bucket_name="test-bucket",
            tenant=tenant,
        )
        assert sensor.bucket_key == "test-tenant/.lock"
