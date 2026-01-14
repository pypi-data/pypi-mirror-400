import os
import re
from unittest import mock

import pytest
import awswrangler as wr
import pandas as pd
import boto3

from rcplus_alloy_common.aws.wr import (
    get_s3_output,
    get_database,
    start_query_execution,
    read_sql_query,
    create_ctas_table,
    to_parquet,
    create_iceberg_table,
    create_json_table,
    create_parquet_table,
    create_csv_table,
    extract_table_creation_params,
    validate_table_input,
    validate_path,
)


def test_get_s3_output_wo_tenant(mock_athena_backend):
    assert get_s3_output(workgroup=None) is None
    assert get_s3_output(workgroup=os.environ["WR_WORKGROUP"]) is None


def test_get_s3_output_w_tenant(mock_athena_backend):
    with mock.patch.dict(os.environ, {"TENANT": "test-tenant", "WR_WORKGROUP": "workgroup_without_output"}):
        assert get_s3_output(workgroup=None) is None

    with mock.patch.dict(os.environ, {"TENANT": "test-tenant", "WR_WORKGROUP": ""}):
        assert get_s3_output(workgroup=None) is None

    with mock.patch.dict(os.environ, {"TENANT": "test-tenant"}):  # WR_WORKGROUP from mock_athena_backend
        assert get_s3_output(workgroup=os.environ["WR_WORKGROUP"]) == "s3://test/athena_results/test-tenant"


def test_get_s3_output_with_enforced_config(mock_athena_backend_enforced):
    with mock.patch.dict(os.environ, {"TENANT": "test-tenant"}):
        with pytest.raises(ValueError) as e:
            get_s3_output(workgroup=os.environ["WR_WORKGROUP"])
            assert "EnforceWorkGroupConfiguration is set to True, cannot override OutputLocation" in str(e)


def test_get_database_with_tenant():
    with mock.patch.dict(os.environ, {"TENANT": "test-tenant"}):
        database = get_database()
        assert database == "test-tenant"


def test_get_database_without_tenant_with_wr_database():
    database = get_database()
    assert database == os.environ["WR_DATABASE"]


def test_get_database(monkeypatch):
    monkeypatch.delenv("WR_DATABASE", raising=False)
    database = get_database()
    assert database is None


def test_start_query_execution(mock_athena_backend):
    with mock.patch.dict(os.environ, {"TENANT": "test-tenant"}):
        query_id = start_query_execution("SELECT 1")
        result = wr.athena.get_query_execution(query_id)
        assert result["ResultConfiguration"]["OutputLocation"] == "s3://test/athena_results/test-tenant"
        assert result["QueryExecutionContext"]["Database"] == "test-tenant"


def test_start_query_execution_without_database(mock_athena_backend):
    query_id = start_query_execution("SELECT 1")
    result = wr.athena.get_query_execution(query_id)
    assert result["ResultConfiguration"]["OutputLocation"] == "s3://test/athena_results"
    assert result["QueryExecutionContext"]["Database"] == "test-db"


def test_start_query_execution_pass_database(mock_athena_backend):
    query_id = start_query_execution("SELECT 1", database="test-tenant")
    result = wr.athena.get_query_execution(query_id)
    assert result["ResultConfiguration"]["OutputLocation"] == "s3://test/athena_results"
    assert result["QueryExecutionContext"]["Database"] == "test-tenant"


def test_read_sql_query(monkeypatch, mock_athena_backend, mock_glue_database):
    monkeypatch.delenv("WR_DATABASE", raising=False)
    with pytest.raises(ValueError) as e:
        read_sql_query("SELECT 1")
        assert "Database is not set" in str(e)


def test_create_ctas_table(mock_athena_backend):
    with mock.patch.dict(os.environ, {"TENANT": "test-tenant"}):
        result = create_ctas_table("SELECT 1", wait=True)
        assert result["ctas_database"] == "test-tenant"
        query_metadata = result["ctas_query_metadata"]
        assert query_metadata.output_location == "s3://test/athena_results/test-tenant"
        expected_external_location = (
            f"external_location = 's3://test/athena_results/test-tenant/{result['ctas_table']}'"
        )
        assert expected_external_location in query_metadata.raw_payload["Query"]


def test_create_ctas_table_without_database(
    mock_athena_backend,
):
    result = create_ctas_table("SELECT 1", wait=True)
    assert result["ctas_database"] == "test-db"
    query_metadata = result["ctas_query_metadata"]
    assert query_metadata.output_location == "s3://test/athena_results"
    expected_external_location = f"external_location = 's3://test/athena_results/{result['ctas_table']}'"
    assert expected_external_location in query_metadata.raw_payload["Query"]


def test_create_ctas_table_pass_database(mock_athena_backend):
    result = create_ctas_table("SELECT 1", database="some-database", wait=True)
    assert result["ctas_database"] == "some-database"
    query_metadata = result["ctas_query_metadata"]
    assert query_metadata.output_location == "s3://test/athena_results"
    expected_external_location = f"external_location = 's3://test/athena_results/{result['ctas_table']}'"
    assert expected_external_location in query_metadata.raw_payload["Query"]


def test_to_parquet(mock_athena_backend, mock_s3_bucket, mock_glue_database):
    with mock.patch.dict(os.environ):
        # Make sure the database argument is passed to the underlying function
        del os.environ["WR_DATABASE"]
        schema_path = os.path.join(os.path.dirname(__file__), "test_schema.yml")
        table_name = "test_table"
        database_name = "test-db"
        path = f"s3://test/{database_name}/{table_name}"
        data = {"fp_id": [f"10{i}" for i in range(5)], "vector": [i for i in range(5)]}
        df = pd.DataFrame(data)
        to_parquet(
            df,
            path=path,
            database=database_name,
            table=table_name,
            schema_file_path=schema_path,
            dataset=True
        )
        client = boto3.client("glue", region_name="us-east-1")

        response = client.get_table(DatabaseName=database_name, Name=table_name)
        assert response["Table"]["Name"] == table_name
        assert (
            response["Table"]["StorageDescriptor"]["Columns"] ==
            [{"Name": "fp_id", "Type": "string", "Comment": "First party id"}]
        )
        assert (
            response["Table"]["StorageDescriptor"]["InputFormat"] ==
            "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
        )
        assert (
            response["Table"]["PartitionKeys"] ==
            [{"Name": "vector", "Type": "int", "Comment": "User vector"}]
        )
        assert (
            response["Table"]["StorageDescriptor"]["Location"] ==
            f"s3://test/{database_name}/{table_name}"
        )


def test_create_json_table(mock_athena_backend, mock_s3_bucket, mock_glue_database):
    schema_path = os.path.join(os.path.dirname(__file__), "test_schema.yml")
    table_name = "test_table"
    database_name = "test-db"
    path = f"s3://test/{database_name}/{table_name}"
    create_json_table(
        table=table_name,
        path=path,
        schema_file_path=schema_path,
        database=database_name
    )
    client = boto3.client("glue", region_name="us-east-1")

    response = client.get_table(DatabaseName=database_name, Name=table_name)
    assert (
        response["Table"]["Name"] ==
        table_name
    )
    assert (
        response["Table"]["StorageDescriptor"]["Columns"] ==
        [{"Name": "fp_id", "Type": "string", "Comment": "First party id"}]
    )
    assert (
        response["Table"]["StorageDescriptor"]["InputFormat"] ==
        "org.apache.hadoop.mapred.TextInputFormat"
    )
    assert (
        response["Table"]["PartitionKeys"] ==
        [{"Name": "vector", "Type": "int", "Comment": "User vector"}]
    )
    assert (
        response["Table"]["StorageDescriptor"]["Location"] ==
        f"s3://test/{database_name}/{table_name}"
    )


def test_create_parquet_table(mock_athena_backend, mock_s3_bucket, mock_glue_database):
    schema_path = os.path.join(os.path.dirname(__file__), "test_schema.yml")
    table_name = "test_table"
    database_name = "test-db"
    path = f"s3://test/{database_name}/{table_name}"
    create_parquet_table(
        database=database_name,
        table=table_name,
        path=path,
        schema_file_path=schema_path
    )
    client = boto3.client("glue", region_name="us-east-1")

    response = client.get_table(DatabaseName=database_name, Name=table_name)
    assert response["Table"]["Name"] == table_name
    assert (
        response["Table"]["StorageDescriptor"]["Columns"] ==
        [{"Name": "fp_id", "Type": "string", "Comment": "First party id"}]
    )
    assert (
        response["Table"]["StorageDescriptor"]["InputFormat"] ==
        "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
    )
    assert (
        response["Table"]["PartitionKeys"] ==
        [{"Name": "vector", "Type": "int", "Comment": "User vector"}]
    )
    assert (
        response["Table"]["StorageDescriptor"]["Location"] ==
        f"s3://test/{database_name}/{table_name}"
    )


def test_create_iceberg_table_from_schema_file(mock_athena_backend, mock_s3_bucket, mock_glue_database):
    """
    Since create_iceberg_table executes sql, the actual table creation cannot be mocked with moto.
    Therefore this just tests that calling the wrapper doesn't raise errors.
    And tests expected SQL for table creation.
    """
    schema_path = os.path.join(os.path.dirname(__file__), "test_schema.yml")
    table_name = "test_table"
    database_name = "test-db"
    path = f"s3://test/{database_name}/{table_name}"
    create_iceberg_table(
        database=database_name,
        table=table_name,
        path=path,
        schema_file_path=schema_path,
    )

    queries = wr.athena.list_query_executions()
    assert len(queries) == 1
    assert (
        re.sub(
            r"\s",
            "",
            """
                CREATE TABLE IF NOT EXISTS test_table (
                    fp_id string COMMENT 'First party id',
                    vector int COMMENT 'User vector'
                )
                COMMENT 'test_description'
                PARTITIONED BY (vector)
                LOCATION 's3://test/test-db/test_table'
                TBLPROPERTIES (
                    'format'='parquet',
                    'table_type' ='ICEBERG'
                )
            """,
        )
        == re.sub(r"\s", "", wr.athena.get_query_execution(query_execution_id=queries[0])["Query"])
    )


@pytest.mark.parametrize(
    "has_partition_column, partition_column_in_columns", [(True, True), (True, False), (False, False)]
)
def test_create_iceberg_table_from_columns_list(
    mock_athena_backend, mock_s3_bucket, mock_glue_database, has_partition_column, partition_column_in_columns
):
    """
    Since create_iceberg_table executes sql, the actual table creation cannot be mocked with moto.
    Therefore this just tests that calling the wrapper doesn't raise errors.
    And tests expected SQL for table creation.
    """
    table_name = "test_table_from_parameters"
    database_name = "test-db"
    path = f"s3://test/{database_name}/{table_name}"

    description = "test_table_from_parameters_description"

    columns_types = {
        "id": "string",
        "value": "map<string,float>",
    }
    if has_partition_column and partition_column_in_columns:
        columns_types["partition_col"] = "string"

    columns_comments = {
        "id": "User external identifier",
        "value": "User attribute value",
    }
    if has_partition_column:
        columns_comments["partition_col"] = "Partition column comment"

    partitions_types = {}
    if has_partition_column:
        partitions_types = {
            "partition_col": "string",
        }

    create_iceberg_table(
        database=database_name,
        table=table_name,
        path=path,
        columns_types=columns_types,
        columns_comments=columns_comments,
        partitions_types=partitions_types,
        description=description,
    )

    queries = wr.athena.list_query_executions()
    assert len(queries) == 1
    assert (
        re.sub(
            r"\s",
            "",
            f"""
                CREATE TABLE IF NOT EXISTS test_table_from_parameters (
                    id string COMMENT 'User external identifier',
                    value map<string,float> COMMENT 'User attribute value'
                    {",partition_col string COMMENT 'Partition column comment'" if has_partition_column else ""}
                )
                COMMENT 'test_table_from_parameters_description'
                {"PARTITIONED BY (partition_col)" if has_partition_column else ""}
                LOCATION 's3://test/test-db/test_table_from_parameters'
                TBLPROPERTIES (
                    'format'='parquet',
                    'table_type' ='ICEBERG'
                )
            """,
        )
        == re.sub(r"\s", "", wr.athena.get_query_execution(query_execution_id=queries[0])["Query"])
    )


def test_validate_table_input_schema_file():
    schema_path = os.path.join(os.path.dirname(__file__), "test_schema.yml")
    columns_types = None
    partitions_types = None

    validate_table_input(
        schema_path,
        columns_types,
        partitions_types
    )


def test_validate_table_input_dtype():
    schema_path = None
    columns_types = {"test": "value"}
    partitions_types = {"test": "value"}

    validate_table_input(
        schema_path,
        columns_types,
        partitions_types
    )


def test_validate_table_no_schema():
    schema_path = None
    columns_types = None
    partitions_types = None
    with pytest.raises(ValueError) as e:

        validate_table_input(
            schema_path,
            columns_types,
            partitions_types
        )

        assert "Supply either only schema_file_path or columns_types/partitions_types" in str(e)


def test_validate_wrong_path():
    database_name = "test_db"
    table_name = "test-table"
    path = f"s3://test/{table_name}"
    with pytest.raises(ValueError) as e:

        validate_path(
            table_name,
            database_name,
            path,
        )

        assert "Database and table required in path" in str(e)


def test_validate_table_no_s3():
    database_name = "test_db"
    table_name = "test-table"
    path = f"test/{table_name}"
    with pytest.raises(ValueError) as e:

        validate_path(
            table_name,
            database_name,
            path,
        )

        assert "path has to start with s3://" in str(e)


def test_create_parquet_table_skip_path(mock_athena_backend, mock_s3_bucket, mock_glue_database):
    schema_path = os.path.join(os.path.dirname(__file__), "test_schema.yml")
    table_name = "test_table"
    database_name = "test-db"
    path = "s3://test/"
    create_parquet_table(
        database=database_name,
        table=table_name,
        path=path,
        schema_file_path=schema_path,
        skip_path_validation=True
    )
    client = boto3.client("glue", region_name="us-east-1")

    response = client.get_table(DatabaseName=database_name, Name=table_name)
    assert response["Table"]["Name"] == table_name
    assert (
        response["Table"]["StorageDescriptor"]["Columns"] ==
        [{"Name": "fp_id", "Type": "string", "Comment": "First party id"}]
    )
    assert (
        response["Table"]["StorageDescriptor"]["InputFormat"] ==
        "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
    )
    assert (
        response["Table"]["PartitionKeys"] ==
        [{"Name": "vector", "Type": "int", "Comment": "User vector"}]
    )
    assert (
        response["Table"]["StorageDescriptor"]["Location"] ==
        "s3://test/"
    )


def test_create_json_serialization(mock_athena_backend, mock_s3_bucket, mock_glue_database):
    schema_path = os.path.join(os.path.dirname(__file__), "test_schema.yml")
    table_name = "test_table"
    database_name = "test-db"
    path = "s3://test/"
    create_json_table(
        database=database_name,
        table=table_name,
        path=path,
        schema_file_path=schema_path,
        skip_path_validation=True,
        serde_library="org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe",
        compression="gzip",
        )
    client = boto3.client("glue", region_name="us-east-1")

    response = client.get_table(DatabaseName=database_name, Name=table_name)
    assert response["Table"]["Name"] == table_name
    assert (
        response["Table"]["StorageDescriptor"]["SerdeInfo"]["SerializationLibrary"] ==
        "org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe"
    )
    assert (
        response["Table"]["Parameters"]["compressionType"] ==
        "gzip"
    )


def test_create_csv_table(mock_athena_backend, mock_s3_bucket, mock_glue_database):
    schema_path = os.path.join(os.path.dirname(__file__), "test_schema.yml")
    table_name = "test_table"
    database_name = "test-db"
    path = f"s3://test/{database_name}/{table_name}"
    create_csv_table(
        database=database_name,
        table=table_name,
        path=path,
        schema_file_path=schema_path
    )
    client = boto3.client("glue", region_name="us-east-1")

    response = client.get_table(DatabaseName=database_name, Name=table_name)
    assert response["Table"]["Name"] == table_name
    assert (
        response["Table"]["StorageDescriptor"]["Columns"] ==
        [{"Name": "fp_id", "Type": "string", "Comment": "First party id"}]
    )
    assert (
        response["Table"]["StorageDescriptor"]["InputFormat"] ==
        "org.apache.hadoop.mapred.TextInputFormat"
    )
    assert (
        response["Table"]["PartitionKeys"] ==
        [{"Name": "vector", "Type": "int", "Comment": "User vector"}]
    )
    assert (
        response["Table"]["StorageDescriptor"]["Location"] ==
        f"s3://test/{database_name}/{table_name}"
    )


def test_extract_table_creation_params(mock_athena_backend, mock_glue_database):
    schema_path = os.path.join(os.path.dirname(__file__), "test_schema.yml")
    table_name = "test_table"
    database_name = "test-db"
    path = f"s3://test/{database_name}/{table_name}"
    database, columns_types, partitions_types, description, columns_comments = extract_table_creation_params(
        database=database_name,
        table=table_name,
        path=path,
        schema_file_path=schema_path,
        columns_types=None,
        partitions_types=None,
        description=None,
        columns_comments=None,
        skip_path_validation=False,
    )
    assert database == database_name
    assert columns_types == {"fp_id": "string"}
    assert partitions_types == {"vector": "int"}
    assert description == "test_description"
    assert columns_comments == {"fp_id": "First party id", "vector": "User vector"}
