"""
Logging functions tests
"""
import json
import logging

import airflow  # noqa: F401 airflow is imported to force the RedirectStdHandler to be registered
import pytest
from _pytest.logging import LogCaptureHandler  # noqa: PLC2701

from rcplus_alloy_common.logging import (
    configure_logger,
    configure_existing_logger,
    configure_existing_loggers,
    change_logging_level,
    CustomJsonFormatter,
    CustomLoggingFormatter,
)
from opentelemetry import trace
from opentelemetry.instrumentation.logging import LoggingInstrumentor

from .conftest import LoggingContext
from .celery import ColorFormatter  # NOTE: a fake celery module for testing purposes


def assert_log_level(logger, caplog, log_level):
    caplog.clear()
    if logger.handlers and logger.handlers[0].__class__.__name__ != "NullHandler":
        return False
    logger.debug("DEBUG message")
    logger.info("INFO message")
    logger.warning("WARNING message")
    logger.error("ERROR message")
    assert caplog.records
    assert not [record for record in caplog.records if record.levelno < log_level]
    assert [record for record in caplog.records if record.levelno == log_level]
    caplog.clear()
    return True


def assert_json_format(logger, caplog):
    caplog.clear()
    logger.error("test")
    # assert that the log is in JSON format
    json.loads(caplog.text)
    caplog.clear()


@pytest.fixture
def add_handler_to_root_logger():
    handler = logging.StreamHandler()
    handler.setFormatter(ColorFormatter())
    logging.root.addHandler(handler)
    yield
    logging.root.removeHandler(handler)


@pytest.fixture
def existing_loggers_to_error():
    prev_state = configure_existing_loggers(log_level=logging.ERROR)
    yield
    for logger, level in prev_state.items():
        configure_existing_logger(logger, log_level=level)


@pytest.mark.parametrize("logger", [{"log_name": "my_logger"}], indirect=True)
def test_logger_default_level(logger, caplog):
    assert_log_level(logger, caplog, logging.INFO)


@pytest.mark.parametrize("logger", [{"log_level": logging.ERROR}], indirect=True)
def test_logger_set_level(logger, caplog):
    assert_log_level(logger, caplog, logging.ERROR)


@pytest.mark.parametrize("logger", [{"log_mode": "JSON"}], indirect=True)
def test_json_format(logger, caplog):
    assert_json_format(logger, caplog)


@pytest.mark.parametrize("logger", [{"log_mode": "TEXT"}], indirect=True)
def test_text_format(logger, caplog):
    # assert that the log is not in JSON format
    logger.info("test")
    with pytest.raises(json.decoder.JSONDecodeError):
        json.loads(caplog.text)


@pytest.mark.parametrize("logger", [{"log_mode": "TEXT", "log_level": logging.DEBUG}], indirect=True)
def test_change_log_level(logger, caplog):
    assert_log_level(logger, caplog, logging.DEBUG)
    configure_existing_logger(logger, log_level="WARNING")
    assert_log_level(logger, caplog, logging.WARNING)

    # new_logger should start with the default level (info)
    n_handlers = len(logging.root.handlers)
    new_logger = configure_logger("new_logger")
    assert n_handlers == len(logging.root.handlers)
    assert_log_level(new_logger, caplog, logging.INFO)

    # logger should still be at the warning level
    assert_log_level(logger, caplog, logging.WARNING)

    # change the log level of the new logger
    configure_existing_logger(new_logger, log_level="ERROR")
    assert_log_level(new_logger, caplog, logging.ERROR)

    # # change all the loggers to debug
    # prev_state = configure_existing_loggers(log_level="DEBUG")
    # assert_log_level(logger, caplog, logging.DEBUG)
    # assert_log_level(new_logger, caplog, logging.DEBUG)
    # for log_name in logging.root.manager.loggerDict:
    #     assert_log_level(logging.getLogger(log_name), caplog, logging.DEBUG)

    # # restore the previous state
    # for logger, level in prev_state.items():
    #     configure_existing_logger(logger, log_level=level)


@pytest.mark.parametrize("logger", [{"log_mode": "JSON", "log_level": logging.DEBUG}], indirect=True)
def test_configure_existing_loggers(logger, caplog, existing_loggers_to_error):  # pylint: disable=unused-argument
    assert_log_level(logger, caplog, logging.ERROR)
    for log_name in logging.root.manager.loggerDict:
        success = assert_log_level(logging.getLogger(log_name), caplog, logging.ERROR)
        if success:
            assert_json_format(logging.getLogger(log_name), caplog)


@pytest.mark.parametrize("logger", [{"log_mode": "TEXT", "log_level": logging.DEBUG}], indirect=True)
def test_configure_two_loggers(logger, caplog):
    assert_log_level(logger, caplog, logging.DEBUG)
    configure_existing_logger(logger, log_level="WARNING")
    n_handlers = len(logging.root.handlers)
    new_logger = configure_logger("new_logger", log_level=logging.ERROR)
    assert n_handlers == len(logging.root.handlers)
    assert_log_level(logger, caplog, logging.WARNING)
    assert_log_level(new_logger, caplog, logging.ERROR)
    new_logger2 = configure_logger("new_logger2", log_level=logging.INFO)
    assert n_handlers == len(logging.root.handlers)
    assert_log_level(logger, caplog, logging.WARNING)
    assert_log_level(new_logger, caplog, logging.ERROR)
    assert_log_level(new_logger2, caplog, logging.INFO)


@pytest.mark.parametrize(
    "logger",
    [
        {
            "log_mode": "JSON",
        }
    ],
    indirect=True,
)
def test_do_configure(logger, caplog):  # pylint: disable=unused-argument
    assert [
        x
        for x in logging.root.handlers
        if isinstance(
            x.formatter,
            (
                CustomJsonFormatter,
                CustomLoggingFormatter,
            ),
        )
    ]


@pytest.mark.parametrize(
    "logger",
    [{"log_mode": "JSON", "skip_handler_types": (LogCaptureHandler,), "skip_handler_modules": None}],
    indirect=True,
)
def test_do_not_configure_types(logger, caplog):  # pylint: disable=unused-argument
    non_configured_handlers = [
        x
        for x in logging.root.handlers
        if not isinstance(
            x.formatter,
            (
                CustomJsonFormatter,
                CustomLoggingFormatter,
            ),
        )
    ]
    assert not [x for x in non_configured_handlers if not isinstance(x, LogCaptureHandler)]


@pytest.mark.parametrize(
    "logger",
    [
        {
            "log_mode": "JSON",
            "skip_handler_modules": (
                "_pytest",
                "airflow.utils.log.logging_mixin",
            ),
        }
    ],
    indirect=True,
)
def test_do_not_configure_modules(logger, caplog):  # pylint: disable=unused-argument
    assert not [
        x
        for x in logging.root.handlers
        if isinstance(
            x.formatter,
            (
                CustomJsonFormatter,
                CustomLoggingFormatter,
            ),
        )
    ]


@pytest.mark.parametrize(
    "logger",
    [{"log_mode": "JSON", "skip_handler_names": ("LogCaptureHandler",), "skip_handler_modules": None}],
    indirect=True,
)
def test_do_not_configure_names(logger, caplog):  # pylint: disable=unused-argument
    non_configured_handlers = [
        x
        for x in logging.root.handlers
        if not isinstance(
            x.formatter,
            (
                CustomJsonFormatter,
                CustomLoggingFormatter,
            ),
        )
    ]
    assert not [x for x in non_configured_handlers if not isinstance(x, LogCaptureHandler)]


def test_warn_unexpected_configuration(caplog, add_handler_to_root_logger):  # pylint: disable=unused-argument
    with LoggingContext(
        caplog,
        log_mode="JSON",
        skip_handler_formatter_modules=None,
    ):
        assert caplog.records[0].message == (
            "Found an handler of type StreamHandler in the root logger. "
            "Changing the formatter of this handler may cause unexpected behavior."
        )
        assert caplog.records[0].levelname == "WARNING"
        assert "Found more than one handler in the root logger. Changed the formatter of " in caplog.records[1].message


def test_warn_unexpected_configuration_without_tests(
    caplog, add_handler_to_root_logger
):  # pylint: disable=unused-argument
    with LoggingContext(
        caplog,
        log_mode="JSON",
        skip_handler_modules=(
            "_pytest",
            "airflow.utils.log.logging_mixin",
        ),
        skip_handler_formatter_modules=None,
    ):
        assert caplog.records[0].message == (
            "Found an handler of type StreamHandler in the root logger. "
            "Changing the formatter of this handler may cause unexpected behavior."
        )
        assert caplog.records[0].levelname == "WARNING"
        assert len(caplog.records) == 1


def test_do_not_warn_celery(
    caplog, add_handler_to_root_logger
):  # pylint: disable=unused-argument
    with LoggingContext(
        caplog,
        log_mode="JSON",
        skip_handler_modules=(
            "_pytest",
            "airflow.utils.log.logging_mixin",
        ),
    ):
        assert not caplog.records


# @pytest.mark.parametrize('logger', [{"log_mode": "JSON"}], indirect=True)
# def test_json_format_for_pywarnings(logger, caplog):
#     import warnings
#     # this test is not working since the warnings are not captured by caplog
#     warnings.warn("test")
#     json.loads(caplog.text)


def test_change_logging_level(caplog):
    logger = logging.getLogger("test_change_logging_level")
    logger.setLevel(logging.DEBUG)
    logger.debug("DEBUG message")
    assert "DEBUG message" in caplog.text
    caplog.clear()
    with change_logging_level(logger, log_level=logging.ERROR):
        logger.debug("DEBUG message")
        assert not caplog.text


@pytest.mark.parametrize("logger", [{"log_name": "my_logger"}], indirect=True)
def test_alloy_tag_for_lambda(logger, monkeypatch, caplog):
    # set relevant environment variables
    monkeypatch.setenv("AWS_LAMBDA_FUNCTION_NAME", "dev-alloy-my-software-component-lambdaname")
    monkeypatch.setenv("SOFTWARE_COMPONENT", "my-software-component")
    logger.error("test")
    assert "alloy.lambda.my-software-component.dev-lambdaname" == json.loads(caplog.text)["alloy_tag"]


@pytest.mark.parametrize("logger", [{"log_name": "my_logger"}], indirect=True)
def test_alloy_tag_for_lambda_preset(logger, monkeypatch, caplog):
    # set relevant environment variables
    monkeypatch.setenv("AWS_LAMBDA_FUNCTION_NAME", "dev-alloy-my-software-component-lambdaname")
    monkeypatch.setenv("SOFTWARE_COMPONENT", "my-software-component")
    monkeypatch.setenv("ALLOY_TAG", "alloy.lambda.my-software-component.dev-another-lambdaname")
    logger.error("test")
    assert "alloy.lambda.my-software-component.dev-another-lambdaname" == json.loads(caplog.text)["alloy_tag"]


@pytest.mark.parametrize("logger", [{"log_name": "my_logger"}], indirect=True)
@pytest.mark.parametrize(
    "env_vars", [
        {
            "AWS_LAMBDA_FUNCTION_NAME": "dev-alloy-my-software-component-lambdaname"
        },
        {
            "SOFTWARE_COMPONENT": "my-software-component",
        },
        {}
    ]
)
def test_alloy_tag_for_lambda_empty(env_vars, logger, monkeypatch, caplog):
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
    logger.error("test")
    assert "alloy_tag" not in json.loads(caplog.text)


@pytest.mark.parametrize("logger", [{"log_mode": "JSON"}], indirect=True)
def test_alloy_logger_long_message(logger, caplog):
    logger.error("0123456789" * 200 + "0")
    assert len(json.loads(caplog.text)["message"]) == 2000
    assert "..." in json.loads(caplog.text)["message"]


@pytest.mark.parametrize("logger", [{"log_mode": "JSON", "log_level": logging.DEBUG}], indirect=True)
def test_alloy_logger_with_otel(logger, caplog):
    LoggingInstrumentor().instrument()
    # Set up a test tracer provider with a service name
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("test-span") as test_span:
        logger.debug("DEBUG message")
    assert "trace_id" in json.loads(caplog.text)
    assert "span_id" in json.loads(caplog.text)
    assert "trace_sampled" in json.loads(caplog.text)
    assert "service_name" in json.loads(caplog.text)
    trace_id_hex = json.loads(caplog.text)["trace_id"]
    trace_id_int = int(trace_id_hex, 16)
    assert trace_id_int == test_span.get_span_context().trace_id != 0
