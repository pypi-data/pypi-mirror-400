"""
HTTP utils module
"""

import functools
import logging

from contextlib import contextmanager
from importlib import import_module
from typing import Any
from typing import Generator
from typing import Optional

from requests import Response
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3 import Retry


def _log_response(response: Response, *args: Any, **kwargs: Any) -> None:
    logging.debug("Request to %s returned status code %d", response.url, response.status_code)


def _check_for_errors(response: Response, *args: Any, **kwargs: Any) -> None:
    response.raise_for_status()


@contextmanager
def request(total: int = 3, backoff_factor: float = 0.1, **kwargs: Any) -> Generator[Session, None, None]:
    """
    Generate a requests session that allows retries and raises HTTP errors (status code >= 400).
    Uses the same arguments as the class Retry from urllib3
    """
    settings = import_module("jsm_user_services.settings")
    JSM_USER_SERVICE_HTTP_TIMEOUT = float(getattr(settings, "JSM_USER_SERVICE_HTTP_TIMEOUT", 30))

    session = Session()
    session.hooks.update(response=[_log_response, _check_for_errors])
    max_retries = Retry(total=total, backoff_factor=backoff_factor, **kwargs)
    adapter = HTTPAdapter(max_retries=max_retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    session.request = functools.partial(session.request, timeout=JSM_USER_SERVICE_HTTP_TIMEOUT)  # type: ignore
    try:
        yield session
    finally:
        session.close()


def get_response_body(response: Response) -> Any:
    """
    Deserialize response
    """
    try:
        response_body = response.json()
    except ValueError:
        response_body = response.text
    return response_body


def convert_header_to_meta_key(header: Optional[str]) -> Optional[str]:
    """
    Django Http Request has a dictionary called META with the request headers.
    But it replaces the header name following the rules:
      - all characters to uppercase
      - replacing any hyphens with underscores
      - adding an HTTP_ prefix to the name.
    So, for example, a header called X-Bender would be mapped to the META key HTTP_X_BENDER.
    """
    if header is None:
        return None

    return f"HTTP_{header.replace('-', '_')}".upper()
