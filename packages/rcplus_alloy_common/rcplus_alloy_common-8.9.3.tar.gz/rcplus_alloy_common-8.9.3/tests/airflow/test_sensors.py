from datetime import datetime

import pytest
import boto3
from moto import mock_s3, mock_ec2, mock_autoscaling

from airflow.models.dag import DAG

from rcplus_alloy_common.airflow.sensors import (
    AlloySqsSensor,
    AlloyAutoScalingGroupSensor
)
from rcplus_alloy_common.airflow.observability import slack_alert_on_retry, slack_alert_on_failure


@pytest.fixture(autouse=True)
def moto_s3():
    mock = mock_s3()
    mock.start()
    # create bucket
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket="lock-bucket")
    s3.put_object(
        Bucket="lock-bucket",
        Key=".lock",
        Body=b"alloy-my-software-component-test_dag",
    )
    yield
    mock.stop()


def test_sqs_sensor_callbacks():
    with DAG(dag_id="test_dag", start_date=datetime(2020, 1, 1)):
        sqs_sensor = AlloySqsSensor(
            task_id="test_sqs_sensor_callbacks",
            sqs_queue="https://sqs.us-east-1.amazonaws.com/123456789012/test_queue",
        )

        assert slack_alert_on_failure in sqs_sensor.on_failure_callback
        assert slack_alert_on_retry in sqs_sensor.on_retry_callback


@mock_ec2
@mock_autoscaling
def test_autoscaling_sensor_callbacks():
    with DAG(dag_id="test_dag", start_date=datetime(2020, 1, 1)):
        autoscaling_sensor = AlloyAutoScalingGroupSensor(
            task_id="test_autoscaling_sensor_callbacks",
            autoscaling_group_name="test_group",
        )

        assert autoscaling_sensor.poke({}) is False

        # Start Autoscaling group
        region_name = "us-east-1"
        ec2 = boto3.resource("ec2", region_name=region_name)
        vpc = ec2.create_vpc(CidrBlock="10.11.0.0/16")
        subnet1 = ec2.create_subnet(
            VpcId=vpc.id, CidrBlock="10.11.1.0/24", AvailabilityZone=f"{region_name}a"
        )

        as_client = boto3.client("autoscaling", region_name="us-east-1")
        as_client.create_launch_configuration(
            LaunchConfigurationName="TestLC",
            ImageId="ami-1234567890",
            InstanceType="t2.medium",
        )
        as_client.create_auto_scaling_group(
            AutoScalingGroupName=autoscaling_sensor.autoscaling_group_name,
            MinSize=1,
            MaxSize=1,
            LaunchConfigurationName="TestLC",
            VPCZoneIdentifier=subnet1.id,
        )
        assert autoscaling_sensor.poke({}) is True


@mock_ec2
@mock_autoscaling
def test_autoscaling_sensor_with_capacity_callbacks():
    with DAG(dag_id="test_dag", start_date=datetime(2020, 1, 1)):
        autoscaling_capacity_sensor_2 = AlloyAutoScalingGroupSensor(
            task_id="test_autoscaling_sensor_callbacks",
            autoscaling_group_name="test_group",
            expected_capacity=2,
        )

        autoscaling_capacity_sensor_0 = AlloyAutoScalingGroupSensor(
            task_id="test_autoscaling_sensor_fail_callbacks",
            autoscaling_group_name="test_group",
            expected_capacity=0,
        )

        assert autoscaling_capacity_sensor_2.poke({}) is False
        assert autoscaling_capacity_sensor_0.poke({}) is False

        # Start Autoscaling group
        region_name = "us-east-1"
        ec2 = boto3.resource("ec2", region_name=region_name)
        vpc = ec2.create_vpc(CidrBlock="10.11.0.0/16")
        subnet1 = ec2.create_subnet(
            VpcId=vpc.id, CidrBlock="10.11.1.0/24", AvailabilityZone=f"{region_name}a"
        )

        as_client = boto3.client("autoscaling", region_name="us-east-1")
        as_client.create_launch_configuration(
            LaunchConfigurationName="TestLC",
            ImageId="ami-1234567890",
            InstanceType="t2.medium",
        )
        as_client.create_auto_scaling_group(
            AutoScalingGroupName=autoscaling_capacity_sensor_2.autoscaling_group_name,
            MinSize=0,
            MaxSize=3,
            DesiredCapacity=2,
            LaunchConfigurationName="TestLC",
            VPCZoneIdentifier=subnet1.id,
        )
        assert autoscaling_capacity_sensor_2.poke({}) is True
        assert autoscaling_capacity_sensor_0.poke({}) is False


@mock_ec2
@mock_autoscaling
def test_autoscaling_sensor_with_capacity_0_callbacks():
    with DAG(dag_id="test_dag", start_date=datetime(2020, 1, 1)):
        autoscaling_capacity_sensor_2 = AlloyAutoScalingGroupSensor(
            task_id="test_autoscaling_sensor_callbacks",
            autoscaling_group_name="test_group",
            expected_capacity=2,
        )

        autoscaling_capacity_sensor_0 = AlloyAutoScalingGroupSensor(
            task_id="test_autoscaling_sensor_zero_callbacks",
            autoscaling_group_name="test_group",
            expected_capacity=0,
        )

        assert autoscaling_capacity_sensor_2.poke({}) is False
        assert autoscaling_capacity_sensor_0.poke({}) is False

        # Start Autoscaling group
        region_name = "us-east-1"
        ec2 = boto3.resource("ec2", region_name=region_name)
        vpc = ec2.create_vpc(CidrBlock="10.11.0.0/16")
        subnet1 = ec2.create_subnet(
            VpcId=vpc.id, CidrBlock="10.11.1.0/24", AvailabilityZone=f"{region_name}a"
        )

        as_client = boto3.client("autoscaling", region_name="us-east-1")
        as_client.create_launch_configuration(
            LaunchConfigurationName="TestLC",
            ImageId="ami-1234567890",
            InstanceType="t2.medium",
        )
        as_client.create_auto_scaling_group(
            AutoScalingGroupName=autoscaling_capacity_sensor_2.autoscaling_group_name,
            MinSize=0,
            MaxSize=3,
            DesiredCapacity=0,
            LaunchConfigurationName="TestLC",
            VPCZoneIdentifier=subnet1.id,
        )
        assert autoscaling_capacity_sensor_2.poke({}) is False
        assert autoscaling_capacity_sensor_0.poke({}) is True
