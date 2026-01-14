import logging

import pytest

from rcplus_alloy_common.exceptions import raise_exception, UncaughtException


def test_raise_fatal_exception(caplog):
    # Test that the exception is passed to the logger
    with pytest.raises(SystemExit) as excinfo:
        raise_exception("Test Exception", fatal=True)
    assert excinfo.value.code == 1

    assert caplog.records[0].exc_info is not None
    assert isinstance(caplog.records[0].exc_info[1], UncaughtException)
    assert "Test Exception" in caplog.records[0].exc_info[1].args
    assert caplog.records[0].levelname == "ERROR"


def test_raise_non_fatal_exception(caplog):
    # Test that the exception is passed to the logger
    raise_exception("Test Exception", fatal=False)
    assert caplog.records[0].exc_info is not None
    assert isinstance(caplog.records[0].exc_info[1], UncaughtException)
    assert "Test Exception" in caplog.records[0].exc_info[1].args
    assert caplog.records[0].levelname == "ERROR"


def test_raise_fatal_exception_from_exception(caplog):
    with pytest.raises(SystemExit) as excinfo:
        raise_exception("Test Exception", from_exc=Exception("Test"), fatal=True, exit_code=2)
    assert excinfo.value.code == 2

    assert isinstance(excinfo.value.__context__, UncaughtException)
    assert isinstance(excinfo.value.__context__.__cause__, Exception)
    assert excinfo.value.__context__.__cause__.args == ("Test",)
    assert excinfo.value.__context__.args == ("Test Exception",)

    assert caplog.records[0].exc_info is not None
    assert isinstance(caplog.records[0].exc_info[1], UncaughtException)
    assert "Test Exception" in caplog.records[0].exc_info[1].args
    assert caplog.records[0].levelname == "ERROR"


def test_raise_non_fatal_exception_from_exception(caplog):
    raise_exception("Test Exception", from_exc=Exception("Test"), fatal=False)
    assert isinstance(caplog.records[0].exc_info[1], UncaughtException)
    assert isinstance(caplog.records[0].exc_info[1].__cause__, Exception)
    assert caplog.records[0].exc_info[1].__cause__.args == ("Test",)
    assert caplog.records[0].exc_info[1].args == ("Test Exception",)
    assert caplog.records[0].levelname == "ERROR"


def test_raise_exception_with_logger(caplog):
    logger = logging.getLogger("my_custom_logger")
    raise_exception("Test Exception", logger=logger, fatal=False)
    assert caplog.records[0].exc_info is not None
    assert isinstance(caplog.records[0].exc_info[1], UncaughtException)
    assert "Test Exception" in caplog.records[0].exc_info[1].args
    assert caplog.records[0].levelname == "ERROR"
    assert caplog.records[0].name == "my_custom_logger"


def test_raise_exception_with_custom_exception(caplog):
    class CustomException(Exception):
        pass

    raise_exception("Test Exception", exception=CustomException, fatal=False)
    assert caplog.records[0].exc_info is not None
    assert isinstance(caplog.records[0].exc_info[1], CustomException)
    assert "Test Exception" in caplog.records[0].exc_info[1].args
    assert caplog.records[0].levelname == "ERROR"
