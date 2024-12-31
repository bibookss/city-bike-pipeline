import logging
import os

import pandas as pd
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

    :param session: The `requests` session object used to send the HTTP request.
    :param kwargs: The parameters to be passed to the `session.request()` method, such as `url`, `method`, `params`, etc.
    :return: The HTTP response object returned by the `session.request()` method.
    :rtype: requests.Response
    :raises requests.RequestException: If the request fails after the maximum number of retry attempts,
        a `RequestException` is raised. This includes connection errors, timeout errors, and other types of errors.
    """
    response = session.request(**kwargs)
    response.raise_for_status()
    return response


def save_file(df: pd.DataFrame, file_path: str) -> None:
    """
    Saves a DataFrame to a specified file path in CSV format.

    :param df: The DataFrame to be saved.
    :param file_path: The file path where the DataFrame should be saved.
    :return: None
    :rtype: None
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    _logger.info("Saving %s rows and %s columns to %s", *df.shape, file_path)
    df.to_csv(file_path, sep="|", index=None)
    _logger.info("Data saved successfully to %s", file_path)


def flatten_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Flattens a DataFrame by expanding columns with lists or dictionaries.

    :param df: The DataFrame to be flattened.
    :return: A new DataFrame with flattened columns.
    :rtype: pd.DataFrame
    """
    columns_to_check = df.columns.tolist()
    while columns_to_check:
        column = columns_to_check.pop()
        if df[column].apply(lambda x: isinstance(x, list)).any():
            df[column] = df[column].apply(
                lambda x: "&&".join(map(str, x)) if isinstance(x, list) else str(x)
            )

        elif df[column].apply(lambda x: isinstance(x, dict)).any():
            dict_df = df[column].apply(pd.Series)  # Flatten dictionary
            dict_df.columns = [
                f"{column}_{col}" for col in dict_df.columns
            ]  # Add prefix to columns
            df = pd.concat(
                [df.drop(columns=column), dict_df], axis=1
            )  # Concatenate the new columns
            columns_to_check.extend(dict_df.columns.tolist())

    return df
