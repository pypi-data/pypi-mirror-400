import logging

import boto3
import pytest
from moto import mock_s3

from rcplus_alloy_common import configure_logger
from rcplus_alloy_common.logging import AlloyStreamHandler

MODELS_BUCKET = "models-bucket"
TENANT = "tenant_1"


def remove_custom_handlers(logger: logging.Logger) -> None:
    for handler in logger.handlers:
        if isinstance(handler, AlloyStreamHandler):
            logger.removeHandler(handler)


class LoggingContext:
    def __init__(self, caplog, **kwargs):
        self.params = kwargs
        self.logger = None
        self.original_handlers = None
        self.old_formatter = None
        self.caplog = caplog

    def __enter__(self):
        # copy original formatters in order to restore them at the end of the test
        self.original_handlers = [(x, x.formatter) for x in logging.root.handlers]
        self.old_formatter = self.caplog.handler.formatter
        self.logger = configure_logger(**self.params)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # restore original formatters
        for handler in logging.root.handlers:
            logging.root.removeHandler(handler)
        for handler, formatter in self.original_handlers:
            logging.root.addHandler(handler)
            handler.setFormatter(formatter)

        # restore original caplog formatter
        self.caplog.handler.setFormatter(self.old_formatter)

        # remove custom handlers
        remove_custom_handlers(logging.root)


@pytest.fixture(scope="function")
def logger(request, caplog):
    with LoggingContext(caplog, **request.param) as context:
        yield context.logger


@pytest.fixture
def mock_s3_bucket():
    with mock_s3():
        client = boto3.client("s3")
        client.create_bucket(Bucket="test")
        client.put_object(Body="test", Bucket="test", Key="data/test.txt")
        client.put_object(Body=bytes.fromhex("0123456789abcdef"), Bucket="test", Key="data/test.bin")
        yield client


@pytest.fixture
def mock_model_s3():
    with mock_s3():
        client = boto3.client("s3")
        client.create_bucket(Bucket=MODELS_BUCKET)

        with open("tests/data/inference_age.yaml") as params:
            params_path = f"{TENANT}/age/inference.yaml"
            client.put_object(Bucket=MODELS_BUCKET, Key=params_path, Body=params.read().encode())

        with open("tests/data/inference_gender.yaml") as params:
            params_path = f"{TENANT}/gender/inference.yaml"
            client.put_object(Bucket=MODELS_BUCKET, Key=params_path, Body=params.read().encode())

        yield client
