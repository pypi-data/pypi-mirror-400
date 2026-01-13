"""
XClient Python SDK for accessing XCloud Service API.

This package provides a client library for interacting with the XCloud Service API.
"""

from .api import Client, AuthenticatedClient
from .connection_config import (
    ConnectionConfig,
    ProxyTypes,
)
from .exceptions import (
    XClientException,
    TimeoutException,
    NotFoundException,
    AuthenticationException,
    InvalidArgumentException,
    NotEnoughSpaceException,
    RateLimitException,
    APIException,
)
from .job import Job, JobClient

__all__ = [
    # API
    "Client",
    "AuthenticatedClient",
    # Connection config
    "ConnectionConfig",
    "ProxyTypes",
    # Exceptions
    "XClientException",
    "TimeoutException",
    "NotFoundException",
    "AuthenticationException",
    "InvalidArgumentException",
    "NotEnoughSpaceException",
    "RateLimitException",
    "APIException",

    # Job SDK
    "Job",
    "JobClient",
]

__version__ = "1.0.0"

