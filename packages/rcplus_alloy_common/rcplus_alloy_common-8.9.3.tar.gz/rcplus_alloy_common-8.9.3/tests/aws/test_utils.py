import sys
from datetime import datetime, timezone

import pytest

from rcplus_alloy_common.aws.utils import (
    datetime_to_str,
    str_to_datetime,
)


def test_datetime_to_str():
    dt_obj = datetime(2021, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    assert datetime_to_str(dt_obj, format="dynamodb") == "2021-01-01T00:00:00+00:00"
    assert datetime_to_str(dt_obj, format="athena") == "2021-01-01 00:00:00.0"


def test_str_to_datetime():
    expected_obj = datetime(2021, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    assert str_to_datetime("2021-01-01T00:00:00+00:00", format="dynamodb") == expected_obj
    assert str_to_datetime("2021-01-01 00:00:00.0", format="athena") == expected_obj

    with pytest.raises(ValueError):
        str_to_datetime("2021-01-01T00:00:00+00:00", format="athena")


@pytest.mark.skipif(sys.version_info >= (3, 11), reason="Python 3.11 supports datetime without a T separator")
def test_str_to_datetime_exceptions():
    with pytest.raises(ValueError):
        str_to_datetime("2021-01-01 00:00:00.0", format="dynamodb")


def test_str_to_datetime_and_back():
    assert (
        str_to_datetime(
            datetime_to_str(datetime(2021, 1, 1, 0, 0, 0, tzinfo=timezone.utc), format="dynamodb"),
            format="dynamodb"
        ) == datetime(2021, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    )
    assert (
        str_to_datetime(
            datetime_to_str(datetime(2021, 1, 1, 0, 0, 0, tzinfo=timezone.utc), format="athena"),
            format="athena"
        ) == datetime(2021, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    )


def test_datetime_to_str_and_back():
    assert (
        datetime_to_str(
            str_to_datetime("2021-01-01T00:00:00+00:00", format="dynamodb"),
            format="dynamodb"
        ) == "2021-01-01T00:00:00+00:00"
    )
    assert (
        datetime_to_str(
            str_to_datetime("2021-01-01T00:00:00+00:00", format="dynamodb"),
            format="athena"
        ) == "2021-01-01 00:00:00.0"
    )
    assert (
        datetime_to_str(
            str_to_datetime("2021-01-01 00:00:00.0", format="athena"),
            format="athena"
        ) == "2021-01-01 00:00:00.0"
    )
    assert (
        datetime_to_str(
            str_to_datetime("2021-01-01 00:00:00.0", format="athena"),
            format="dynamodb"
        ) == "2021-01-01T00:00:00+00:00"
    )


def test_convert_to_unixtime():
    assert str_to_datetime("2021-01-01T00:00:00+00:00", format="dynamodb").timestamp() == 1609459200.0
    assert str_to_datetime("2021-01-01 00:00:00", format="dynamodb").timestamp() == 1609459200.0
    assert str_to_datetime("2021-01-01 00:00:00.0").timestamp() == 1609459200.0
