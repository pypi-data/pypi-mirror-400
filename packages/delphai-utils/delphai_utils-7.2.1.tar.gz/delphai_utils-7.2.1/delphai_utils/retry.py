from httpx import (
    StreamError,
    TimeoutException,
    NetworkError,
    ProtocolError,
    ProxyError,
    HTTPStatusError,
)
from tenacity import retry as tenacity_retry
from tenacity import (
    retry_if_exception_type,
    retry_if_exception,
    stop_after_attempt,
    wait_random_exponential,
)

HTTP_RETRY_EXCEPTION_TYPES = (
    TimeoutException,
    NetworkError,
    ProtocolError,
    ProxyError,
    StreamError,
)


def test_response_status_code(exception):
    if not isinstance(exception, HTTPStatusError):
        return False

    if 500 <= exception.response.status_code < 600:
        return True

    return exception.response.status_code in (
        408,  # Request Timeout
        429,  # Too Many Requests
    )


def retry_httpx(
    stop=stop_after_attempt(3),
    wait=wait_random_exponential(multiplier=1, max=60, min=1),
    retry=retry_if_exception_type(tuple(HTTP_RETRY_EXCEPTION_TYPES))
    | retry_if_exception(test_response_status_code),
    reraise=True,
    **kwargs,
):
    return tenacity_retry(stop=stop, wait=wait, retry=retry, reraise=reraise, **kwargs)
