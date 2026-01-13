import json
import logging
from typing import Optional
from httpx import Limits

from ..api.client.client import AuthenticatedClient
from ..connection_config import ConnectionConfig
from ..api.metadata import default_headers
from ..exceptions import (
    AuthenticationException,
    RateLimitException,
    NotFoundException,
    APIException,
)
from ..api.client.types import Response

logger = logging.getLogger(__name__)


def handle_api_exception(e: Response):
    """Handle API exceptions and convert them to appropriate XClient exceptions."""
    try:
        body = json.loads(e.content) if e.content else {}
    except json.JSONDecodeError:
        body = {}

    if e.status_code == 401:
        return AuthenticationException(
            f"Authentication failed: {body.get('error', 'Invalid credentials')}"
        )
    
    if e.status_code == 404:
        return NotFoundException(
            f"Resource not found: {body.get('error', 'The requested resource was not found')}"
        )

    if e.status_code == 429:
        return RateLimitException(
            f"{e.status_code}: Rate limit exceeded, please try again later."
        )

    if "error" in body:
        return APIException(f"{e.status_code}: {body['error']}")
    
    if "message" in body:
        return APIException(f"{e.status_code}: {body['message']}")
    
    return APIException(f"{e.status_code}: {e.content}")


class JobClient(AuthenticatedClient):
    """
    The client for interacting with the XClient Job API.
    """

    def __init__(
        self,
        config: ConnectionConfig,
        require_api_key: bool = True,
        require_access_token: bool = False,
        limits: Optional[Limits] = None,
        *args,
        **kwargs,
    ):
        if require_api_key and require_access_token:
            raise AuthenticationException(
                "Only one of api_key or access_token can be required, not both",
            )

        if not require_api_key and not require_access_token:
            raise AuthenticationException(
                "Either api_key or access_token is required",
            )

        token = None
        if require_api_key:
            if config.api_key is None:
                raise AuthenticationException(
                    "API key is required. "
                    "You can either set the environment variable `XCLIENT_API_KEY` "
                    'or pass it directly like JobClient(api_key="xclient_...")',
                )
            token = config.api_key

        if require_access_token:
            if config.access_token is None:
                raise AuthenticationException(
                    "Access token is required. "
                    "You can set the environment variable `XCLIENT_ACCESS_TOKEN` "
                    "or pass the `access_token` in options.",
                )
            token = config.access_token

        auth_header_name = "X-API-KEY" if require_api_key else "Authorization"
        prefix = "" if require_api_key else "Bearer"

        headers = {
            **default_headers,
            **(config.headers or {}),
        }

        httpx_args = {
            "event_hooks": {
                "request": [self._log_request],
                "response": [self._log_response],
            },
        }
        
        if config.proxy is not None:
            httpx_args["proxy"] = config.proxy
        
        if limits is not None:
            httpx_args["limits"] = limits

        super().__init__(
            base_url=config.api_url,
            httpx_args=httpx_args,
            headers=headers,
            token=token,
            auth_header_name=auth_header_name,
            prefix=prefix,
            *args,
            **kwargs,
        )

    def _log_request(self, request):
        logger.info(f"Request {request.method} {request.url}")

    def _log_response(self, response: Response):
        if response.status_code >= 400:
            logger.error(f"Response {response.status_code}")
        else:
            logger.info(f"Response {response.status_code}")


# We need to override the logging hooks for the async usage
class AsyncJobClient(JobClient):
    async def _log_request(self, request):
        logger.info(f"Request {request.method} {request.url}")

    async def _log_response(self, response: Response):
        if response.status_code >= 400:
            logger.error(f"Response {response.status_code}")
        else:
            logger.info(f"Response {response.status_code}")

