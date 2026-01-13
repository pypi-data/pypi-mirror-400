def format_request_timeout_error() -> Exception:
    return TimeoutException(
        "Request timed out — the 'request_timeout' option can be used to increase this timeout",
    )


def format_execution_timeout_error() -> Exception:
    return TimeoutException(
        "Execution timed out — the 'timeout' option can be used to increase this timeout",
    )


class XClientException(Exception):
    """
    Base class for all XClient errors.

    Raised when a general XClient exception occurs.
    """

    pass


class TimeoutException(XClientException):
    """
    Raised when a timeout occurs.

    The `unavailable` exception type is caused by service timeout.\n
    The `canceled` exception type is caused by exceeding request timeout.\n
    The `deadline_exceeded` exception type is caused by exceeding the timeout for process, watch, etc.\n
    The `unknown` exception type is sometimes caused by the service timeout when the request is not processed correctly.\n
    """

    pass


class InvalidArgumentException(XClientException):
    """
    Raised when an invalid argument is provided.
    """

    pass


class NotEnoughSpaceException(XClientException):
    """
    Raised when there is not enough disk space.
    """

    pass


class NotFoundException(XClientException):
    """
    Raised when a resource is not found.
    """

    pass


class AuthenticationException(XClientException):
    """
    Raised when authentication fails.
    """

    pass


class RateLimitException(XClientException):
    """
    Raised when the API rate limit is exceeded.
    """

    pass


class APIException(XClientException):
    """
    Raised when an API error occurs.
    """

    pass

