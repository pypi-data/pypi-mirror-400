import logging
from dataclasses import dataclass

from iomete_sdk.api_utils import APIUtils


@dataclass
class SparkJobApiClient:
    logger = logging.getLogger('SparkJobApiClient')

    host: str
    api_key: str
    domain: str
    verify: bool = True

    spark_job_endpoint: str = None
    api_utils: APIUtils = None

    def __post_init__(self):
        self.api_utils = APIUtils(api_key=self.api_key, verify=self.verify)

        self.logger.debug(f"Host: {self.host}")
        self.spark_job_endpoint = f"{self.host}/api/v1/domains/{self.domain}/spark/jobs"

    def create_job(self, payload: dict):
        return self.api_utils.call(method="POST", url=self.spark_job_endpoint, payload=payload)

    def update_job(self, job_id: str, payload: dict):
        return self.api_utils.call(method="PUT", url=f"{self.spark_job_endpoint}/{job_id}", payload=payload)

    def get_jobs(self):
        return self.api_utils.call(method="GET", url=self.spark_job_endpoint)

    def get_job_by_id(self, job_id: str):
        return self.api_utils.call(method="GET", url=f"{self.spark_job_endpoint}/{job_id}")

    def delete_job_by_id(self, job_id: str):
        return self.api_utils.call(method="DELETE", url=f"{self.spark_job_endpoint}/{job_id}")

    def get_job_runs(self, job_id: str):
        return self.api_utils.call(method="GET", url=f"{self.spark_job_endpoint}/{job_id}/runs")

    def submit_job_run(self, job_id: str, payload: dict):
        return self.api_utils.call(method="POST", url=f"{self.spark_job_endpoint}/{job_id}/runs", payload=payload)

    def cancel_job_run(self, job_id: str, run_id: str):
        return self.api_utils.call(method="DELETE", url=f"{self.spark_job_endpoint}/{job_id}/runs/{run_id}")

    def get_job_run_by_id(self, job_id: str, run_id: str):
        return self.api_utils.call(method="GET", url=f"{self.spark_job_endpoint}/{job_id}/runs/{run_id}")

    def get_job_run_logs(self, job_id: str, run_id: str, time_range: str = "5m"):
        return self.api_utils.call(method="GET",
                                   url=f"{self.spark_job_endpoint}/{job_id}/runs/{run_id}/logs?range={time_range}")

    def get_job_run_metrics(self, job_id: str, run_id: str):
        return self.api_utils.call(method="GET", url=f"{self.spark_job_endpoint}/{job_id}/runs/{run_id}/metrics")
