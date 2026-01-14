import os
import pytest
from copy import deepcopy

from rcplus_alloy_common.aws.wr_utils import (
    get_partition_columns_with_type,
    read_table_from_yaml_schema,
    get_columns_with_comments,
    get_columns_with_types,
    get_partition_columns_list,
    get_sql_columns_with_comments,
    normalize_column_description,
)

test_schema = {
    "name": "test_table_2",
    "description": "test_description",
    "columns": [
        {"name": "fp_id", "type": "string", "description": "First party id"},
    ],
    "external": {"partitions": [
        {"name": "vector", "type": "int", "description": "User vector"},
    ]
    }
}


def test_read_table_from_yaml_schema():
    schema_path = os.path.join(os.path.dirname(__file__), "test_schema.yml")
    table_name = "test_table_2"
    schema = read_table_from_yaml_schema(schema_path, table_name)
    assert schema == test_schema


def test_get_partition_columns_with_type():
    result = get_partition_columns_with_type(test_schema)
    assert result == {"vector": "int"}


def test_get_partition_columns_list():
    result = get_partition_columns_list(test_schema)
    assert result == ["vector"]


def test_get_columns_with_types_non_partition():
    result = get_columns_with_types(test_schema, include_partition=False)

    assert result == {"fp_id": "string"}


def test_get_columns_with_types_with_partition():
    result = get_columns_with_types(test_schema, include_partition=True)

    assert result == {"fp_id": "string", "vector": "int"}


def test_get_columns_with_comments():
    result = get_columns_with_comments(test_schema)

    assert result == {"fp_id": "First party id", "vector": "User vector"}


def test_get_sql_columns_with_comments():
    result = get_sql_columns_with_comments(test_schema)

    assert result == "fp_id string COMMENT 'First party id', vector int COMMENT 'User vector'"


def test_get_sql_column_with_comments_space_in_column():
    incorrect_schema = {
        "name": "test_table_2",
        "description": "test_description",
        "columns": [
            {"name": "fp_ id", "type": "string", "description": "First party id"},
        ],
        "external": {"partitions": [
            {"name": "vector", "type": "int", "description": "User vector"},
        ]
        }
    }
    with pytest.raises(ValueError):
        get_sql_columns_with_comments(incorrect_schema)


def test_get_sql_column_with_comments_hyphen_in_description():
    incorrect_schema = {
        "name": "test_table_2",
        "description": "test_description",
        "columns": [
            {"name": "fp_id", "type": "string", "description": "First party id"},
        ],
        "external": {"partitions": [
            {"name": "vector", "type": "int", "description": "User' vector"},
        ]
        }
    }
    with pytest.raises(ValueError):
        get_sql_columns_with_comments(incorrect_schema)


def test_normalize_column_description():
    description = "First party id\n" * 100
    result = normalize_column_description(description)
    assert len(result) == 255
    assert "\n" not in result


def test_get_columns_with_comments_long_description():
    test_schema_long = deepcopy(test_schema)
    long_description = "First party id\n" * 100
    test_schema_long["columns"][0]["description"] = long_description
    result = get_columns_with_comments(test_schema_long)

    assert result == {"fp_id": long_description.replace("\n", " ")[0:255], "vector": "User vector"}


def test_get_sql_column_with_comments_hyphen_in_long_description():
    test_schema_long = deepcopy(test_schema)
    long_description = "First party id" * 100
    test_schema_long["columns"][0]["description"] = long_description
    result = get_sql_columns_with_comments(test_schema_long)
    assert result == f"fp_id string COMMENT '{long_description[0:255]}', vector int COMMENT 'User vector'"
