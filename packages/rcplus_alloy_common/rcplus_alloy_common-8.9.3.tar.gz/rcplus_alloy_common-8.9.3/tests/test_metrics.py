"""
Metrics functions tests
"""
import asyncio
import logging
from unittest.mock import Mock

import pytest
import requests

from rcplus_alloy_common import make_single_metric
from rcplus_alloy_common import get_request_retry_session
from rcplus_alloy_common import publish_metrics_sync
from rcplus_alloy_common import metrics
from rcplus_alloy_common import publish_metrics_async
from rcplus_alloy_common import is_valid_metric


def test_get_request_retry_session_return_type():
    session = get_request_retry_session()
    assert isinstance(session, requests.Session)


def test_make_single_metric_required_params():
    with pytest.raises(TypeError):
        # noinspection PyArgumentList
        make_single_metric()


def test_make_single_metric_default_value():
    metric = make_single_metric("test_metric", 1)
    assert isinstance(metric, dict)
    assert "interval" in metric
    assert metric["interval"] > 0
    assert "time" in metric
    assert metric["time"] > 0
    assert "tags" in metric
    assert isinstance(metric["tags"], list)
    assert len(metric["tags"]) == 3
    assert "env=undefined" in metric["tags"]


def test_make_single_metric_custom_value():
    metric = make_single_metric("test_metric", 1, interval=86400, extra_tags=["env=test"])
    assert isinstance(metric, dict)
    assert "name" in metric
    assert metric["name"] == "test_metric"
    assert "value" in metric
    assert metric["value"] == 1
    assert "interval" in metric
    assert metric["interval"] == 86400
    assert "tags" in metric
    assert isinstance(metric["tags"], list)
    assert len(metric["tags"]) == 3
    assert "env=test" in metric["tags"]


def test_is_valid_metric_true():
    metric = make_single_metric("test_metric", 1)
    assert is_valid_metric(metric)


def test_is_valid_metric_false():
    assert not is_valid_metric({})


def test_publish_metrics_async_required_params():
    with pytest.raises(TypeError):
        # noinspection PyArgumentList
        publish_metrics_async()


def test_publish_metrics_async_event_loop(monkeypatch):
    metric = make_single_metric("test_metric", 1)

    get_event_loop_mock = Mock()
    monkeypatch.setattr(asyncio, "get_event_loop", get_event_loop_mock)
    publish_metrics_async(metric)

    assert get_event_loop_mock.call_count == 1


@pytest.mark.asyncio
async def test_publish_metrics_async_exec(monkeypatch):
    publish_metrics_sync_mock = Mock()
    monkeypatch.setattr(metrics, "publish_metrics_sync", publish_metrics_sync_mock)

    metric = make_single_metric("test_metric", 1)

    await publish_metrics_async(metric)

    assert publish_metrics_sync_mock.call_count == 1


def test_publish_metrics_sync_required_params():
    with pytest.raises(TypeError):
        # noinspection PyArgumentList
        publish_metrics_sync()


def test_publish_metrics_sync_exec_failures(caplog):
    metric = make_single_metric("test_metric", 1)

    # ConnectionError
    publish_metrics_sync(
        metric, retry_count=1, request_timeout=1,
        api_key="test", api_user="test", api_endpoint="http://127.0.0.1",
    )
    assert [record for record in caplog.records if record.message.startswith("Failed to publish metrics")]
    caplog.clear()

    # TODO: Should we check all the possible situations? Commented the test for now.
    # ConnectTimeout
    # publish_metrics_sync(
    #     metric, retry_count=1, request_timeout=1,
    #     api_key="test", api_user="test", api_endpoint="http://192.168.1.2",
    # )
    # assert [record for record in caplog.records if record.message.startswith("Failed to publish metrics")]
    # caplog.clear()

    # TODO: Should we rely on 3rd party service? This is httpbin.org in this case. Commented the tests for now
    # RetryError
    # publish_metrics_sync(
    #     metric, retry_count=1, request_timeout=1,
    #     api_key="test", api_user="test", api_endpoint="http://httpbin.org/status/503",
    # )
    # assert [record for record in caplog.records if record.message.startswith("Failed to publish metrics")]
    # caplog.clear()

    # HTTPError
    # publish_metrics_sync(
    #     metric, retry_count=1, request_timeout=1,
    #     api_key="test", api_user="test", api_endpoint="http://httpbin.org/status/404",
    # )
    # assert [record for record in caplog.records if record.message.startswith("Failed to publish metrics")]
    # caplog.clear()


def test_publish_metrics_sync_exec():
    metric = make_single_metric("test_metric", 1)
    # TODO: Should we rely on 3rd party service? This is httpbin.org in this case.
    publish_metrics_sync(metric, api_key="test", api_user="test", api_endpoint="http://httpbin.org/status/200")


def test_env_tag_with_extra_env():
    metric = make_single_metric("test_metric", 1, env_tag="test", extra_tags=["env=wrong"])
    assert isinstance(metric, dict)
    assert "tags" in metric
    assert isinstance(metric["tags"], list)
    assert len(metric["tags"]) == 3
    assert "env=test" in metric["tags"]
    assert "env=wrong" not in metric["tags"]


def test_env_tag_with_tenant():
    metric = make_single_metric("test_metric", 1, env_tag="test", tenant="test_tenant")
    assert isinstance(metric, dict)
    assert "tags" in metric
    assert isinstance(metric["tags"], list)
    assert len(metric["tags"]) == 4
    assert "tenant=test_tenant" in metric["tags"]


def test_env_tag_with_no_tenant_override(caplog):
    metric = make_single_metric("test_metric", 1, env_tag="test", extra_tags=["tenant=tenant1"], tenant="test_tenant")
    assert isinstance(metric, dict)
    assert "tags" in metric
    assert isinstance(metric["tags"], list)
    assert len(metric["tags"]) == 4
    assert "tenant=test_tenant" in metric["tags"]
    assert "tenant=tenant1" not in metric["tags"]

    # if there is a conflict for the tenant tag the warning message is issued
    assert [record for record in caplog.records if record.levelno == logging.WARNING]


def test_env_tag_with_no_malformed_tenant_set():
    with pytest.raises(ValueError) as exc_info:
        make_single_metric("test_metric", 1, env_tag="test", tenant=["test_tenant"])

    assert "Expecting tenant value as string" in str(exc_info.value)
