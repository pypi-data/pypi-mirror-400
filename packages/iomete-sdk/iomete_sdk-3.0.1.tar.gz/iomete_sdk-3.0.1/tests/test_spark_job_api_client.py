import time
import uuid

import pytest as pytest

from iomete_sdk.spark import SparkJobApiClient
from iomete_sdk.api_utils import ClientError
from tests import TEST_TOKEN, TEST_HOST, TEST_DOMAIN

SPARK_VERSION = "3.5.3"


def random_job_name():
    return f"test-job-{uuid.uuid4().hex}"


@pytest.fixture
def create_payload() -> dict:
    return {
        "name": random_job_name(),
        "namespace": "iomete-system",
        "jobUser": "admin",
        "jobType": "MANUAL",
        "template": {
            "applicationType": "python",
            "image": f"iomete/spark-py:{SPARK_VERSION}-v1",
            "mainApplicationFile": "https://raw.githubusercontent.com/iomete/query-scheduler-job/main/job.py",
            "configMaps": [{
                "key": "application.conf",
                "content": "# Queries to be run sequentially\n[\n  # let's create an example SELECT\n  \"\"\"\n  SELECT 1\n  \"\"\"\n]",
                "mountPath": "/etc/configs"
            }],
            "deps": {
                "pyFiles": ["https://github.com/iomete/query-scheduler-job/raw/main/infra/dependencies.zip"]
            },
            "instanceConfig": {
                "singleNodeDeployment": False, "driverType": "driver-x-small",
                "executorType": "exec-x-small", "executorCount": 1
            },
            "restartPolicy": {"type": "Never"},
            "maxExecutionDurationSeconds": "3600"
            # "volumeId": "eb64f935-9290-48f3-a34f-6d33f34dadf9",
        }
    }


@pytest.fixture
def job_client():
    return SparkJobApiClient(
        host=TEST_HOST,
        api_key=TEST_TOKEN,
        domain=TEST_DOMAIN
    )


def test_create_job_without_name_raise_400(job_client, create_payload):
    payload_without_name = {}

    with pytest.raises(ClientError) as err:
        response = job_client.create_job(payload=payload_without_name)

    assert err.value.status == 400


def test_create_job_successful(job_client, create_payload):
    response = job_client.create_job(payload=create_payload)

    assert response["name"] == create_payload["name"]
    assert response["id"] is not None

    # clean up
    job_client.delete_job_by_id(job_id=response["id"])


def test_update_job(job_client, create_payload):
    # create job
    job_create_response = job_client.create_job(payload=create_payload)

    cron_schedule = "0 0 */1 * *"

    # update job
    update_payload = job_create_response.copy()
    update_payload["jobType"] = "SCHEDULED"
    update_payload["schedule"] = cron_schedule
    job_update_response = job_client.update_job(job_id=job_create_response["id"], payload=update_payload)

    assert job_update_response["schedule"] == cron_schedule
    assert job_update_response["jobType"] == "SCHEDULED"
    assert job_update_response["name"] == job_create_response["name"]
    assert job_update_response["id"] == job_create_response["id"]

    # clean up
    job_client.delete_job_by_id(job_id=job_update_response["id"])


def test_get_jobs(job_client):
    response = job_client.get_jobs()

    assert len(response) > 0

    job = response[0]
    assert job["id"] is not None


def test_get_job_by_id(job_client, create_payload):
    # create job
    job = job_client.create_job(payload=create_payload)

    # check job is created
    response = job_client.get_job_by_id(job_id=job["id"])

    assert response["item"] is not None
    assert response["permissions"] is not None

    job = response["item"]
    assert job["name"] == create_payload["name"]
    assert job["id"] is not None

    # clean up
    job_client.delete_job_by_id(job_id=job["id"])


def test_get_job_run_by_id(job_client, create_payload):
    job = job_client.create_job(payload=create_payload)
    job_run = job_client.submit_job_run(job_id=job["id"], payload={})

    job_run_info = job_client.get_job_run_by_id(job_id=job["id"], run_id=job_run["id"])

    assert job_run_info["jobId"] == job["id"]
    assert job_run_info["id"] == job_run["id"]
    assert job_run_info["driverErrorMessage"] == ''
    assert job_run_info["executionAttempts"] == 1

    job_client.cancel_job_run(job_id=job["id"], run_id=job_run["id"])
    job_client.delete_job_by_id(job_id=job["id"])


def test_get_job_run_logs(job_client, create_payload):
    job = job_client.create_job(payload=create_payload)
    job_run = job_client.submit_job_run(job_id=job["id"], payload={})

    job_run_logs = job_client.get_job_run_logs(job_id=job["id"], run_id=job_run["id"])

    assert job_run_logs is not None
    assert len(job_run_logs) > 0
    assert job_run_logs[0]['date'] is not None
    assert job_run_logs[0]['logLine'] is not None

    job_client.cancel_job_run(job_id=job["id"], run_id=job_run["id"])
    job_client.delete_job_by_id(job_id=job["id"])


def test_get_job_run_metrics(job_client, create_payload):
    job = job_client.create_job(payload=create_payload)
    job_run = job_client.submit_job_run(job_id=job["id"], payload={})

    time.sleep(10)

    job_run_metrics = job_client.get_job_run_metrics(job_id=job["id"], run_id=job_run["id"])

    assert job_run_metrics is not None
    assert job_run_metrics["runId"] == job_run["id"]
    assert job_run_metrics["driver"] is not None
    assert job_run_metrics["executors"] is not None

    job_client.cancel_job_run(job_id=job["id"], run_id=job_run["id"])
    job_client.delete_job_by_id(job_id=job["id"])


def test_delete_job_by_id(job_client, create_payload):
    # create job
    job = job_client.create_job(payload=create_payload)

    # check job is created
    response = job_client.get_job_by_id(job_id=job["id"])
    assert response["item"]["name"] == create_payload["name"]

    # delete job
    job_client.delete_job_by_id(job_id=job["id"])

    # check job is deleted
    with pytest.raises(ClientError) as err:
        job_client.get_job_by_id(job_id=job["id"])
    assert err.value.status == 404
    assert err.value.content["errorCode"] == "NOT_FOUND"


def test_get_job_runs(job_client, create_payload):
    # create job
    job = job_client.create_job(payload=create_payload)

    # check job is created
    response = job_client.get_job_runs(job_id=job["id"])

    # should be empty run list
    assert response == []

    # clean up
    job_client.delete_job_by_id(job_id=job["id"])


def test_submit_job_run(job_client, create_payload):
    # create job
    job = job_client.create_job(payload=create_payload)

    # submit job run
    response = job_client.submit_job_run(job_id=job["id"], payload={})

    run_id = response["id"]

    assert run_id is not None

    # sleep 5 seconds before cleaning up
    time.sleep(5)

    # clean up
    job_client.cancel_job_run(job_id=job["id"], run_id=run_id)
    job_client.delete_job_by_id(job_id=job["id"])
