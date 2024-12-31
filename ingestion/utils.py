import logging

import requests
from tenacity import (
    before_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_random,
)

_logger = logging.getLogger(__name__)


@retry(
    before=before_log(_logger, logging.DEBUG),
    wait=wait_random(1, 5),
    stop=stop_after_attempt(5),
    retry=retry_if_exception_type(requests.RequestException),
)
def send_request(session: requests.Session, **kwargs) -> requests.Response:
    response = session.request(**kwargs)
    response.raise_for_status()
    return response
