from datetime import datetime, timedelta, timezone
from unittest.mock import patch
import os
import logging
import json

import pytest
import botocore
import boto3
import moto
from moto import mock_s3, mock_ssm, mock_glue, mock_athena

from airflow.models.dag import DAG
from airflow.models import DagRun
from airflow.utils.context import Context
from airflow.exceptions import AirflowException

from rcplus_alloy_common.multitenancy import (
    CustomAttributeRawDataFormat,
    CustomAttributeType,
)
from rcplus_alloy_common.version import head_ref
from rcplus_alloy_common.airflow.observability import slack_alert_on_retry, slack_alert_on_failure
from rcplus_alloy_common.airflow.operators import (
    AlloyGlueJobOperator,
    AlloyEcsRunTaskOperator,
    AlloyDbtRunTaskOperator,
    AlloyBashOperator,
    AlloyBranchPythonOperator,
    AlloyDbtRunRefreshTaskOperator,
    AlloyAthenaOptimizeOperator,
    AlloyAthenaPostDbtVerificationOperator,
)


@pytest.fixture
def mock_ecs_operator_execute():
    with patch("airflow.providers.amazon.aws.operators.ecs.EcsRunTaskOperator.execute") as mock_execute:
        mock_execute.return_value = None
        yield mock_execute


@pytest.fixture
def mock_gluejob_operator_execute():
    with patch("airflow.providers.amazon.aws.operators.glue.GlueJobOperator.execute") as mock_execute:
        mock_execute.return_value = None
        yield mock_execute


@pytest.fixture
def mock_bash_operator_execute():
    with patch("airflow.operators.bash.BashOperator.execute") as mock_execute:
        mock_execute.return_value = None
        yield mock_execute


@pytest.fixture
def mock_optimize_more_runs_query_exception():
    with patch("rcplus_alloy_common.airflow.operators.AlloyAthenaOperator.execute") as mock_retriable_athena_query:
        mock_retriable_athena_query.side_effect = Exception(
            "Final state of Athena job is FAILED, query_execution_id is "
            "mock-query-id. Error: ICEBERG_OPTIMIZE_MORE_RUNS_NEEDED"
        )
        yield mock_retriable_athena_query


@pytest.fixture
def mock_vacuum_more_runs_query_exception():
    with patch("rcplus_alloy_common.airflow.operators.AlloyAthenaOperator.execute") as mock_retriable_athena_query:
        mock_retriable_athena_query.side_effect = Exception(
            "Final state of Athena job is FAILED, query_execution_id is "
            "mock-query-id. Error: ICEBERG_VACUUM_MORE_RUNS_NEEDED"
        )
        yield mock_retriable_athena_query


@pytest.fixture
def mock_airflow_variable():
    # patch airflow.models.Variable.get to return "subnet-12345678,subnet-12345678,subnet-12345678" if called with
    # global_VPC_PRIVATE_SUBNETS and "sg-12345678" if called with global_VPC_DEFAULT_SECURITY_GROUP
    with patch("airflow.models.Variable.get") as mock_get:
        mock_get.side_effect = lambda key, *args, **kwargs: {
            "global_VPC_PRIVATE_SUBNETS": "subnet-12345678,subnet-12345678,subnet-12345678",
            "global_VPC_DEFAULT_SECURITY_GROUP": "sg-12345678",
            "global_SHARED_ECS_CLUSTER": "my-test-cluster",
        }[key]
        yield mock_get


@pytest.fixture(autouse=True)
def moto_s3():
    mock = mock_s3()
    mock.start()
    # create bucket
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket="dev-alloy-glue-log4j-appender-jar")
    # put object from data/log4j2.properties
    with open("tests/data/log4j2.properties") as f:
        s3.put_object(Bucket="dev-alloy-glue-log4j-appender-jar", Key="lib/log4j2.properties", Body=f.read())

    s3.create_bucket(Bucket="test-bucket")
    s3.put_object(Bucket="test-bucket", Key=".lock", Body=b"test_lock")

    # put some fake data in the bucket for the test tables
    ## old (enough) table
    s3.put_object(Bucket="test-bucket", Key="test-database/test-table/1", Body=b"test")
    s3.put_object(Bucket="test-bucket", Key="test-database/test-table/2", Body=b"test")
    s3.put_object(Bucket="test-bucket", Key="test-database/test-table/3", Body=b"test")
    ## manipulate object last_modified
    bucket = moto.s3.models.s3_backends["123456789012"]["global"].buckets["test-bucket"]
    key = bucket.keys["test-database/test-table/1"]
    key.last_modified = datetime.now(timezone.utc) - timedelta(hours=25)

    ## recent table
    s3.put_object(Bucket="test-bucket", Key="test-database/test-table-2/1", Body=b"test")
    s3.put_object(Bucket="test-bucket", Key="test-database/test-table-2/2", Body=b"test")
    s3.put_object(Bucket="test-bucket", Key="test-database/test-table-2/3", Body=b"test")
    ## manipulate object last_modified
    bucket = moto.s3.models.s3_backends["123456789012"]["global"].buckets["test-bucket"]
    key = bucket.keys["test-database/test-table-2/1"]
    key.last_modified = datetime.now(timezone.utc) - timedelta(hours=23)

    yield
    mock.stop()


class QueryResultsDict(dict):
    def __init__(self, rows):
        self.rows = rows

    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        column_info = [{"CatalogName": "string"}]
        return moto.athena.models.QueryResults(rows=self.rows, column_info=column_info)


class ExecutionsDict(dict):
    """
    Simulates execution that is first queued, and succeeded on subsequent calls.
    """

    def __init__(self, workgroup):
        self.n = 0
        self.workgroup = workgroup

    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        execution = moto.athena.models.Execution(query="select", context=None, config=None, workgroup=self.workgroup)
        if self.n == 0:
            execution.status = "QUEUED"
            self.n = 1

        return execution


class FailedExecutionsDict(dict):
    """
    Simulates execution that fails.
    """

    def __init__(self, workgroup):
        self.workgroup = workgroup

    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        execution = moto.athena.models.Execution(query="select", context=None, config=None, workgroup=self.workgroup)
        execution.status = "FAILED"
        return execution


@pytest.fixture
def mock_athena_backend_with_data():
    backend = moto.athena.athena_backends["123456789012"]["us-east-1"]
    backend.query_results = QueryResultsDict(
        rows=[{"Data": [{"VarCharValue": "data"}]}, {"Data": [{"VarCharValue": "has data"}]}]
    )
    backend.executions = ExecutionsDict(workgroup=os.environ["WR_WORKGROUP"])
    yield


@pytest.fixture
def mock_athena_backend_no_data():
    backend = moto.athena.athena_backends["123456789012"]["us-east-1"]
    backend.query_results = QueryResultsDict(rows=[{"Data": [{"VarCharValue": "data"}]}, {"Data": [{}]}])
    yield


@pytest.fixture
def mock_athena_backend_failed_query():
    backend = moto.athena.athena_backends["123456789012"]["us-east-1"]
    backend.executions = FailedExecutionsDict(workgroup=os.environ["WR_WORKGROUP"])
    yield


@pytest.fixture(autouse=True)
def moto_ssm():
    mock = mock_ssm()
    mock.start()
    # create parameter
    ssm = boto3.client("ssm", region_name="us-east-1")
    ssm.put_parameter(
        Name="/alloy/airflow/glue/fluentd_log4j_appender_conf_s3_path",
        Description="config file for fluentd log4j appender",
        Value="s3://dev-alloy-glue-log4j-appender-jar/lib/log4j2.properties",
        Type="String",
        Overwrite=True,
        Tier="Standard",
    )
    ssm.put_parameter(
        Name="/alloy/airflow/glue/fluentd_log4j_appender_jarball_s3_path",
        Description="jarball for fluentd log4j appender",
        Value="s3://dev-alloy-glue-log4j-appender-jar/lib/log4j2.jar",
        Type="String",
        Overwrite=True,
        Tier="Standard",
    )
    yield
    mock.stop()


@pytest.fixture(autouse=True)
def moto_athena():
    with mock_athena():
        client = boto3.client("athena")
        client.create_work_group(
            Name=os.environ["WR_WORKGROUP"],
            Configuration={
                "ResultConfiguration": {
                    "OutputLocation": "s3://test-bucket/athena_results",
                },
                "EnforceWorkGroupConfiguration": True,
            },
        )
        yield


@pytest.fixture(autouse=True)
def moto_glue():
    DATABASE_INPUT = {  # noqa: N806
        "Name": "test-database",
        "Description": "a testdatabase",
        "LocationUri": "s3://test-bucket/test-database",
        "Parameters": {},
        "CreateTableDefaultPermissions": [
            {
                "Principal": {"DataLakePrincipalIdentifier": "a_fake_owner"},
                "Permissions": ["ALL"],
            },
        ],
    }
    TABLE_INPUT = {  # noqa: N806
        "Name": "test-table",
        "Owner": "a_fake_owner",
        "Parameters": {"EXTERNAL": "TRUE"},
        "Retention": 0,
        "StorageDescriptor": {
            "Columns": [
                {"Name": "col1", "Type": "string"},
                {"Name": "col2", "Type": "string"},
            ],
            "Location": "s3://test-bucket/test-database/test-table",
            "BucketColumns": [],
            "Compressed": False,
            "InputFormat": "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat",
            "NumberOfBuckets": -1,
            "OutputFormat": "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat",
            "Parameters": {},
            "SerdeInfo": {
                "Parameters": {"serialization.format": "1"},
                "SerializationLibrary": "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe",
            },
            "SkewedInfo": {
                "SkewedColumnNames": [],
                "SkewedColumnValueLocationMaps": {},
                "SkewedColumnValues": [],
            },
            "SortColumns": [],
            "StoredAsSubDirectories": False,
        },
        "TableType": "EXTERNAL_TABLE",
    }

    mock = mock_glue()
    mock.start()
    # create database and tables
    glue = boto3.client("glue", region_name="us-east-1")
    glue.create_database(DatabaseInput=DATABASE_INPUT)
    for table_name in ["test-table", "test-table-2", "test-table-3"]:
        TABLE_INPUT["Name"] = table_name
        TABLE_INPUT["StorageDescriptor"]["Location"] = f"s3://test-bucket/test-database/{table_name}"
        glue.create_table(
            DatabaseName="test-database",
            TableInput=TABLE_INPUT,
        )

    # create a job with arbitrary jars and files
    glue.create_job(
        Name="test-job",
        Role="test-role",
        Command={
            "Name": "glueetl",
            "ScriptLocation": "s3://test-bucket/test-job",
        },
        DefaultArguments={
            "--job-language": "python",
            "--extra-jars": "s3://test-bucket/test-job/jar.jar",
            "--extra-files": "s3://test-bucket/test-job/.config",
        },
        MaxRetries=0,
        Timeout=123,
        MaxCapacity=1.0,
        GlueVersion="4.0",
        NumberOfWorkers=1,
        WorkerType="Standard",
    )

    # create a job with the logzio appender jars in the extra-jars
    glue.create_job(
        Name="preconfigured-test-job",
        Role="test-role",
        Command={
            "Name": "glueetl",
            "ScriptLocation": "s3://test-bucket/test-job",
        },
        DefaultArguments={
            "--job-language": "python",
            "--extra-jars": "s3://dev-alloy-glue-log4j-appender-jar/lib/log4j2.jar"
        },
        MaxRetries=0,
        Timeout=123,
        MaxCapacity=1.0,
        GlueVersion="4.0",
        NumberOfWorkers=1,
        WorkerType="Standard",
    )

    # create a job without any default arguments
    glue.create_job(
        Name="no-default-args-test-job",
        Role="test-role",
        Command={
            "Name": "glueetl",
            "ScriptLocation": "s3://test-bucket/test-job",
        },
        MaxRetries=0,
        Timeout=123,
        MaxCapacity=1.0,
        GlueVersion="4.0",
        NumberOfWorkers=1,
        WorkerType="Standard",
    )
    yield
    mock.stop()


def test_alloy_glue_job_operator(mock_gluejob_operator_execute):  # pylint: disable=unused-argument
    with DAG(dag_id="test_dag", start_date=datetime(2020, 1, 1)) as dag:
        operator = AlloyGlueJobOperator(
            task_id="test_alloy_glue_job_operator",
            job_name="test-job",
        )
        context = Context(
            dag=dag,
            dag_run=DagRun(dag_id=dag.dag_id, run_id="undefined_123"),
        )
        operator.execute(context=context)
        assert operator.dest_s3_path in operator.script_args["--extra-files"]
        # fetch the resulting log4j2.properties file
        s3 = boto3.client("s3", region_name="us-east-1")
        response = s3.get_object(
            Bucket=operator.dest_s3_path.split("/")[2], Key="/".join(operator.dest_s3_path.split("/")[3:])
        )
        config_file = response["Body"].read().decode("utf-8")

        # fetch the template log4j2.properties file
        response = s3.get_object(Bucket="dev-alloy-glue-log4j-appender-jar", Key="lib/log4j2.properties")
        template = response["Body"].read().decode("utf-8")

        # compare the two files
        found = False
        for orig, result in zip(template.split("\n"), config_file.split("\n")):
            if orig.startswith("appender.Fluentd.additionalFields"):
                found = True
                _result = dict(
                    [x.split("=") for x in result.replace("appender.Fluentd.additionalFields = ", "").split(";")]
                )
                assert len(_result) == 9
                assert _result["env"] == "test"
                assert _result["version"] == "0.0.0"
                assert _result["repository"] == "my-test-repo"
                assert _result["software_component"] == "my-software-component"
                assert _result["dag_id"] == "test_dag"
                assert _result["dag_run_id"] == "undefined_123"
                assert _result["task_id"] == "test_alloy_glue_job_operator"
                assert _result["glue_job_name"] == "test-job"
                assert _result["alloy_tag"] == "alloy.glue.my-software-component.test_dag-test-job"
            else:
                assert orig == result
        assert found is True


def test_alloy_glue_job_operator_extra_jars_with_args_append(
    mock_gluejob_operator_execute,
):  # pylint: disable=unused-argument
    with DAG(dag_id="test_dag", start_date=datetime(2020, 1, 1)) as dag:
        # if script_args are set they will overwrite the default arguments of the job.
        for job_name in ["no-default-args-test-job", "preconfigured-test-job", "test-job"]:
            operator = AlloyGlueJobOperator(
                task_id=f"test-{job_name}-alloy-glue-job-operator",
                job_name=job_name,
                script_args={"--extra-jars": "s3://test-bucket/test-job/jar.jar"},
            )
            context = Context(
                dag=dag,
                dag_run=DagRun(dag_id=dag.dag_id, run_id="undefined_123"),
            )
            operator.execute(context=context)
            expected_extra = "s3://test-bucket/test-job/jar.jar,s3://dev-alloy-glue-log4j-appender-jar/lib/log4j2.jar"
            assert operator.script_args["--extra-jars"] == expected_extra, f"failing for job_name {job_name}"


def test_alloy_glue_job_operator_extra_jars_with_args(mock_gluejob_operator_execute):  # pylint: disable=unused-argument
    with DAG(dag_id="test_dag", start_date=datetime(2020, 1, 1)) as dag:
        # if script_args are set they will overwrite the default arguments of the job.
        for job_name in ["no-default-args-test-job", "preconfigured-test-job", "test-job"]:
            operator = AlloyGlueJobOperator(
                task_id=f"test-{job_name}-alloy-glue-job-operator",
                job_name=job_name,
                script_args={
                    "--extra-jars": "s3://test-bucket/test-job/jar.jar,s3://dev-alloy-glue-log4j-appender-jar/lib/log4j2.jar"
                },
            )
            context = Context(
                dag=dag,
                dag_run=DagRun(dag_id=dag.dag_id, run_id="undefined_123"),
            )
            operator.execute(context=context)
            expected_extra = "s3://test-bucket/test-job/jar.jar,s3://dev-alloy-glue-log4j-appender-jar/lib/log4j2.jar"
            assert operator.script_args["--extra-jars"] == expected_extra, f"failing for job_name {job_name}"


def test_alloy_glue_job_operator_extra_files_with_args_append(
    mock_gluejob_operator_execute,
):  # pylint: disable=unused-argument
    with DAG(dag_id="test_dag", start_date=datetime(2020, 1, 1)) as dag:
        # if script_args are set they will overwrite the default arguments of the job.
        for job_name in ["no-default-args-test-job", "preconfigured-test-job", "test-job"]:
            operator = AlloyGlueJobOperator(
                task_id=f"test-{job_name}-alloy-glue-job-operator",
                job_name=job_name,
                script_args={"--extra-files": "s3://test-bucket/test-job/.config"},
            )
            context = Context(
                dag=dag,
                dag_run=DagRun(dag_id=dag.dag_id, run_id="undefined_123"),
            )
            operator.execute(context=context)
            expected_extra = ",".join(
                [
                    "s3://test-bucket/test-job/.config",
                    f"s3://dev-alloy-glue-log4j-appender-jar/config/test_dag/test-{job_name}-alloy-glue-job-operator/undefined_123/log4j2.properties",
                ]
            )
            assert operator.script_args["--extra-files"] == expected_extra, f"failing for job_name {job_name}"


def test_alloy_glue_job_operator_extra_files_with_args(
    mock_gluejob_operator_execute,
):  # pylint: disable=unused-argument
    with DAG(dag_id="test_dag", start_date=datetime(2020, 1, 1)) as dag:
        # if script_args are set they will overwrite the default arguments of the job.
        for job_name in ["no-default-args-test-job", "preconfigured-test-job", "test-job"]:
            operator = AlloyGlueJobOperator(
                task_id=f"test-{job_name}-alloy-glue-job-operator",
                job_name=job_name,
                script_args={
                    "--extra-files": ",".join(
                        [
                            f"s3://dev-alloy-glue-log4j-appender-jar/config/test_dag/test-{job_name}-alloy-glue-job-operator/undefined_123/log4j2.properties",
                            "s3://test-bucket/test-job/.config",
                        ]
                    )
                },
            )
            context = Context(
                dag=dag,
                dag_run=DagRun(dag_id=dag.dag_id, run_id="undefined_123"),
            )
            operator.execute(context=context)
            expected_extra = ",".join(
                [
                    f"s3://dev-alloy-glue-log4j-appender-jar/config/test_dag/test-{job_name}-alloy-glue-job-operator/undefined_123/log4j2.properties",
                    "s3://test-bucket/test-job/.config",
                ]
            )
            assert operator.script_args["--extra-files"] == expected_extra, f"failing for job_name {job_name}"


def test_alloy_glue_job_operator_without_args(mock_gluejob_operator_execute):  # pylint: disable=unused-argument
    with DAG(dag_id="test_dag", start_date=datetime(2020, 1, 1)) as dag:
        # if script_args are set they will overwrite the default arguments of the job.
        for job_name in ["no-default-args-test-job", "preconfigured-test-job", "test-job"]:
            operator = AlloyGlueJobOperator(
                task_id=f"test-{job_name}-alloy-glue-job-operator",
                job_name=job_name,
            )
            context = Context(
                dag=dag,
                dag_run=DagRun(dag_id=dag.dag_id, run_id="undefined_123"),
            )
            operator.execute(context=context)
            if job_name == "test-job":
                expected_files = ",".join(
                    [
                        "s3://test-bucket/test-job/.config",
                        f"s3://dev-alloy-glue-log4j-appender-jar/config/test_dag/test-{job_name}-alloy-glue-job-operator/undefined_123/log4j2.properties",
                    ]
                )
                expected_jars = "s3://test-bucket/test-job/jar.jar,s3://dev-alloy-glue-log4j-appender-jar/lib/log4j2.jar"
            else:
                expected_files = f"s3://dev-alloy-glue-log4j-appender-jar/config/test_dag/test-{job_name}-alloy-glue-job-operator/undefined_123/log4j2.properties"
                expected_jars = "s3://dev-alloy-glue-log4j-appender-jar/lib/log4j2.jar"
            assert operator.script_args["--extra-files"] == expected_files, f"failing for job_name {job_name}"
            assert operator.script_args["--extra-jars"] == expected_jars, f"failing for job_name {job_name}"


def test_alloy_ecs_operator_network_config_factory(mock_airflow_variable):  # pylint: disable=unused-argument
    with DAG(dag_id="test_dag", start_date=datetime(2020, 1, 1)):
        operator = AlloyEcsRunTaskOperator(
            task_id="test_alloy_ecs_operator_network_config_factory",
            cluster="test",
            task_definition="test",
            overrides={},
        )
        operator.network_configuration_factory()
        assert "awsvpcConfiguration" in operator.network_configuration
        assert operator.network_configuration["awsvpcConfiguration"]["subnets"] == [
            "subnet-12345678",
            "subnet-12345678",
            "subnet-12345678",
        ]
        assert operator.network_configuration["awsvpcConfiguration"]["securityGroups"] == ["sg-12345678"]
        assert operator.network_configuration["awsvpcConfiguration"]["assignPublicIp"] == "DISABLED"


def test_alloy_ecs_operator_overrides_factory_void(mock_airflow_variable):  # pylint: disable=unused-argument
    with DAG(dag_id="test_dag", start_date=datetime(2020, 1, 1)) as dag:
        operator = AlloyEcsRunTaskOperator(
            task_id="test_alloy_ecs_operator_overrides_factory",
            task_definition="test-task",
            reattach=False,
        )
        operator.cluster == "{{ var.value.global_SHARED_ECS_CLUSTER }}"
        operator.overrides_factory(dag_id=dag.dag_id, dag_run_id="undefined_123")
        assert "containerOverrides" in operator.overrides
        assert len(operator.overrides["containerOverrides"]) == 2
        assert operator.overrides["containerOverrides"][0]["name"] == "test-task"
        assert operator.overrides["containerOverrides"][1]["name"] == "alloy-logs-router"

        logz_io_env = operator.overrides["containerOverrides"][1]["environment"]

        assert {"name": "DAG_RUN_ID", "value": "undefined_123"} in logz_io_env
        assert {"name": "DAG_ID", "value": "test_dag"} in logz_io_env
        assert {"name": "TASK_ID", "value": "test_alloy_ecs_operator_overrides_factory"} in logz_io_env
        assert {"name": "ALLOY_TAG", "value": "alloy.ecs.my-software-component.test_dag-test-task"} in logz_io_env


def test_alloy_ecs_operator_overrides_factory_void2(mock_airflow_variable):  # pylint: disable=unused-argument
    with DAG(dag_id="test_dag", start_date=datetime(2020, 1, 1)) as dag:
        operator = AlloyEcsRunTaskOperator(
            task_id="test_alloy_ecs_operator_overrides_factory",
            cluster="test",
            task_definition="test-task",
            overrides={},
        )
        assert operator.cluster == "test"
        operator.overrides_factory(dag_id=dag.dag_id, dag_run_id="undefined_123")
        assert "containerOverrides" in operator.overrides
        assert len(operator.overrides["containerOverrides"]) == 2
        assert operator.overrides["containerOverrides"][0]["name"] == "test-task"
        assert operator.overrides["containerOverrides"][1]["name"] == "alloy-logs-router"

        logz_io_env = operator.overrides["containerOverrides"][1]["environment"]

        assert {"name": "DAG_RUN_ID", "value": "undefined_123"} in logz_io_env
        assert {"name": "DAG_ID", "value": "test_dag"} in logz_io_env
        assert {"name": "TASK_ID", "value": "test_alloy_ecs_operator_overrides_factory"} in logz_io_env
        assert {"name": "ALLOY_TAG", "value": "alloy.ecs.my-software-component.test_dag-test-task"} in logz_io_env


def test_alloy_ecs_operator_overrides_factory(mock_airflow_variable):  # pylint: disable=unused-argument
    with DAG(dag_id="test_dag", start_date=datetime(2020, 1, 1)) as dag:
        operator = AlloyEcsRunTaskOperator(
            task_id="test_alloy_ecs_operator_overrides_factory",
            cluster="test-cluster-2",
            task_definition="test-alloy-my-software-component-test-task",
            overrides={
                "containerOverrides": [
                    {
                        "name": "test-alloy-my-software-component-test-task",
                        "environment": [{"name": "TEST_ENV", "value": "test"}],
                        "command": ["echo", "test"],
                    }
                ]
            },
        )
        assert operator.task_definition == "test-alloy-my-software-component-test-task"
        assert operator.cluster == "test-cluster-2"
        operator.overrides_factory(dag_id=dag.dag_id, dag_run_id="undefined_123")
        assert "containerOverrides" in operator.overrides
        assert len(operator.overrides["containerOverrides"]) == 2
        assert operator.overrides["containerOverrides"][0]["name"] == "test-alloy-my-software-component-test-task"
        assert operator.overrides["containerOverrides"][1]["name"] == "alloy-logs-router"
        assert operator.overrides["containerOverrides"][0]["environment"] == [{"name": "TEST_ENV", "value": "test"}]
        assert operator.overrides["containerOverrides"][0]["command"] == ["echo", "test"]
        logz_io_env = operator.overrides["containerOverrides"][1]["environment"]

        assert {"name": "DAG_RUN_ID", "value": "undefined_123"} in logz_io_env
        assert {"name": "DAG_ID", "value": "test_dag"} in logz_io_env
        assert {"name": "TASK_ID", "value": "test_alloy_ecs_operator_overrides_factory"} in logz_io_env
        assert {"name": "ALLOY_TAG", "value": "alloy.ecs.my-software-component.test_dag-test-test-task"} in logz_io_env


def test_alloy_ecs_operator_overrides_factory_2(  # pylint: disable=unused-argument
    mock_airflow_variable,
    mock_ecs_operator_execute,
):
    with DAG(dag_id="test_dag", start_date=datetime(2020, 1, 1)) as dag:
        operator = AlloyEcsRunTaskOperator(
            task_id="test_alloy_ecs_operator_overrides_factory",
            cluster="test-cluster-2",
            task_definition="test-task",
            overrides={
                "containerOverrides": [
                    {
                        "name": "alloy-logs-router",
                    }
                ]
            },
        )
        # Create a dummy context
        context = Context(
            dag=dag,
            dag_run=DagRun(run_id="undefined_123", dag_id="test_dag", execution_date=datetime.now()),
        )
        operator.execute(context)
        assert "awsvpcConfiguration" in operator.network_configuration
        assert operator.cluster == "test-cluster-2"
        assert "containerOverrides" in operator.overrides
        assert len(operator.overrides["containerOverrides"]) == 2
        assert operator.overrides["containerOverrides"][1]["name"] == "test-task"
        assert operator.overrides["containerOverrides"][0]["name"] == "alloy-logs-router"
        logz_io_env = operator.overrides["containerOverrides"][0]["environment"]

        assert {"name": "DAG_RUN_ID", "value": "undefined_123"} in logz_io_env
        assert {"name": "DAG_ID", "value": "test_dag"} in logz_io_env
        assert {"name": "TASK_ID", "value": "test_alloy_ecs_operator_overrides_factory"} in logz_io_env
        assert {"name": "ALLOY_TAG", "value": "alloy.ecs.my-software-component.test_dag-test-task"} in logz_io_env


def test_alloy_dbt_run_operator_sidecar_tags(mock_airflow_variable):  # pylint: disable=unused-argument
    with DAG(dag_id="test_dag", start_date=datetime(2020, 1, 1)) as dag:
        operator = AlloyDbtRunTaskOperator(
            task_id="test_alloy_ecs_operator_overrides_factory",
            cluster="test-cluster-2",
            task_definition="dev-alloy-my-software-component-test-task",
            select=["model"],
            exclude=["model2+"],
            full_refresh=True,
            environment_variables=[
                {"name": "TEST_ENV", "value": "test"},
            ]
        )
        assert operator.task_definition == "dev-alloy-my-software-component-test-task"
        assert operator.cluster == "test-cluster-2"
        operator.overrides_factory(dag_id=dag.dag_id, dag_run_id="undefined_123")
        assert "containerOverrides" in operator.overrides
        assert len(operator.overrides["containerOverrides"]) == 2
        assert operator.overrides["containerOverrides"][0]["name"] == "dev-alloy-my-software-component-test-task"
        assert operator.overrides["containerOverrides"][1]["name"] == "alloy-logs-router"
        assert operator.overrides["containerOverrides"][0]["environment"] == [{"name": "TEST_ENV", "value": "test"}]
        assert operator.overrides["containerOverrides"][0]["command"] == [
            "dbt",
            "run",
            "--profiles-dir",
            ".",
            "--full-refresh",
            "--select",
            "model",
            "--exclude",
            "model2+",
        ]
        logz_io_env = operator.overrides["containerOverrides"][1]["environment"]

        assert {"name": "DAG_RUN_ID", "value": "undefined_123"} in logz_io_env
        assert {"name": "DAG_ID", "value": "test_dag"} in logz_io_env
        assert {"name": "TASK_ID", "value": "test_alloy_ecs_operator_overrides_factory"} in logz_io_env
        assert {
                "name": "ALLOY_TAG",
                "value": "alloy.dbt-ecs.my-software-component.test_dag-dev-test-task",
            } in logz_io_env


def test_alloy_ecs_operator_overrides_factory_warnings(caplog):
    with DAG(dag_id="test_dag", start_date=datetime(2020, 1, 1)) as dag:
        operator = AlloyEcsRunTaskOperator(
            task_id="test_alloy_ecs_operator_overrides_factory",
            cluster="test-cluster-2",
            task_definition="test-task",
            overrides={
                "containerOverrides": [
                    {
                        "name": "test-task-2",
                        "environment": [{"name": "TEST_ENV", "value": "test"}],
                        "command": ["echo", "test"],
                    }
                ]
            },
        )
        operator.overrides_factory(dag_id=dag.dag_id, dag_run_id="undefined_123")

    for x in caplog.records:
        assert x.levelname == "WARNING"
        assert (
            "containerOverrides contains containers other than "
            f"['alloy-logs-router', '{operator.task_definition}']: ['test-task-2']"
        ) in x.message


def test_alloy_ecs_operator_command_and_environ():
    with DAG(dag_id="test_dag", start_date=datetime(2020, 1, 1)) as dag:
        operator = AlloyEcsRunTaskOperator(
            task_id="test_alloy_ecs_operator_overrides_factory",
            cluster="test-cluster-2",
            task_definition="test-task",
            environment_variables=[
                {"name": "ENV-VAR", "value": "env var value"},
            ],
            command=["echo", "test"],
        )
        operator.overrides_factory(dag_id=dag.dag_id, dag_run_id="undefined_123")
        assert "containerOverrides" in operator.overrides
        assert len(operator.overrides["containerOverrides"]) == 2
        assert operator.overrides["containerOverrides"][0]["name"] == "test-task"
        assert operator.overrides["containerOverrides"][1]["name"] == "alloy-logs-router"

        assert operator.overrides["containerOverrides"][0]["command"] == ["echo", "test"]
        assert operator.overrides["containerOverrides"][0]["environment"] == [
            {"name": "ENV-VAR", "value": "env var value"}
        ]


@pytest.mark.parametrize(
    "parameters",
    [
        {
            "command": ["echo", "test"],
        },
        {
            "environment_variables": [
                {"name": "ENV-VAR", "value": "env var value"},
            ],
        },
        {
            "command": ["echo", "test"],
            "environment_variables": [
                {"name": "ENV-VAR", "value": "env var value"},
            ],
        },
    ],
)
def test_alloy_ecs_operator_command_and_environ_collision(parameters):
    with DAG(dag_id="test_dag", start_date=datetime(2020, 1, 1)):
        with pytest.raises(ValueError) as e:
            AlloyEcsRunTaskOperator(
                task_id="test_alloy_ecs_operator_overrides_factory",
                cluster="test-cluster-2",
                task_definition="test-task",
                overrides={
                    "containerOverrides": [
                        {
                            "name": "test-task",
                            "command": ["echo", "test"],
                            "environment": [{"name": "ENV-VAR-1", "value": "env var value"}],
                        }
                    ]
                },
                **parameters,
            )
            assert str(e.value) == "Overrides are provided. Environment variables and command are not allowed."


@pytest.mark.parametrize(
    "parameters",
    [
        {},
        {
            "overrides": {
                "containerOverrides": [
                    {
                        "name": "test-task",
                        "command": ["echo", "test"],
                        "environment": [{"name": "ENV-VAR", "value": "env var value"}],
                    }
                ]
            },
        },
        {"tenant": "tenant_1"},
        {
            "tenant": "tenant_1",
            "overrides": {
                "containerOverrides": [
                    {
                        "name": "test-task",
                        "command": ["echo", "test"],
                    }
                ]
            },
        },
        {
            "tenant": "tenant_1",
            "overrides": {
                "containerOverrides": [
                    {
                        "name": "test-task",
                        "command": ["echo", "test"],
                        "environment": [{"name": "ENV-VAR", "value": "env var value"}],
                    }
                ]
            },
        },
    ],
)
def test_alloy_ecs_operator_tenant(  # pylint: disable=unused-argument
    mock_airflow_variable,
    mock_ecs_operator_execute,
    parameters,
):
    with DAG(dag_id="test_dag", start_date=datetime(2020, 1, 1)) as dag:
        operator = AlloyEcsRunTaskOperator(
            task_id="test_alloy_ecs_operator_overrides_factory",
            cluster="test-cluster-2",
            task_definition="test-task",
            tenant=parameters.get("tenant"),
            overrides=parameters.get("overrides"),
        )
        # Create a dummy context
        context = Context(
            dag=dag,
            dag_run=DagRun(run_id="undefined_123", dag_id="test_dag", execution_date=datetime.now()),
        )
        operator.execute(context)
        assert "awsvpcConfiguration" in operator.network_configuration
        assert operator.cluster == "test-cluster-2"
        assert "containerOverrides" in operator.overrides
        assert len(operator.overrides["containerOverrides"]) == 2
        assert operator.overrides["containerOverrides"][0]["name"] == "test-task"
        assert operator.overrides["containerOverrides"][1]["name"] == "alloy-logs-router"
        primary_task_env = operator.overrides["containerOverrides"][0]["environment"]

        if parameters.get("tenant") is not None:
            assert {"name": "TENANT", "value": "tenant_1"} in primary_task_env
            assert {
                "name": "FEATURES",
                "value": json.dumps(
                    {
                        "sso_data": True, "enterprise": True, "dcr": True,
                        "byok": True, "gotom": True, "coops": True, "audience_segment_service": True,
                    }
                ),
            } in primary_task_env
            assert {"name": "WR_DATABASE", "value": "tenant_1"} in primary_task_env
        else:
            assert {"name": "TENANT", "value": "tenant_1"} not in primary_task_env
            assert {
                "name": "FEATURES",
                "value": json.dumps(
                    {
                        "sso_data": True, "enterprise": True, "dcr": True,
                        "byok": True, "gotom": True, "coops": True, "audience_segment_service": True,
                    }
                ),
            } not in primary_task_env
            assert {"name": "WR_DATABASE", "value": "tenant_1"} not in primary_task_env

        if parameters.get("overrides") is not None:
            environments = parameters["overrides"]["containerOverrides"][0].get("environments")
            if environments is not None:
                assert {"name": "ENV-VAR", "value": "env var value"} in primary_task_env
        else:
            assert {"name": "ENV-VAR", "value": "env var value"} not in primary_task_env


def test_operator_version_log(caplog, mock_bash_operator_execute):  # pylint: disable=unused-argument
    with DAG(
        dag_id="test_dag",
        start_date=datetime(2020, 1, 1),
        schedule="@daily",
    ) as dag:
        operator = AlloyBashOperator(
            task_id="test_operator_version_log",
            bash_command="echo 'hello world'",
        )
        operator.execute({})
        found = False
        for x in caplog.records:
            expected_message = (
                f"Running task `{operator.task_id}` of dag `{dag.dag_id}` with `rcplus_alloy_common@{head_ref}`"
            )
            if x.levelname == "INFO" and expected_message in x.message:
                found = True

        assert found


def test_optimize_tables():
    with DAG(
        dag_id="test_dag",
        start_date=datetime(2020, 1, 1),
        schedule="@daily",
    ) as dag:
        operator = AlloyDbtRunRefreshTaskOperator(
            task_id="test_get_refresh_tables",
            table_names=["test-table", "test-table-2"],
            database="test-database",
            task_definition="ecs-test-task",
        )

        # nothing to refresh
        assert not operator.get_refresh_tables()

        # delete tables
        optimize_operator = AlloyAthenaOptimizeOperator(
            task_id="test_alloy_athena_optimize_operator",
            database="test-database",
            table_name="test-table",
            output_location="s3://test-bucket/query-results",
        )
        optimize_operator._drop_table()  # pylint: disable=protected-access

        # assert that the table is deleted
        glue = boto3.client("glue", region_name="us-east-1")
        with pytest.raises(botocore.exceptions.ClientError) as exc_info:
            glue.get_table(DatabaseName="test-database", Name="test-table")
        assert exc_info.value.response["Error"]["Code"] == "EntityNotFoundException"

        # test-table to be refreshed
        tables_to_refresh = operator.get_refresh_tables()
        assert tables_to_refresh == ["test-table"]

        # delete tables
        optimize_operator_2 = AlloyAthenaOptimizeOperator(
            task_id="test_alloy_athena_optimize_operator_2",
            database="test-database",
            table_name="test-table-2",
            output_location="s3://test-bucket/query-results",
        )
        optimize_operator_2._drop_table()  # pylint: disable=protected-access

        tables_to_refresh = operator.get_refresh_tables()
        assert tables_to_refresh == ["test-table", "test-table-2"]

        # assert that the cmd is correct
        operator._update_command(tables_to_refresh)  # pylint: disable=protected-access
        assert operator.overrides["containerOverrides"][0]["command"] == [
            "dbt",
            "run",
            "--full-refresh",
            "--select",
            "test-table",
            "test-table-2",
            "--profiles-dir",
            ".",
        ]
        context = Context(
            dag=dag,
            dag_run=DagRun(dag_id=dag.dag_id, run_id="undefined_123"),
        )
        optimization_ok = optimize_operator_2._optimize(context)  # pylint: disable=protected-access
        assert optimization_ok is True
        optimization_ok = optimize_operator_2._vacuum(context)  # pylint: disable=protected-access
        assert optimization_ok is True


def test_optimize_tables_failure(mock_optimize_more_runs_query_exception):  # pylint: disable=unused-argument
    with DAG(
        dag_id="test_dag",
        start_date=datetime(2020, 1, 1),
        schedule="@daily",
    ) as dag:
        optimize_operator = AlloyAthenaOptimizeOperator(
            task_id="test_alloy_athena_optimize_operator",
            database="test-database",
            table_name="test-table",
            output_location="s3://test-bucket/query-results",
        )

        context = Context(
            dag=dag,
            dag_run=DagRun(dag_id=dag.dag_id, run_id="undefined_123"),
        )
        optimize_operator.execute(context)
        # assert that the table is deleted
        glue = boto3.client("glue", region_name="us-east-1")
        with pytest.raises(botocore.exceptions.ClientError) as exc_info:
            glue.get_table(DatabaseName="test-database", Name="test-table")
        assert exc_info.value.response["Error"]["Code"] == "EntityNotFoundException"


def test_skip_optimize_if_table_does_not_exist(mock_optimize_more_runs_query_exception, caplog):  # pylint: disable=unused-argument
    with DAG(
        dag_id="test_dag",
        start_date=datetime(2020, 1, 1),
        schedule="@daily",
    ) as dag:
        optimize_operator = AlloyAthenaOptimizeOperator(
            task_id="test_alloy_athena_optimize_operator",
            database="test-database",
            table_name="test-table-not-existed",
            output_location="s3://test-bucket/query-results",
        )

        context = Context(
            dag=dag,
            dag_run=DagRun(dag_id=dag.dag_id, run_id="undefined_123"),
        )

        with caplog.at_level(logging.INFO):
            optimize_operator.execute(context)
            assert "Table does not exist test-table-not-existed. Skip AlloyAthenaOptimizeOperator task" in caplog.text


def test_vacuum_tables_failure(mock_vacuum_more_runs_query_exception):  # pylint: disable=unused-argument
    with DAG(
        dag_id="test_dag",
        start_date=datetime(2020, 1, 1),
        schedule="@daily",
    ) as dag:
        optimize_operator = AlloyAthenaOptimizeOperator(
            task_id="test_alloy_athena_optimize_operator",
            database="test-database",
            table_name="test-table",
            output_location="s3://test-bucket/query-results",
        )

        context = Context(
            dag=dag,
            dag_run=DagRun(dag_id=dag.dag_id, run_id="undefined_123"),
        )
        optimize_operator.execute(context)
        # assert that the table is deleted
        glue = boto3.client("glue", region_name="us-east-1")
        with pytest.raises(botocore.exceptions.ClientError) as exc_info:
            glue.get_table(DatabaseName="test-database", Name="test-table")
        assert exc_info.value.response["Error"]["Code"] == "EntityNotFoundException"


def test_skip_dbt_update(caplog):
    with DAG(
        dag_id="test_dag",
        start_date=datetime(2020, 1, 1),
        schedule="@daily",
    ) as dag:
        operator = AlloyDbtRunRefreshTaskOperator(
            task_id="test_get_refresh_tables",
            table_names=["test-table", "test-table-2"],
            database="test-database",
            task_definition="ecs-test-task",
        )
        context = Context(
            dag=dag,
            dag_run=DagRun(dag_id=dag.dag_id, run_id="undefined_123"),
        )
        # assert that AirflowSkipException is raised
        with caplog.at_level(logging.INFO):
            operator.execute(context)
            assert "No tables to refresh" in caplog.text


def test_run_dbt_full_refresh(
    mock_ecs_operator_execute,
    mock_airflow_variable,
    caplog,
):  # pylint: disable=unused-argument
    with DAG(
        dag_id="test_dag",
        start_date=datetime(2020, 1, 1),
        schedule="@daily",
    ) as dag:
        operator = AlloyDbtRunRefreshTaskOperator(
            task_id="test_get_refresh_tables",
            table_names=["test-table", "test-table-2"],
            database="test-database",
            task_definition="ecs-test-task",
        )

        # delete tables
        glue = boto3.client("glue", region_name="us-east-1")
        for table_name in ["test-table", "test-table-2"]:
            glue.delete_table(DatabaseName="test-database", Name=table_name)

        context = Context(
            dag=dag,
            dag_run=DagRun(dag_id=dag.dag_id, run_id="undefined_123"),
        )
        operator.execute(context)
        assert "Tables to refresh ['test-table', 'test-table-2']" in caplog.text


@pytest.mark.parametrize(
    "params",
    [
        {
            "overrides": {
                "containerOverrides": [
                    {
                        "name": "test-task",
                        "command": ["echo", "test"],
                        "environment": [{"name": "ENV-VAR", "value": "env var value"}],
                    }
                ]
            },
            "command": ["dbt", "run", "--full-refresh", "--select", "test-table", "test-table-2"],
            "full_refresh": False,
            "select": ["test-table", "test-table-2"],
        },
        {
            "overrides": {
                "containerOverrides": [
                    {
                        "name": "test-task",
                        "command": ["echo", "test"],
                        "environment": [{"name": "ENV-VAR", "value": "env var value"}],
                    }
                ]
            }
        },
        {
            "full_refresh": False,
        },
        {
            "select": ["test-table", "test-table-2"],
        },
        {
            "exclude": ["test-table-2"],
        },
        {
            "command": ["dbt", "run", "--full-refresh", "--select", "test-table", "test-table-2"],
            "full_refresh": True,
        }
    ]
)
def test_run_dbt_refresh_fail_arguments(
    params,
    mock_ecs_operator_execute,
    mock_airflow_variable,
    caplog
):  # pylint: disable=unused-argument
    with DAG(
        dag_id="test_dag",
        start_date=datetime(2020, 1, 1),
        schedule="@daily",
    ):
        with pytest.raises(ValueError):
            AlloyDbtRunRefreshTaskOperator(
                task_id="test_get_refresh_tables",
                table_names=["test-table", "test-table-2"],
                database="test-database",
                task_definition="ecs-test-task",
                **params
            )


def test_optimize_pre_hook(caplog):
    with DAG(
        dag_id="test_dag",
        start_date=datetime(2020, 1, 1),
        schedule="@daily",
    ) as dag:
        operator = AlloyAthenaOptimizeOperator(
            task_id="test_alloy_athena_optimize_operator",
            database="test-database",
            table_name="test-table",
            output_location="s3://test-bucket/query-results",
            pre_hook="DELETE * FROM test-table",
        )
        context = Context(
            dag=dag,
            dag_run=DagRun(dag_id=dag.dag_id, run_id="undefined_123"),
        )
        operator.execute(context)

        assert "Run pre-hook DELETE * FROM test-table" in caplog.text
        assert "Perform optimization round 1. Execute OPTIMIZE test-table REWRITE DATA USING BIN_PACK" in caplog.text
        assert "Perform vacuum round 1. Execute VACUUM test-table" in caplog.text


def test_optimize_drop_recent_table_warning(caplog):
    with DAG(
        dag_id="test_dag",
        start_date=datetime(2020, 1, 1),
        schedule="@daily",
    ):
        operator = AlloyAthenaOptimizeOperator(
            task_id="test_alloy_athena_optimize_operator",
            database="test-database",
            table_name="test-table-2",
            output_location="s3://test-bucket/query-results",
        )
        operator._drop_table()

        assert "The table `test-table-2` was dropped, but it was created within the last 24 hours." in caplog.text


def test_optimize_drop_old_no_warning(caplog):
    with DAG(
        dag_id="test_dag",
        start_date=datetime(2020, 1, 1),
        schedule="@daily",
    ):
        operator = AlloyAthenaOptimizeOperator(
            task_id="test_alloy_athena_optimize_operator",
            database="test-database",
            table_name="test-table",
            output_location="s3://test-bucket/query-results",
        )
        operator._drop_table()

        assert "but it was created within the last 24 hours." not in caplog.text


def test_branch_python_operator(caplog):
    with DAG(
        dag_id="test_dag",
        start_date=datetime(2020, 1, 1),
        schedule="@daily",
    ):
        operator = AlloyBranchPythonOperator(
            task_id="test_alloy_python_branch_operator",
            python_callable=lambda: "branch_value",
        )

        assert slack_alert_on_failure in operator.on_failure_callback
        assert slack_alert_on_retry in operator.on_retry_callback


def test_skip_dbt_verification_if_table_does_not_exist(mock_athena_backend_with_data, caplog):
    with DAG(
        dag_id="test_dag",
        start_date=datetime(2020, 1, 1),
        schedule="@daily",
    ) as dag:
        operator = AlloyAthenaPostDbtVerificationOperator(
            task_id="test_get_verify_tables",
            table_name="test-table-not-existed",
            database="test-database",
            output_location="s3://test-bucket/query-results",
            workgroup=os.environ["WR_WORKGROUP"],
        )
        context = Context(
            dag=dag,
            dag_run=DagRun(dag_id=dag.dag_id, run_id="undefined_123"),
        )

        with caplog.at_level(logging.INFO):
            operator.execute(context)
            assert (
                "Table does not exist test-table-not-existed. Skip AlloyAthenaPostDbtVerificationOperator task"
                in caplog.text
            )


def test_dbt_verification_not_corrupt(mock_athena_backend_with_data, caplog):
    with DAG(
        dag_id="test_dag",
        start_date=datetime(2020, 1, 1),
        schedule="@daily",
    ) as dag:
        operator = AlloyAthenaPostDbtVerificationOperator(
            task_id="test_get_verify_tables",
            table_name="test-table",
            database="test-database",
            output_location="s3://test-bucket/query-results",
            workgroup=os.environ["WR_WORKGROUP"],
        )
        context = Context(
            dag=dag,
            dag_run=DagRun(dag_id=dag.dag_id, run_id="undefined_123"),
        )

        operator.execute(context)
        assert "Table test-table$partitions is not corrupted" in caplog.text


def test_dbt_verification_corrupt(caplog, mock_athena_backend_no_data):
    with DAG(
        dag_id="test_dag",
        start_date=datetime(2020, 1, 1),
        schedule="@daily",
    ) as dag:
        operator = AlloyAthenaPostDbtVerificationOperator(
            task_id="test_get_verify_tables",
            table_name="test-table-2",
            database="test-database",
            output_location="s3://test-bucket/query-results",
            workgroup=os.environ["WR_WORKGROUP"],
        )
        context = Context(
            dag=dag,
            dag_run=DagRun(dag_id=dag.dag_id, run_id="undefined_123"),
        )

        operator.execute(context)

        assert "test-table-2$partitions corrupted, optimizing" in caplog.text
        assert "test-table-2$partitions corrupted after optimize, dropping" in caplog.text

        # assert that the table is deleted
        glue = boto3.client("glue", region_name="us-east-1")
        with pytest.raises(botocore.exceptions.ClientError) as exc_info:
            glue.get_table(DatabaseName="test-database", Name="test-table-2")
        assert exc_info.value.response["Error"]["Code"] == "EntityNotFoundException"


def test_dbt_verification_query_fails(caplog, mock_athena_backend_failed_query):
    with DAG(
        dag_id="test_dag",
        start_date=datetime(2020, 1, 1),
        schedule="@daily",
    ) as dag:
        operator = AlloyAthenaPostDbtVerificationOperator(
            task_id="test_get_verify_tables",
            table_name="test-table",
            database="test-database",
            output_location="s3://test-bucket/query-results",
            workgroup=os.environ["WR_WORKGROUP"],
        )
        context = Context(
            dag=dag,
            dag_run=DagRun(dag_id=dag.dag_id, run_id="undefined_123"),
        )

        with pytest.raises(AirflowException) as exc_info:
            operator.execute(context)
        assert 'Querying table test-database."test-table$partitions" failed' in str(exc_info.value)


def test_dbt_verification_timeout(caplog):
    with patch(
        "rcplus_alloy_common.airflow.operators.AlloyAthenaPostDbtVerificationOperator.athena_query_execution"
    ) as mock_func:
        mock_response_1 = {"QueryExecution": {"Status": {"State": "RUNNING"}, "Statistics": {"": 0}}}
        mock_response_2 = {
            "QueryExecution": {"Status": {"State": "RUNNING"}, "Statistics": {"EngineExecutionTimeInMillis": 700000}}
        }
        mock_func.side_effect = [mock_response_1] + [mock_response_2] * 3

        with DAG(
            dag_id="test_dag",
            start_date=datetime(2020, 1, 1),
            schedule="@daily",
        ) as dag:
            operator = AlloyAthenaPostDbtVerificationOperator(
                task_id="test_get_verify_tables",
                table_name="test-table-2",
                database="test-database",
                output_location="s3://test-bucket/query-results",
                workgroup=os.environ["WR_WORKGROUP"],
            )
            context = Context(
                dag=dag,
                dag_run=DagRun(dag_id=dag.dag_id, run_id="undefined_123"),
            )

            operator.execute(context)

            assert 'Querying table test-database."test-table-2$partitions" timed out' in caplog.text
            assert "test-table-2$partitions corrupted, optimizing" in caplog.text
            assert "test-table-2$partitions corrupted after optimize, dropping" in caplog.text


def test_dbt_run_full_refresh_operator_skip(caplog):
    with DAG(
        dag_id="test_dag",
        start_date=datetime(2020, 1, 1),
        schedule="@daily",
    ) as dag:
        operator = AlloyDbtRunRefreshTaskOperator(
            task_id="test_get_refresh_tables",
            table_names=["test-table", "test-table-2"],
            database="test-database",
            task_definition="ecs-test-task",
        )
        context = Context(
            dag=dag,
            dag_run=DagRun(dag_id=dag.dag_id, run_id="undefined_123"),
        )

        operator.execute(context)
        assert "No tables to refresh" in caplog.text


def test_dbt_run_full_refresh_operator_fail_early():
    with DAG(
        dag_id="test_dag",
        start_date=datetime(2020, 1, 1),
        schedule="@daily",
    ):
        with pytest.raises(ValueError) as e:
            AlloyDbtRunRefreshTaskOperator(
                task_id="test_get_refresh_tables",
                table_names=["test-table", "test-table-2"],
                database="test-database",
                task_definition="ecs-test-task",
                overrides={
                    "containerOverrides": [
                        {
                            "name": "alloy-logs-router",
                        },
                        {
                            "name": "ecs-test-wrong-task-name",
                            "environment": [{"name": "TEST_ENV", "value": "test"}],
                            "command": ["echo", "test"],
                        },
                    ]
                }
            )
            assert "overrides parameter is not allowed" in str(e.value)


@pytest.mark.parametrize(
    "parameters",
    [
        {},
        {"environment_variables": [{"name": "ENV-VAR", "value": "env var value"}]},
        {"tenant": "tenant_1"},
        {"tenant": "tenant_1", "environment_variables": [{"name": "ENV-VAR", "value": "env var value"}]},
    ],
)
def test_dbt_run_full_refresh_operator(
    mock_ecs_operator_execute,
    mock_airflow_variable,
    caplog,
    parameters,
):  # pylint: disable=unused-argument
    with DAG(
        dag_id="test_dag",
        start_date=datetime(2020, 1, 1),
        schedule="@daily",
    ) as dag:
        operator = AlloyDbtRunRefreshTaskOperator(
            task_id="test_get_refresh_tables",
            table_names=["test-table", "test-table-2"],
            database="test-database",
            task_definition="ecs-test-task",
            **parameters,
        )

        # delete tables
        glue = boto3.client("glue", region_name="us-east-1")
        for table_name in ["test-table", "test-table-2"]:
            glue.delete_table(DatabaseName="test-database", Name=table_name)

        context = Context(
            dag=dag,
            dag_run=DagRun(dag_id=dag.dag_id, run_id="undefined_123"),
        )
        operator.execute(context)
        assert "Tables to refresh ['test-table', 'test-table-2']" in caplog.text

        # assert container parameters
        expected_environment = []
        if parameters.get("environment_variables") is not None:
            for env_var in parameters["environment_variables"]:
                expected_environment.append(env_var)
        if parameters.get("tenant") is not None:
            expected_environment.append({"name": "TENANT", "value": "tenant_1"})
            expected_environment.append(
                {
                    "name": "FEATURES",
                    "value": json.dumps(
                        {
                            "sso_data": True, "enterprise": True, "dcr": True,
                            "byok": True, "gotom": True, "coops": True, "audience_segment_service": True,
                        }
                    ),
                }
            )
            expected_environment.append({"name": "WR_DATABASE", "value": "tenant_1"})
            expected_environment.append(
                {
                    "name": "ACTIVATION_CHANNELS",
                    "value": json.dumps(
                        {
                            "gam": {
                                "activate_by_default": True,
                                "network_id": 987654321,
                            },
                            "xandr": {
                                "activate_by_default": True,
                                "member_id": 4321,
                                "aws_region": "eu-west-1",
                                "ppid_source": "ringier.ch",
                            },
                            "das": {
                                "activate_by_default": False,
                                "network_id": 56789,
                            }
                        },
                        separators=(",", ":")
                        ),
                }
            )
        assert operator.overrides["containerOverrides"][0]["command"] == [
            "dbt",
            "run",
            "--full-refresh",
            "--select",
            "test-table",
            "test-table-2",
            "--profiles-dir",
            ".",
        ]
        assert operator.overrides["containerOverrides"][0]["name"] == "ecs-test-task"
        assert len(expected_environment) == len(operator.overrides["containerOverrides"][0]["environment"])
        for expected_env, actual_env in zip(
            expected_environment, operator.overrides["containerOverrides"][0]["environment"]
        ):
            assert expected_env["name"] == actual_env["name"]
            assert expected_env["value"] == actual_env["value"]


@pytest.mark.parametrize(
    "parameters, expected_command",
    [
        (
            {},
            [
                "dbt",
                "run",
                "--full-refresh",
                "--select",
                "test-table",
                "test-table-2",
                "--profiles-dir",
                ".",
            ],
        ),
        (
            {
                "init_script": "python ./script.py",
            },
            [
                "bash",
                "-c",
                "python ./script.py && dbt run --full-refresh --select test-table test-table-2 --profiles-dir .",
            ],
        ),
        (
            {
                "init_script": "python ./script.py",
                "command": [
                    "dbt",
                    "run",
                    "--select",
                    "__TABLES_PLACEHOLDER__",
                    ".",
                ],
            },
            [
                "bash",
                "-c",
                "python ./script.py && dbt run --select test-table test-table-2 .",
            ],
        ),
    ],
)
def test_dbt_run_full_refresh_operator_with_init_script(
    mock_ecs_operator_execute,
    mock_airflow_variable,
    caplog,
    parameters,
    expected_command,
):  # pylint: disable=unused-argument
    with DAG(
        dag_id="test_dag",
        start_date=datetime(2020, 1, 1),
        schedule="@daily",
    ) as dag:
        operator = AlloyDbtRunRefreshTaskOperator(
            task_id="test_get_refresh_tables",
            table_names=["test-table", "test-table-2"],
            database="test-database",
            task_definition="ecs-test-task",
            tenant="tenant_1",
            **parameters,
        )

        # delete tables
        glue = boto3.client("glue", region_name="us-east-1")
        for table_name in ["test-table", "test-table-2"]:
            glue.delete_table(DatabaseName="test-database", Name=table_name)

        context = Context(
            dag=dag,
            dag_run=DagRun(dag_id=dag.dag_id, run_id="undefined_123"),
        )
        operator.execute(context)
        assert "Tables to refresh ['test-table', 'test-table-2']" in caplog.text

        # assert container parameters
        expected_environment = []
        expected_environment.append({"name": "TENANT", "value": "tenant_1"})
        expected_environment.append(
            {
                "name": "FEATURES",
                "value": json.dumps(
                    {
                        "sso_data": True, "enterprise": True, "dcr": True,
                        "byok": True, "gotom": True, "coops": True, "audience_segment_service": True,
                    }
                ),
            }
        )
        expected_environment.append({"name": "WR_DATABASE", "value": "tenant_1"})
        expected_environment.append(
            {
                "name": "ACTIVATION_CHANNELS",
                "value": json.dumps(
                    {
                        "gam": {
                            "activate_by_default": True,
                            "network_id": 987654321,
                        },
                        "xandr": {
                            "activate_by_default": True,
                            "member_id": 4321,
                            "aws_region": "eu-west-1",
                            "ppid_source": "ringier.ch",
                        },
                        "das": {
                            "activate_by_default": False,
                            "network_id": 56789,
                        }
                    },
                    separators=(",", ":"),
                )
            }
        )
        assert operator.overrides["containerOverrides"][0]["command"] == expected_command
        assert operator.overrides["containerOverrides"][0]["name"] == "ecs-test-task"
        assert len(expected_environment) == len(operator.overrides["containerOverrides"][0]["environment"])
        for expected_env, actual_env in zip(
            expected_environment, operator.overrides["containerOverrides"][0]["environment"]
        ):
            assert expected_env["name"] == actual_env["name"]
            assert expected_env["value"] == actual_env["value"]
