"""
High-level Job SDK interface for XClient.

This module provides a convenient interface for managing jobs through the XClient API.
"""

import json
from http import HTTPStatus
from typing import Optional
from ..api.client.api.jobs import (
    submit_job,
    get_job,
    list_jobs,
    cancel_job,
)
from ..api.client.models.job import Job as JobModel
from ..api.client.models.job_submit_request import JobSubmitRequest
from ..api.client.models.job_submit_response import JobSubmitResponse
from ..api.client.models.job_list_response import JobListResponse
from ..api.client.models.job_status import JobStatus
from ..api.client.models.error_response import ErrorResponse
from ..api.client.types import Response
from ..connection_config import ConnectionConfig
from ..exceptions import (
    NotFoundException,
    APIException,
)
from .client import JobClient, handle_api_exception


class Job:
    """
    High-level interface for managing jobs.
    
    Example:
        ```python
        from xclient import Job, ConnectionConfig
        
        config = ConnectionConfig(api_key="your_api_key")
        job = Job(config=config)
        
        # Submit a job
        result = job.submit(
            name="my-job",
            script="#!/bin/bash\\necho 'Hello World'",
            cluster_id=1
        )
        
        # Get job details
        job_info = job.get(job_id=result.job_id)
        
        # List jobs
        jobs = job.list(status=JobStatus.RUNNING)
        
        # Cancel a job
        job.cancel(job_id=result.job_id)
        ```
    """

    def __init__(
        self,
        config: Optional["ConnectionConfig"] = None,
        api_key: Optional[str] = None,
        access_token: Optional[str] = None,
        domain: Optional[str] = None,
        debug: Optional[bool] = None,
        request_timeout: Optional[float] = None,
    ):
        """
        Initialize the Job client.

        Args:
            config: ConnectionConfig instance. If not provided, a new one will be created.
            api_key: API key for authentication. Overrides config.api_key.
            access_token: Access token for authentication. Overrides config.access_token.
            domain: API domain. Overrides config.domain.
            debug: Enable debug mode. Overrides config.debug.
            request_timeout: Request timeout in seconds. Overrides config.request_timeout.
        """

        if config is None:
            config = ConnectionConfig()

        # Override config values if provided
        if api_key is not None:
            config.api_key = api_key
        if access_token is not None:
            config.access_token = access_token
        if domain is not None:
            config.domain = domain
        if debug is not None:
            config.debug = debug
        if request_timeout is not None:
            config.request_timeout = request_timeout

        self._config = config
        self._client = JobClient(config=config)

    def submit(
        self,
        name: str,
        script: str,
        cluster_id: Optional[int] = None,
        command: Optional[str] = None,
        resources: Optional[dict] = None,
        team_id: Optional[int] = None,
    ) -> JobSubmitResponse:
        """
        Submit a new job.

        Args:
            name: Job name
            script: Job script content
            cluster_id: Cluster ID to submit the job to
            command: Command to execute (optional)
            resources: Resource requirements dict (optional)
            team_id: Team ID (optional)

        Returns:
            JobSubmitResponse containing the submitted job information

        Raises:
            APIException: If the API returns an error
            AuthenticationException: If authentication fails
        """
        request = JobSubmitRequest(
            name=name,
            script=script,
            cluster_id=cluster_id,
            command=command,
            resources=resources,
            team_id=team_id,
        )

        response = submit_job.sync(client=self._client, body=request)

        if isinstance(response, ErrorResponse):
            raise handle_api_exception(
                Response(
                    status_code=HTTPStatus(response.code if response.code != 0 else 400),
                    content=json.dumps({"error": response.error}).encode() if response.error else b"",
                    headers={},
                    parsed=None,
                )
            )

        if response is None:
            raise APIException("Failed to submit job: No response from server")

        return response

    def get(
        self,
        job_id: int,
        cluster_id: int,
    ) -> JobModel:
        """
        Get job details by job ID.

        Args:
            job_id: Job ID
            cluster_id: Cluster ID

        Returns:
            Job model with job details

        Raises:
            NotFoundException: If the job is not found
            APIException: If the API returns an error
        """
        response = get_job.sync(
            id=job_id,
            client=self._client,
            cluster_id=cluster_id,
        )

        if isinstance(response, ErrorResponse):
            error_response = Response(
                status_code=HTTPStatus(response.code if response.code != 0 else 404),
                content=json.dumps({"error": response.error}).encode() if response.error else b"",
                headers={},
                parsed=None,
            )
            if error_response.status_code == 404:
                raise NotFoundException(f"Job {job_id} not found")
            raise handle_api_exception(error_response)

        if response is None:
            raise NotFoundException(f"Job {job_id} not found")

        return response

    def list(
        self,
        page: int = 1,
        page_size: int = 20,
        status: Optional[JobStatus] = None,
        user_id: Optional[int] = None,
        team_id: Optional[int] = None,
        cluster_id: Optional[int] = None,
    ) -> JobListResponse:
        """
        List jobs with optional filtering.

        Args:
            page: Page number (default: 1)
            page_size: Number of items per page (default: 20)
            status: Filter by job status (optional)
            user_id: Filter by user ID (optional)
            team_id: Filter by team ID (optional)
            cluster_id: Filter by cluster ID (optional)

        Returns:
            JobListResponse containing the list of jobs

        Raises:
            APIException: If the API returns an error
        """
        response = list_jobs.sync(
            client=self._client,
            page=page,
            page_size=page_size,
            status=status,
            user_id=user_id,
            team_id=team_id,
            cluster_id=cluster_id,
        )

        if isinstance(response, ErrorResponse):
            raise handle_api_exception(
                Response(
                    status_code=HTTPStatus(response.code if response.code != 0 else 400),
                    content=json.dumps({"error": response.error}).encode() if response.error else b"",
                    headers={},
                    parsed=None,
                )
            )

        if response is None:
            raise APIException("Failed to list jobs: No response from server")

        return response

    def cancel(
        self,
        job_id: int,
    ) -> bool:
        """
        Cancel a job.

        Args:
            job_id: Job ID to cancel

        Returns:
            True if the job was cancelled successfully

        Raises:
            NotFoundException: If the job is not found
            APIException: If the API returns an error
        """
        response = cancel_job.sync(
            id=job_id,
            client=self._client,
        )

        if isinstance(response, ErrorResponse):
            error_response = Response(
                status_code=HTTPStatus(response.code if response.code != 0 else 404),
                content=json.dumps({"error": response.error}).encode() if response.error else b"",
                headers={},
                parsed=None,
            )
            if error_response.status_code == 404:
                raise NotFoundException(f"Job {job_id} not found")
            raise handle_api_exception(error_response)

        return response is not None

