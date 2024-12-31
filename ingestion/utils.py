import logging

import requests
from tenacity import (
    before_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_random,
)

_logger = logging.getLogger("ingestion")

# Constants for retry behavior
MIN_WAIT_TIME = 1
MAX_WAIT_TIME = 5
MAX_ATTEMPTS = 5


@retry(
    before=before_log(_logger, logging.DEBUG),
    wait=wait_random(MIN_WAIT_TIME, MAX_WAIT_TIME),
    stop=stop_after_attempt(MAX_ATTEMPTS),
    retry=retry_if_exception_type(requests.RequestException),
)
def send_request(session: requests.Session, **kwargs) -> requests.Response:
    """
    Sends an HTTP request using the provided session, with automatic retries on failure.

    Arguments:
        session (requests.Session): The `requests` session object that will be used to send the HTTP request.
        **kwargs: The parameters that will be passed to the `session.request()` method, such as `url`, `method`, `params`, etc.

    Returns:
        requests.Response: The HTTP response object returned by the `session.request()` method.

    Raises:
        requests.RequestException: If the request fails after the maximum number of retry attempts,
        a `RequestException` will be raised. This includes connection errors, timeout errors,
        and any other type of error that occurs during the request.
    """
    response = session.request(**kwargs)
    response.raise_for_status()
    return response
