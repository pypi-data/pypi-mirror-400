import logging
from datetime import datetime
from unittest.mock import patch

import pytest

from rcplus_alloy_common.version import head_ref
from rcplus_alloy_common.airflow.dag import AlloyDag
from rcplus_alloy_common.airflow import DagSlaConfig
from rcplus_alloy_common.airflow.observability import publish_dag_metrics_callback


@pytest.fixture
def mock_dag_run():
    with patch("airflow.models.dag.DAG.run") as mock_run:
        mock_run.return_value = None
        yield mock_run


def test_dag_default():
    dag = AlloyDag(
        dag_id="test_dag_default",
        start_date=datetime(2020, 1, 1),
        schedule="@daily",
        tags=["test"],
    )

    assert dag.dag_id == "alloy-my-software-component-test_dag_default"
    assert dag.tags == ["test", "my-test-repo", "0.0.0"]


def test_dag_default_2():
    dag = AlloyDag(
        dag_id="test_dag_default",
        start_date=datetime(2020, 1, 1),
        schedule="@daily",
    )

    assert dag.dag_id == "alloy-my-software-component-test_dag_default"
    assert dag.tags == ["my-test-repo", "0.0.0"]


def test_dag_default_3():
    dag = AlloyDag(
        dag_id="test_dag_default",
        start_date=datetime(2020, 1, 1),
        schedule="@daily",
    )

    assert dag.dag_id == "alloy-my-software-component-test_dag_default"
    assert dag.tags == ["my-test-repo", "0.0.0"]


def test_dag_default_4():
    dag = AlloyDag(
        dag_id="test_dag_default",
        start_date=datetime(2020, 1, 1),
        schedule="@daily",
        tenant="test_tenant",
    )

    assert dag.dag_id == "alloy-my-software-component-test_tenant-test_dag_default"
    assert dag.tags == ["test_tenant", "my-test-repo", "0.0.0"]


def test_dag_default_5():
    dag = AlloyDag(
        dag_id="test_dag_default",
        start_date=datetime(2020, 1, 1),
        schedule="@daily",
        tags=["test"],
        tenant="test_tenant",
    )

    assert dag.dag_id == "alloy-my-software-component-test_tenant-test_dag_default"
    assert dag.tags == ["test", "test_tenant", "my-test-repo", "0.0.0"]


def test_dag_default_6():
    with pytest.raises(ValueError) as exc_info:
        AlloyDag(
            dag_id="test_dag_default",
            start_date=datetime(2020, 1, 1),
            schedule="@daily",
            tags=["test"],
            tenant=["test_tenant"],
        )

    assert str(exc_info.value) == "Malformed tenant parameter. Expected `str` received `['test_tenant']`"


def test_dag_default_7():
    dag = AlloyDag(
        dag_id="test_dag_default",
        start_date=datetime(2020, 1, 1),
        schedule="@daily",
        tags=["test", "test_tenant"],
        tenant="test_tenant",
    )

    assert dag.dag_id == "alloy-my-software-component-test_tenant-test_dag_default"
    assert dag.tags == ["test", "test_tenant", "my-test-repo", "0.0.0"]


def test_dag_with_none_1():
    dag = AlloyDag(
        dag_id="test_dag_default",
        start_date=datetime(2020, 1, 1),
        schedule="@daily",
        tags=None,
    )

    assert dag.dag_id == "alloy-my-software-component-test_dag_default"
    assert dag.tags == ["my-test-repo", "0.0.0"]


def test_dag_with_none_2():
    dag = AlloyDag(
        dag_id="test_dag_default",
        start_date=datetime(2020, 1, 1),
        schedule="@daily",
        tags=None,
        tenant=None,
    )

    assert dag.dag_id == "alloy-my-software-component-test_dag_default"
    assert dag.tags == ["my-test-repo", "0.0.0"]


def test_dag_with_str_tag_1(caplog):
    dag = AlloyDag(
        dag_id="test_dag_default",
        start_date=datetime(2020, 1, 1),
        schedule="@daily",
        tags="test",
        tenant=None,
    )

    assert dag.dag_id == "alloy-my-software-component-test_dag_default"
    assert dag.tags == ["my-test-repo", "0.0.0"]
    assert [record for record in caplog.records if record.levelno == logging.WARNING]


def test_dag_version_log(caplog, mock_dag_run):  # pylint: disable=unused-argument
    dag = AlloyDag(
        dag_id="test_dag_version_log",
        start_date=datetime(2020, 1, 1),
        schedule="@daily",
    )

    dag.run()

    assert f"Running dag `{dag.dag_id}` with version `rcplus_alloy_common@{head_ref}`" in caplog.text


def test_dag_correct_sla():
    dag = AlloyDag(
        dag_id="test_dag_version_log",
        start_date=datetime(2020, 1, 1),
        schedule="@daily",
        sla_config=DagSlaConfig(sla_period="12 hours")
    )

    assert dag.description == "This DAG SLA period is 12 hours"
    assert dag.doc_md == '{"sla_period": 43200}'


def test_dag_incorrect_sla():
    with pytest.raises(ValueError) as exc_info:
        AlloyDag(
            dag_id="test_dag_version_log",
            start_date=datetime(2020, 1, 1),
            schedule="@daily",
            sla_config=DagSlaConfig(sla_period="12")
        )

    assert str(exc_info.value) == "Incorrect SLA period definition '12'"


def test_dag_sla_config_parser():
    assert DagSlaConfig(sla_period="12s").to_json() == '{"sla_period": 12}'
    assert DagSlaConfig(sla_period="12 s").to_json() == '{"sla_period": 12}'
    assert DagSlaConfig(sla_period="12 secs").to_json() == '{"sla_period": 12}'
    assert DagSlaConfig(sla_period="12 seconds").to_json() == '{"sla_period": 12}'

    assert DagSlaConfig(sla_period="1m").to_json() == '{"sla_period": 60}'
    assert DagSlaConfig(sla_period="1 m").to_json() == '{"sla_period": 60}'
    assert DagSlaConfig(sla_period="2 minutes").to_json() == '{"sla_period": 120}'

    assert DagSlaConfig(sla_period="1h").to_json() == '{"sla_period": 3600}'
    assert DagSlaConfig(sla_period="1 h").to_json() == '{"sla_period": 3600}'
    assert DagSlaConfig(sla_period="1 hour").to_json() == '{"sla_period": 3600}'
    assert DagSlaConfig(sla_period="2 hours").to_json() == '{"sla_period": 7200}'

    assert DagSlaConfig(sla_period="1d").to_json() == '{"sla_period": 86400}'
    assert DagSlaConfig(sla_period="1 d").to_json() == '{"sla_period": 86400}'
    assert DagSlaConfig(sla_period="1 day").to_json() == '{"sla_period": 86400}'
    assert DagSlaConfig(sla_period="2 days").to_json() == '{"sla_period": 172800}'

    with pytest.raises(ValueError) as exc_info:
        DagSlaConfig(sla_period="SLA").to_json()

    assert str(exc_info.value) == "Incorrect SLA period definition 'SLA'"

    with pytest.raises(ValueError) as exc_info:
        DagSlaConfig(sla_period="1").to_json()

    assert str(exc_info.value) == "Incorrect SLA period definition '1'"


def test_dag_callbacks():
    dag = AlloyDag(
        dag_id="test_dag",
        start_date=datetime(2020, 1, 1),
        schedule="@daily",
    )

    assert len(dag.on_success_callback) > 0
    assert len(dag.on_failure_callback) > 0
    assert publish_dag_metrics_callback in dag.on_success_callback
    assert publish_dag_metrics_callback in dag.on_failure_callback
