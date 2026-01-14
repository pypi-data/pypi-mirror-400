import time
import os
from datetime import datetime
from contextlib import contextmanager
from unittest.mock import patch

import pytest
from airflow.datasets import Dataset
from rcplus_alloy_common.airflow.utils import AlloyProject, set_default_callbacks, AlloyTagServiceName
from rcplus_alloy_common.airflow.observability import (
    slack_alert_on_retry,
    slack_alert_on_failure,
    publish_task_metrics_callback,
)
from rcplus_alloy_common.airflow.dag import AlloyDag
from rcplus_alloy_common.airflow.operators import AlloyEmptyOperator


@contextmanager
def makedirs(name):
    os.makedirs(name, exist_ok=True)
    yield


def test_project_config():
    project = AlloyProject()
    assert "env" in project
    assert project["env"] == "test"
    assert "git_repo_name" in project
    assert project["git_repo_name"] == "my-test-repo"
    assert "project_id" in project
    assert project["project_id"] == "alloy"
    assert "project_version" in project
    assert project["project_version"] == "0.0.0"
    assert "software_component" in project
    assert project["software_component"] == "my-software-component"
    assert project.tenant_configs[0].name == "tenant_1"


def test_project_config_without_tenant_file(caplog):
    with patch("rcplus_alloy_common.airflow.utils.AlloyProject._load_project_config", return_value=[]):
        project = AlloyProject(4)
        with caplog.at_level("WARNING"):
            project._load_project_config()
            assert "tenant_configs.json not found" in caplog.text
            assert project.tenant_configs == []


def test_project_config_with_tenant_file_with_traverse_fail(caplog):
    with (
        makedirs("tests/f1/f2/f3/f4/f5/f6"),
        patch("rcplus_alloy_common.airflow.utils.AlloyProject._load_project_config", return_value=[]),
        patch("rcplus_alloy_common.airflow.utils.AlloyProject._get_fileloc", return_value="tests/f1/f2/f3/f4/f5/f6"),
    ):
        project = AlloyProject()
        assert project.tenant_configs == []


def test_project_config_with_tenant_file_with_traverse_succeed(caplog):
    with (
        makedirs("tests/f1/f2/f3/f4/f5"),
        patch("rcplus_alloy_common.airflow.utils.AlloyProject._load_project_config", return_value=[]),
        patch("rcplus_alloy_common.airflow.utils.AlloyProject._get_fileloc", return_value="tests/f1/f2/f3/f4/f5"),
    ):
        project = AlloyProject()
        assert project.tenant_configs[0].name == "tenant_1"


def test_project_templated_var():
    project = AlloyProject()
    assert project.get_templated_var("my_var") == "{{ var.value.get('my-software-component/my_var') }}"
    assert project.get_templated_var("my_var", "smt/else") == "{{ var.value.get('smt/else/my_var') }}"


def test_project_depth_property():
    project = AlloyProject()
    project.config = None
    try:
        project.depth = 3
    except FileNotFoundError:
        pass
    assert project.config is None

    project.depth = 2
    assert project.config == {
        "env": "test",
        "git_repo_name": "my-test-repo",
        "project_id": "alloy",
        "project_version": "0.0.0",
        "software_component": "my-software-component",
    }


def test_set_default_callbacks_wo_defaults():
    default_args = set_default_callbacks({})
    assert isinstance(default_args, dict)
    assert "on_success_callback" in default_args
    assert "on_failure_callback" in default_args
    assert "on_retry_callback" in default_args

    assert [publish_task_metrics_callback] == default_args["on_success_callback"]
    assert [slack_alert_on_failure, publish_task_metrics_callback] == default_args["on_failure_callback"]
    assert [slack_alert_on_retry] == default_args["on_retry_callback"]


def test_set_default_callbacks_with_defaults():
    def y():
        time.sleep(10)

    def z():
        return None

    default_args = set_default_callbacks(
        {
            "on_failure_callback": [y, z],
            "on_retry_callback": z,
            "tags": ["test"]
        }
    )
    assert isinstance(default_args, dict)
    assert "on_success_callback" in default_args
    assert "on_failure_callback" in default_args
    assert "on_retry_callback" in default_args

    assert slack_alert_on_failure in default_args["on_failure_callback"]
    assert slack_alert_on_retry in default_args["on_retry_callback"]  # pylint: disable=unsupported-membership-test
    assert len(default_args["on_success_callback"]) == 1
    assert len(default_args["on_failure_callback"]) == 4
    assert len(default_args["on_retry_callback"]) == 2

    # no default callback was removed
    assert y in default_args["on_failure_callback"]
    assert z in default_args["on_failure_callback"]
    assert z in default_args["on_retry_callback"]  # pylint: disable=unsupported-membership-test
    # no default was removed
    assert "tags" in default_args
    assert "test" in default_args["tags"]


def test_set_default_callbacks_no_replacement():
    default_args = set_default_callbacks(
        {
            "on_failure_callback": slack_alert_on_failure,
            "on_retry_callback": slack_alert_on_retry,
        }
    )
    assert isinstance(default_args, dict)
    assert "on_success_callback" in default_args
    assert "on_failure_callback" in default_args
    assert "on_retry_callback" in default_args

    assert [publish_task_metrics_callback] == default_args["on_success_callback"]
    assert [slack_alert_on_failure, publish_task_metrics_callback] == default_args["on_failure_callback"]
    assert [slack_alert_on_retry] == default_args["on_retry_callback"]

    default_args = set_default_callbacks(
        {
            "on_success_callback": [publish_task_metrics_callback],
            "on_failure_callback": [slack_alert_on_failure],
            "on_retry_callback": [slack_alert_on_retry],
        }
    )
    assert isinstance(default_args, dict)
    assert "on_success_callback" in default_args
    assert "on_failure_callback" in default_args
    assert "on_retry_callback" in default_args

    assert publish_task_metrics_callback in default_args["on_success_callback"]
    assert slack_alert_on_failure in default_args["on_failure_callback"]
    assert slack_alert_on_retry in default_args["on_retry_callback"]
    assert len(default_args["on_success_callback"]) == 1
    assert len(default_args["on_failure_callback"]) == 2
    assert len(default_args["on_retry_callback"]) == 1


def test_get_dataset():
    project = AlloyProject()
    dataset = project.get_dataset("task_id", "dag_name", software_component="software_component")
    assert dataset == Dataset("alloy-software_component-dag_name-task_id")

    with AlloyDag(
        dag_id="test_dag_default",
        start_date=datetime(2020, 1, 1),
        schedule="@daily",
    ):
        operator = AlloyEmptyOperator(task_id="task_id")
        op_dataset = operator.outlets[0]
        assert op_dataset == project.get_dataset(task_id="task_id", dag_name="test_dag_default")


def test_get_dataset_with_tenant():
    project = AlloyProject()
    dataset = project.get_dataset("task_id", "dag_name", "tenant", "software_component")
    assert dataset == Dataset("alloy-software_component-tenant-dag_name-task_id")

    with AlloyDag(
        dag_id="test_dag_default",
        start_date=datetime(2020, 1, 1),
        schedule="@daily",
        tenant="tenant"
    ):
        operator = AlloyEmptyOperator(task_id="task_id")
        op_dataset = operator.outlets[0]
        assert op_dataset == project.get_dataset(task_id="task_id", dag_name="test_dag_default", tenant="tenant")


def test_alloy_tag():
    with AlloyDag(
        dag_id="my-dag-id",
        start_date=datetime(2020, 1, 1),
        schedule="@daily",
    ):
        operator = AlloyEmptyOperator(task_id="alloy-my-software-component-my-task-id")
        operator.service_name = AlloyTagServiceName.UNKNOWN
        assert operator.get_alloy_tag(operator.task_id) == (
            "alloy.unknown.my-software-component.my-dag-id-my-task-id"
        )


def test_alloy_tag_with_tenant():
    with AlloyDag(
        dag_id="my-dag-id",
        tenant="my-tenant",
        start_date=datetime(2020, 1, 1),
        schedule="@daily",
    ):
        operator = AlloyEmptyOperator(task_id="my-task-id")
        operator.service_name = AlloyTagServiceName.LAMBDA
        assert operator.get_alloy_tag("alloy-my-software-component-something") == (
            "alloy.lambda.my-software-component.my-tenant-my-dag-id-something"
        )


def test_make_dag_id():
    project = AlloyProject()
    assert project.make_dag_id("downsample") == "alloy-my-software-component-downsample"
    assert project.make_dag_id("downsample", tenant="my-tenant") == "alloy-my-software-component-my-tenant-downsample"

    with pytest.raises(ValueError) as exc_info:
        project.make_dag_id("downsample", tenant=1)

    assert "Malformed tenant parameter. Expected `str` received `1`" == str(exc_info.value)
