import pytest

from rcplus_alloy_common.custom_attributes import (
    parse_s3_url,
    read_s3_file_content,
    copy_file_from_s3,
    normalize_label,
)


def test_parse_s3_url():
    s3_url = "s3://test/data/test.txt"
    s3_bucket, s3_path = parse_s3_url(s3_url)
    assert s3_bucket == "test"
    assert s3_path == "data/test.txt"

    with pytest.raises(ValueError) as exc_info:
        s3_url = "https://test/data/test.txt"
        _, _ = parse_s3_url(s3_url)

    assert str(exc_info.value) == f"Failed to parse malformed S3 URL {s3_url}"


def test_read_s3_file_content(mock_s3_bucket):
    s3_url = "s3://test/data/test.txt"
    assert read_s3_file_content(s3_url) == "test"

    with pytest.raises(Exception) as exc_info:
        s3_url = "s3://test/data/not_found.txt"
        read_s3_file_content(s3_url)

    assert "The specified key does not exist" in str(exc_info.value)


def test_copy_file_from_s3_text(mock_s3_bucket):
    s3_url = "s3://test/data/test.txt"
    tmp_path = "/tmp/test.txt"
    copy_file_from_s3(s3_url, tmp_path)
    with open(tmp_path) as tmp_f:
        assert tmp_f.read() == "test"

    with pytest.raises(Exception) as exc_info:
        s3_url = "s3://test/data/not_found.txt"
        copy_file_from_s3(s3_url, tmp_path)

    assert "The specified key does not exist" in str(exc_info.value)


def test_copy_file_from_s3_bin(mock_s3_bucket):
    s3_url = "s3://test/data/test.bin"
    tmp_path = "/tmp/test.bin"
    copy_file_from_s3(s3_url, tmp_path, decode=False)
    with open(tmp_path, "rb") as tmp_f:
        assert tmp_f.read() == bytes.fromhex("0123456789abcdef")


def test_normalize_label():
    assert normalize_label("17", "attr") == "attr_17"
    assert normalize_label("17-20", "attr") == "attr_17_20"
    assert normalize_label("17+", "attr") == "attr_17_plus"
    assert normalize_label("value", "attr") == "value"
