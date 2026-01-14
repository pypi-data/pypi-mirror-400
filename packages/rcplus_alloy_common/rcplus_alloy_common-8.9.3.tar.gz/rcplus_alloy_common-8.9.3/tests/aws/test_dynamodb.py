from datetime import datetime, timezone
import uuid

import pandas as pd
import awswrangler as wr
import pyarrow as pa

from rcplus_alloy_common.aws.dynamodb import DynamoDBAthenaSynchronizer, AttributeUpdatesItem


def get_item(client, item_id):
    response = client.get_item(
        TableName="test",
        Key={"id": {"S": item_id}},
    )
    return response["Item"]


def test_tmp_table(
    mock_dynamodb_table,
    mock_s3_bucket,
    mock_glue_database,
):
    handler = DynamoDBAthenaSynchronizer(
        table_name="test",
        s3_bucket="test",
        athena_table_name="athena_table__tmp",
    )

    # NOTE: `handler.sync_table()` is called in the constructor so the snapshot must exist
    assert not handler.table_snapshot.empty
    assert "recent_timestamp" in handler.table_snapshot.id.tolist()
    assert "old_timestamp" in handler.table_snapshot.id.tolist()
    assert "no_timestamp" in handler.table_snapshot.id.tolist()

    # list all tables
    response = mock_glue_database.get_tables(
        DatabaseName=wr.config.database,
    )

    tmp_table = [table for table in response["TableList"] if table["Name"] == "athena_table__tmp"][0]
    assert tmp_table["Name"] == "athena_table__tmp"
    assert tmp_table["StorageDescriptor"]["Location"].startswith(f"s3://test/{wr.config.database}/athena_table__tmp")

    df = wr.s3.read_parquet(f"s3://test/{wr.config.database}/athena_table__tmp")
    pd.testing.assert_frame_equal(df, handler.table_snapshot.reset_index(drop=True))  # we coerce the types in Athena


def test_tmp_table_filter_expression(
    mock_dynamodb_table,
    mock_s3_bucket,
    mock_glue_database,
):
    handler = DynamoDBAthenaSynchronizer(
        table_name="test",
        s3_bucket="test",
        athena_table_name="athena_table__tmp",
        filter_expression="attribute_not_exists(p_timestamp) OR p_timestamp > :p",
        expression_attribute_values={":p": "2023-01-01T00:00:00.000"},
    )

    # NOTE: `handler.sync_table()` is called in the constructor so the snapshot must exist
    assert not handler.table_snapshot.empty
    assert "recent_timestamp" in handler.table_snapshot.id.tolist()
    assert "old_timestamp" not in handler.table_snapshot.id.tolist()
    assert "no_timestamp" in handler.table_snapshot.id.tolist()


def test_update(
    mock_dynamodb_table,
    mock_s3_bucket,
    mock_glue_database,
):
    handler = DynamoDBAthenaSynchronizer(
        table_name="test",
        s3_bucket="test",
        athena_table_name="athena_table__tmp",
    )

    now = datetime.now(tz=timezone.utc)
    handler.update(
        items=[
            ({"id": "recent_timestamp"}, {"p_timestamp": AttributeUpdatesItem(Action="PUT", Value=now)}),
            ({"id": "old_timestamp"}, {"p_timestamp": AttributeUpdatesItem(Action="PUT", Value=now)}),
            ({"id": "no_timestamp"}, {"p_timestamp": AttributeUpdatesItem(Action="PUT", Value=now)}),
        ],
        sync_athena=False,
    )

    assert get_item(mock_dynamodb_table, "recent_timestamp")["p_timestamp"]["S"] == now.isoformat()
    assert get_item(mock_dynamodb_table, "old_timestamp")["p_timestamp"]["S"] == now.isoformat()
    assert get_item(mock_dynamodb_table, "no_timestamp")["p_timestamp"]["S"] == now.isoformat()


def test_update_multiple_columns(
    mock_dynamodb_table,
    mock_s3_bucket,
    mock_glue_database,
):
    handler = DynamoDBAthenaSynchronizer(
        table_name="test",
        s3_bucket="test",
        athena_table_name="athena_table__tmp",
    )

    now = datetime.now(tz=timezone.utc)
    handler.update(
        items=[
            (
                {"id": "another_timestamp"},
                {
                    "p_timestamp_2": AttributeUpdatesItem(Action="PUT", Value=now),
                    "p_timestamp": AttributeUpdatesItem(Action="PUT", Value=now),
                },
            ),
        ],
        sync_athena=False,
    )

    assert get_item(mock_dynamodb_table, "another_timestamp")["p_timestamp_2"]["S"] == now.isoformat()
    assert get_item(mock_dynamodb_table, "another_timestamp")["p_timestamp"]["S"] == now.isoformat()


def test_update_sync_athena(
    mock_dynamodb_table,
    mock_s3_bucket,
    mock_glue_database,
):
    handler = DynamoDBAthenaSynchronizer(
        table_name="test",
        s3_bucket="test",
        athena_table_name="athena_table__tmp",
    )

    now = datetime.now(tz=timezone.utc)
    handler.update(
        items=[
            ({"id": "recent_timestamp"}, {"p_timestamp": AttributeUpdatesItem(Action="PUT", Value=now)}),
            ({"id": "old_timestamp"}, {"p_timestamp": AttributeUpdatesItem(Action="PUT", Value=now)}),
            ({"id": "no_timestamp"}, {"p_timestamp": AttributeUpdatesItem(Action="PUT", Value=now)}),
            (
                {"id": "another_timestamp"},
                {
                    "p_timestamp_2": AttributeUpdatesItem(Action="PUT", Value=now),
                    "p_timestamp": AttributeUpdatesItem(Action="PUT", Value=now),
                },
            ),
        ],
        sync_athena=True,
    )

    assert get_item(mock_dynamodb_table, "recent_timestamp")["p_timestamp"]["S"] == now.isoformat()
    assert "p_timestamp_2" not in get_item(mock_dynamodb_table, "recent_timestamp")
    assert get_item(mock_dynamodb_table, "old_timestamp")["p_timestamp"]["S"] == now.isoformat()
    assert "p_timestamp_2" not in get_item(mock_dynamodb_table, "old_timestamp")
    assert get_item(mock_dynamodb_table, "no_timestamp")["p_timestamp"]["S"] == now.isoformat()
    assert "p_timestamp_2" not in get_item(mock_dynamodb_table, "no_timestamp")
    assert get_item(mock_dynamodb_table, "another_timestamp")["p_timestamp_2"]["S"] == now.isoformat()
    assert get_item(mock_dynamodb_table, "another_timestamp")["p_timestamp"]["S"] == now.isoformat()

    df = wr.s3.read_parquet(f"s3://test/{wr.config.database}/athena_table__tmp")
    pd.testing.assert_frame_equal(df, handler.table_snapshot.reset_index(drop=True))  # we coerce the types in Athena


def test_update_with_custom_columns_dtypes(
    mock_dynamodb_table,
    mock_s3_bucket,
    mock_glue_database,
):
    handler = DynamoDBAthenaSynchronizer(
        table_name="test",
        s3_bucket="test",
        athena_table_name="athena_table__tmp",
        columns=["custom_str_column", "custom_int_column"],
        dtypes={"custom_str_column": "string", "custom_int_column": "Int64"},
        index_col="id",
    )

    now = datetime.now(tz=timezone.utc)
    handler.update(
        items=[
            ({"id": "recent_timestamp"}, {"p_timestamp": AttributeUpdatesItem(Action="PUT", Value=now)}),
        ],
        sync_athena=True,
    )

    df = wr.s3.read_parquet(f"s3://test/{wr.config.database}/athena_table__tmp")
    pd.testing.assert_frame_equal(df, handler.table_snapshot.reset_index(drop=True))  # we coerce the types in Athena
    assert df["custom_str_column"].dtype == "string"
    assert df["custom_int_column"].dtype == "Int64"  # NOTE: not all the dtypes are supported


def test_update_drop_timestamp(
    mock_dynamodb_table,
    mock_s3_bucket,
    mock_glue_database,
):
    handler = DynamoDBAthenaSynchronizer(
        table_name="test",
        s3_bucket="test",
        athena_table_name="athena_table__tmp",
    )

    handler.update(
        items=[
            ({"id": "recent_timestamp"}, {"p_timestamp": AttributeUpdatesItem(Value=None, Action="PUT")}),
            ({"id": "old_timestamp"}, {"p_timestamp": AttributeUpdatesItem(Value=None, Action="PUT")}),
            ({"id": "no_timestamp"}, {"p_timestamp": AttributeUpdatesItem(Value=None, Action="PUT")}),
            (
                {"id": "another_timestamp"},
                {
                    "p_timestamp": AttributeUpdatesItem(Value=None, Action="PUT"),
                },
            ),
        ],
        sync_athena=False,
    )

    assert "p_timestamp" not in get_item(mock_dynamodb_table, "recent_timestamp")
    assert "p_timestamp" not in get_item(mock_dynamodb_table, "old_timestamp")
    assert "p_timestamp" not in get_item(mock_dynamodb_table, "no_timestamp")
    assert "p_timestamp" not in get_item(mock_dynamodb_table, "another_timestamp")
    assert "p_timestamp_2" in get_item(mock_dynamodb_table, "another_timestamp")


def test_parse_dates(mock_dynamodb_table):
    df = pd.DataFrame(
        {
            "p_timestamp": ["2021-01-01T00:00:00", "2021-01-01T00:00:00", None],
            "gam_unload_timestamp": ["2021-01-01T00:00:00.000000", "2021-01-01T00:00:00.000000", None],
            "not_a_date": ["20211", "2021", None],
            "is_an_int": [1, 2, 3],
            "is_an_int_with_none": [2021, 2022, None],
            "is_a_float": [2023.05, 2023.06, 2023.07],
            "is_a_bool": [True, False, True],
            "is_a_uuid": [str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())],
            "is_an_object": [{"a": 1}, None, None],
            "is_an_empty_object_not_a_date": [None, None, None],
            "is_an_empty_object_and_a_date": [None, None, None],
        }
    )
    dtypes = {"is_an_empty_object_not_a_date": "string", "is_an_empty_object_and_a_date": "datetime64[ns, UTC]"}
    df_parsed = DynamoDBAthenaSynchronizer._parse_dates(df.copy(deep=True), dtypes)
    for col in df.columns:
        if col in {"p_timestamp", "gam_unload_timestamp", "is_an_empty_object_and_a_date"}:
            assert df_parsed[col].dtype == "datetime64[ns, UTC]"
        else:
            assert df_parsed[col].dtype == df[col].dtype, f"Column {col} has wrong dtype"


def test_pyarrow_additional_kwargs(
    mock_dynamodb_table,
    mock_s3_bucket,
    mock_glue_database,
):
    schema = pa.schema([("id", pa.string())])

    handler = DynamoDBAthenaSynchronizer(
        table_name="test",
        s3_bucket="test",
        athena_table_name="athena_table__tmp",
        pyarrow_additional_kwargs={"schema": schema},
    )

    # NOTE: `handler.sync_table()` is called in the constructor so the snapshot must exist
    assert not handler.table_snapshot.empty
    assert "id" in handler.table_snapshot.columns.tolist()
    assert len(handler.table_snapshot.columns.tolist()) == 1

    schema = pa.schema([("id", pa.string()), ("p_timestamp", pa.string())])

    handler = DynamoDBAthenaSynchronizer(
        table_name="test",
        s3_bucket="test",
        athena_table_name="athena_table__tmp",
        pyarrow_additional_kwargs={"schema": schema},
    )

    # NOTE: `handler.sync_table()` is called in the constructor so the snapshot must exist
    assert not handler.table_snapshot.empty
    assert "id" in handler.table_snapshot.columns.tolist()
    assert "p_timestamp" in handler.table_snapshot.columns.tolist()
    assert len(handler.table_snapshot.columns.tolist()) == 2


def test_read_non_existing_columns(
    mock_dynamodb_table,
    mock_s3_bucket,
    mock_glue_database,
):
    handler = DynamoDBAthenaSynchronizer(
        table_name="test",
        s3_bucket="test",
        athena_table_name="athena_table__tmp",
        columns=["is_an_empty_object_not_a_date", "is_an_empty_object_and_a_date"],
        dtypes={"is_an_empty_object_not_a_date": "string",
                "is_an_empty_object_and_a_date": "datetime64[ns, UTC]"},
    )

    # NOTE: `handler.sync_table()` is called in the constructor so the snapshot must exist
    assert not handler.table_snapshot.empty
    assert "is_an_empty_object_not_a_date" in handler.table_snapshot.columns.tolist()
    assert "is_an_empty_object_and_a_date" in handler.table_snapshot.columns.tolist()

    assert handler.table_snapshot.is_an_empty_object_not_a_date.dtype == "string"
    assert handler.table_snapshot.is_an_empty_object_and_a_date.dtype == "datetime64[ns, UTC]"
