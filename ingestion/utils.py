import logging

import requests
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_random,
)

MIN_WAIT_TIME = 1
MAX_WAIT_TIME = 5
MAX_ATTEMPTS = 5

_logger = logging.getLogger("ingestion")


@retry(
    before_sleep=before_sleep_log(_logger, logging.WARNING),
    reraise=True,
    wait=wait_random(MIN_WAIT_TIME, MAX_WAIT_TIME),
    stop=stop_after_attempt(MAX_ATTEMPTS),
    retry=retry_if_exception_type(requests.RequestException),
)
def send_request(session: requests.Session, **kwargs) -> requests.Response:
    """
    Sends an HTTP request using the provided session, with automatic retries on failure.

    :param session: The `requests` session object used to send the HTTP request.
    :param **kwargs: The parameters to be passed to the `session.request()` method, such as `url`, `method`, `params`, etc.
    :return: The HTTP response object returned by the `session.request()` method.
    :rtype: requests.Response
    :raises requests.RequestException: If the request fails after the maximum number of retry attempts,
        a `RequestException` is raised. This includes connection errors, timeout errors, and other types of errors.
    """
    response = session.request(**kwargs)
    response.raise_for_status()
    return response
