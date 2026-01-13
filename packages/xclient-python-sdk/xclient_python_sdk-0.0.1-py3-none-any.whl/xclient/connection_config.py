import os

from typing import Literal, Optional, Dict
from httpx._types import ProxyTypes

REQUEST_TIMEOUT: float = 30.0  # 30 seconds

KEEPALIVE_PING_INTERVAL_SEC = 50  # 50 seconds
KEEPALIVE_PING_HEADER = "Keepalive-Ping-Interval"

# API path prefix
DEFAULT_API_PATH: str = "/api/v1"


class ConnectionConfig:
    """
    Configuration for the connection to the API.
    """

    @staticmethod
    def _domain():
        return os.getenv("XCLIENT_DOMAIN", "localhost:8090")

    @staticmethod
    def _debug():
        return os.getenv("XCLIENT_DEBUG", "false").lower() == "true"

    @staticmethod
    def _api_key():
        return os.getenv("XCLIENT_API_KEY")

    @staticmethod
    def _access_token():
        return os.getenv("XCLIENT_ACCESS_TOKEN")

    @staticmethod
    def _api_path():
        return os.getenv("XCLIENT_API_PATH", DEFAULT_API_PATH)

    def __init__(
        self,
        domain: Optional[str] = None,
        debug: Optional[bool] = None,
        api_key: Optional[str] = None,
        access_token: Optional[str] = None,
        request_timeout: Optional[float] = None,
        headers: Optional[Dict[str, str]] = None,
        proxy: Optional[ProxyTypes] = None,
        api_path: Optional[str] = None,
    ):
        self.domain = domain or ConnectionConfig._domain()
        self.debug = debug or ConnectionConfig._debug()
        self.api_key = api_key or ConnectionConfig._api_key()
        self.access_token = access_token or ConnectionConfig._access_token()
        self.headers = headers or {}
        self.proxy = proxy
        self.api_path = api_path or ConnectionConfig._api_path()

        self.request_timeout = ConnectionConfig._get_request_timeout(
            REQUEST_TIMEOUT,
            request_timeout,
        )

        if request_timeout == 0:
            self.request_timeout = None
        elif request_timeout is not None:
            self.request_timeout = request_timeout
        else:
            self.request_timeout = REQUEST_TIMEOUT

        # Ensure api_path starts with /
        if not self.api_path.startswith("/"):
            self.api_path = "/" + self.api_path

        # Build API URL
        if self.debug:
            base_url = "http://localhost:8090"
        else:
            # If domain already includes protocol, use it as-is
            # Otherwise, default to http:// for backward compatibility
            if self.domain.startswith(("http://", "https://")):
                base_url = self.domain
            else:
                base_url = f"http://{self.domain}"
        
        self.api_url = f"{base_url}{self.api_path}"

    @staticmethod
    def _get_request_timeout(
        default_timeout: Optional[float],
        request_timeout: Optional[float],
    ):
        if request_timeout == 0:
            return None
        elif request_timeout is not None:
            return request_timeout
        else:
            return default_timeout

    def get_request_timeout(self, request_timeout: Optional[float] = None):
        return self._get_request_timeout(self.request_timeout, request_timeout)


# Re-export ProxyTypes for convenience
__all__ = ["ConnectionConfig", "ProxyTypes"]

