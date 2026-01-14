from importlib import reload
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from airflow.models import DagRun
from airflow.models.dag import DAG
from airflow.utils.context import Context

from rcplus_alloy_common.airflow.observability import (
    slack_alert_on_failure,
    slack_alert_on_retry,
    send_sla_slack_message,
    publish_dag_metrics_callback,
    publish_task_metrics_callback,
)


@pytest.fixture
def mock_airflow_variable():
    with patch("airflow.models.Variable.get") as mock_get:
        # Define the mocked return value
        mock_get.return_value = "mocked_value"

        yield mock_get


@pytest.fixture
def mock_slack_webhook_operator():
    with patch("airflow.providers.slack.operators.slack_webhook.SlackWebhookOperator.execute") as mock_execute:
        # Mock the execute method to avoid actual API requests
        mock_execute.return_value = None

        yield mock_execute


@pytest.fixture
def mock_task_instance():
    with patch("airflow.models.TaskInstance") as mock_task_instance:
        mock_task_instance.duration = 100
        yield mock_task_instance


@pytest.fixture
def mock_publish_metrics():
    with patch("rcplus_alloy_common.metrics.publish_metrics_sync") as mock_publish_metric:
        # Mock the execute method to avoid actual API requests
        mock_publish_metric.return_value = None

        yield mock_publish_metric


def test_slack_alert(
    mock_airflow_variable,  # pylint: disable=unused-argument
    mock_slack_webhook_operator,
    mock_task_instance
):
    # Create a dummy context
    context = Context(
        dag_id="anydag",
        dag=DAG(dag_id="test_dag", start_date=datetime(2020, 1, 1)),
        dag_run=DagRun(run_id="anyrun", dag_id="anydag", execution_date=datetime.now()),
        task_instance=mock_task_instance,
        execution_date=datetime.now(),
        logical_date=datetime.now(),
        data_interval_start=datetime.now(),
        try_number=1,
    )
    slack_alert_on_retry(context)
    slack_alert_on_failure(context)

    # Assert that the mocked method was called
    assert mock_slack_webhook_operator.call_count == 2


def test_my_task(
    mock_airflow_variable,  # pylint: disable=unused-argument
    mock_slack_webhook_operator,
    mock_task_instance
):
    # Create a dummy context
    context = Context(
        dag_id="anydag",
        dag=DAG(dag_id="test_dag", start_date=datetime(2020, 1, 1)),
        dag_run=DagRun(run_id="anyrun", dag_id="anydag", execution_date=datetime.now()),
        task_instance=mock_task_instance,
        execution_date=datetime.now(),
        logical_date=datetime.now(),
        data_interval_start=datetime.now(),
        try_number=1,
    )
    slack_alert_on_retry(context)

    # Assert that the mocked method was called
    mock_slack_webhook_operator.assert_called_once_with(context=context)


def test_slack_sla_alert(
    mock_airflow_variable,  # pylint: disable=unused-argument
    mock_slack_webhook_operator,
    mock_task_instance
):
    send_sla_slack_message("test", "test", "test")

    # Assert that the mocked method was called
    assert mock_slack_webhook_operator.call_count == 1


def test_publish_dag_metrics_callback(
    mock_publish_metrics,
):
    # observability module reload is required to use the patched `publish_metrics_sync` function
    import rcplus_alloy_common.airflow.observability
    reload(rcplus_alloy_common.airflow.observability)

    # Create a dummy context
    dag_run = DagRun(
        run_id="anyrun",
        dag_id="anydag",
        execution_date=datetime.now(),
        start_date=datetime.now() - timedelta(hours=1),
    )
    dag_run.end_date = datetime.now()
    context = Context(
        dag_id="anydag",
        dag=DAG(dag_id="test_dag", start_date=datetime(2020, 1, 1)),
        dag_run=dag_run,
        task_instance=mock_task_instance,
        execution_date=datetime.now(),
        logical_date=datetime.now(),
        data_interval_start=datetime.now(),
        try_number=1,
    )
    publish_dag_metrics_callback(context)

    # Assert that the mocked method was called
    assert mock_publish_metrics.call_count == 1


def test_publish_task_metrics_callback(
    mock_task_instance,
    mock_publish_metrics,
):
    # observability module reload is required to use the patched `publish_metrics_sync` function
    import rcplus_alloy_common.airflow.observability
    reload(rcplus_alloy_common.airflow.observability)

    # Create a dummy context
    context = Context(
        dag_id="anydag",
        dag=DAG(dag_id="test_dag", start_date=datetime(2020, 1, 1)),
        dag_run=DagRun(run_id="anyrun", dag_id="anydag", execution_date=datetime.now()),
        task_instance=mock_task_instance,
        execution_date=datetime.now(),
        logical_date=datetime.now(),
        data_interval_start=datetime.now(),
        try_number=1,
    )
    publish_task_metrics_callback(context)

    # Assert that the mocked method was called
    assert mock_publish_metrics.call_count == 1
