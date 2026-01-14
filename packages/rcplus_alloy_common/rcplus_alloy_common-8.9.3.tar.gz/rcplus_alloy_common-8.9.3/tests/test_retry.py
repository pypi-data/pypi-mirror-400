"""
Retry decorator tests
"""
# ruff: noqa: PLW0603

import logging

import pytest

from rcplus_alloy_common import retry

count = 3


def test_retry_catch_exception():
    @retry(delay=0.1)
    def failure_func():
        raise ValueError("Fail forever")

    with pytest.raises(Exception):
        failure_func()


def test_retry_catch_specific_exception():
    @retry(exceptions=(ValueError,), delay=0.1)
    def failure_func():
        raise ValueError("Fail forever")

    with pytest.raises(ValueError):
        failure_func()


def test_retry_success():
    global count

    @retry(tries=2, delay=0.1)
    def recoverable_failure_1():
        global count

        count -= 1
        if count > 0:
            raise ValueError("Count not zero")

        return True

    @retry(tries=3, delay=0.1)
    def recoverable_failure_2():
        global count

        count -= 1
        if count > 0:
            raise ValueError("Count not zero")

        return True

    count = 4
    # Fail on too few tries
    with pytest.raises(ValueError):
        recoverable_failure_1()

    count = 4
    # Success on more tries
    assert recoverable_failure_2()


def test_retry_wrong_params():
    with pytest.raises(ValueError):
        retry(tries=0)(lambda: 1)

    with pytest.raises(ValueError):
        retry(delay=0)(lambda: 1)

    with pytest.raises(ValueError):
        retry(backoff=0)(lambda: 1)

    with pytest.raises(ValueError):
        retry(exceptions=tuple())(lambda: 1)


@pytest.mark.parametrize("logger", [{"log_name": "my_logger"}], indirect=True)
def test_retry_logging(logger, caplog):
    @retry(decorator_logger=logger, delay=0.1)
    def failure_func_1():
        raise ValueError("Fail forever 1")

    with pytest.raises(Exception):
        failure_func_1()

    assert [record for record in caplog.records if record.levelno == logging.WARNING]

    caplog.clear()

    @retry(decorator_logger=logger, decorator_logger_level=logging.INFO, delay=0.1)
    def failure_func_2():
        raise ValueError("Fail forever 2")

    with pytest.raises(Exception):
        failure_func_2()

    assert [record for record in caplog.records if record.levelno == logging.INFO]
    assert not [record for record in caplog.records if record.levelno == logging.WARNING]


def test_retry_with_exception_text_filter():
    global count

    @retry(exceptions=(ValueError,), exceptions_filter="not zero", delay=0.1)
    def failure_func_1():
        global count

        count -= 1
        if count > 0:
            raise ValueError("Count not zero")

        return True

    count = 1
    assert failure_func_1()

    @retry(exceptions=(ValueError,), exceptions_filter="not zero", delay=0.1)
    def failure_func_2():
        raise ValueError("Always fail")

    with pytest.raises(ValueError):
        failure_func_2()

    @retry(exceptions=(ValueError,), exceptions_filter="not zero", delay=0.1)
    def failure_func_3():
        global count

        count -= 1
        if count > 0:
            raise KeyError("Count not zero")

        return True

    count = 4
    with pytest.raises(KeyError):
        failure_func_3()


def test_retry_wrong_exception():
    global count

    @retry(exceptions=(ValueError,), delay=0.1)
    def failure_func():
        global count

        count -= 1
        if count > 0:
            raise KeyError("Count not zero")

        return True

    count = 2
    with pytest.raises(KeyError):
        failure_func()
