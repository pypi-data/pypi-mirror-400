# XClient

[XClient](https://xclient.cloud) Python SDK for XCloud Service API. Manage and execute jobs with confidence.

## Run your first XClient Job

### 1. Install [xclient-python-sdk](https://pypi.org/project/xclient-python-sdk/)

```bash
pip install xclient-python-sdk
```

### 2. Setup your XClient API key

1. Sign up to [XClient](https://xcloud-service.com)
2. Manage your [API key](https://xcloud-service.com/home/api-keys)
3. Create API key, and set environment variable with your API key

```
export XCLIENT_API_KEY=xck_******
export XCLIENT_DOMAIN=localhost:8090  # optional, default is localhost:8090
```

### 3. Execute code with XClient Job

```python
from xclient import Job

job = Job(api_key="xck_******")

# Submit a job
result = job.submit(
    name="my-training-job",
    script="#!/bin/bash\necho 'Hello World'",
    cluster_id=1,
    resources={"cpu": 4, "gpu": 1, "memory": "8GB"}
)

# Get job details
job_info = job.get(job_id=result.job_id, cluster_id=1)

# List jobs
from xclient.api.client.models.job_status import JobStatus
running_jobs = job.list(status=JobStatus.RUNNING, page=1, page_size=20)

# Cancel a job
job.cancel(job_id=result.job_id)
```

### 4. Documents

Visit [XClient Documents](https://xclient.cloud/docs)
