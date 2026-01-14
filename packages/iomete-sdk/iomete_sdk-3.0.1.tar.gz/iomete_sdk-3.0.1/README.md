# IOMETE SDK

This is the IOMETE SDK for Python. 
It provides convenient access to the IOMETE API from applications written in the Python language.

## Installation

Install the package with:

```bash
pip install iomete-sdk
```

## Usage - Spark Job API

### Import and initialize the client
```python
from iomete_sdk.spark import SparkJobApiClient

HOST = "<DATAPLANE_HOST>" # https://dataplane-endpoint.example.com
API_KEY = "<IOMETE_API_KEY>"
DOMAIN = "<IOMETE_DOMAIN>"

job_client = SparkJobApiClient(
    host=HOST,
    api_key=API_KEY,
    domain=DOMAIN
)
```

### Create a new job
```python
response = job_client.create_job(payload={
        "name": "job-name",
        "namespace": "k8s-namespace",
        "jobUser": "job-user",
        "jobType": "MANUAL/SCHEDULED/STREAMING",
        "template": {
            "applicationType": "python",
            "image": f"iomete/spark-py:3.5.3-v1",
            "mainApplicationFile": "path/to/job.py",
            "configMaps": [{
                "key": "application.conf",
                "content": "[SELECT 1]",
                "mountPath": "/etc/configs"
            }],
            "deps": {
                "pyFiles": ["path/to/dependencies.zip"]
            },
            "instanceConfig": {
                "singleNodeDeployment": False, "driverType": "driver-x-small",
                "executorType": "exec-x-small", "executorCount": 1
            },
            "restartPolicy": {"type": "Never"},
            "maxExecutionDurationSeconds": "max-execution-duration",
            "volumeId": "volume-id",
        }
    })

job_id = response["id"]
```

### Get jobs
```python
response = job_client.get_jobs()
```

### Get job
```python
response = job_client.get_job(job_id=job_id)
```

### Update job
```python
response = job_client.update_job(job_id=job_id, payload=updated_payload)
```

### Delete job
```python
response = job_client.delete_job(job_id=job_id)
```


### Submit job run
```python
response = job_client.submit_job_run(job_id=job_id, payload={})
```

### Cancel job run
```python
response = job_client.cancel_job_run(job_id=job_id, run_id=run_id)
```

### Get Job Runs
```python
response = job_client.get_job_runs(job_id=job_id)
```

### Get Job Run
```python
response = job_client.get_job_run(job_id=job_id, run_id=run_id)
```

### Get Job Run Logs
```python
response = job_client.get_job_run_logs(job_id=job_id, run_id=run_id, time_range="5m")
```
**Supported Time Range:** 5m, 15m, 30m, 1h, 3h, 6h, 12h, 24h, 2d, 7d, 14d, 30d 

### Get Job Run Metrics
```python
response = job_client.get_job_run_metrics(job_id=job_id, run_id=run_id)
```

### Publishing to PyPI

**1. Get PyPI API Token**

Before publishing, you need a PyPI API token:

1. Go to https://pypi.org/ and log in. Username/Password and OTP can be found in 1Password
2. Navigate to Account Settings → API tokens
3. Click "Add API token"
4. Name it (e.g., "iomete-sdk-release")
5. Scope: Select "Project: iomete-sdk" (or "Entire account" for first release)
6. Copy the token (starts with `pypi-...`) - you won't see it again!

**2. Configure credentials (optional)**

Save token to avoid typing it each time:

```bash
# Create/edit ~/.pypirc
cat > ~/.pypirc << EOF
[pypi]
username = __token__
password = pypi-YOUR_TOKEN_HERE
EOF

chmod 600 ~/.pypirc
```

**3. Build and publish**

```bash
# Clean, build, and check the package
make check

# Upload to PyPI (will prompt for token if not in ~/.pypirc)
make release
```

When prompted:
- Username: `__token__`
- Password: `pypi-YOUR_TOKEN_HERE`

**4. Verify publication**

Check the new version at https://pypi.org/project/iomete-sdk/

### Release Checklist

- [ ] Update version in `setup.py`
- [ ] Update dependencies if needed
- [ ] Run tests: `pytest tests/ -v`
- [ ] Update CHANGELOG (TODO)
- [ ] Commit changes: `git commit -am "Bump version to X.Y.Z"`
- [ ] Tag release: `git tag vX.Y.Z`
- [ ] Push: `git push && git push --tags`
- [ ] Build and publish: `make release`

