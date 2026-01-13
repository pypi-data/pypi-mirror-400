"""
Module with decorators used in ``pyrelukko``.
"""
import os
import time
from functools import wraps
from typing import Union

from pyrelukko import RelukkoDTO

# pylint: disable=too-many-arguments,too-many-positional-arguments
def retry(logger, exceptions, tries: Union[float, int]=4,
          delay: Union[float, int]=5, backoff: Union[float, int]=2.0,
          max_delay=None):
    """Retry calling the decorated function using an exponential backoff.

    See https://www.calazan.com/retry-decorator-for-python-3/

    :param logger: Python logger that supports ``warning()``.
    :type logger: Logger
    :param exceptions: The exception to catch and retry the decorated function
                       again. May be a tuple of exceptions to catch.
    :type exceptions: Exception|Tuple[Exception, Exception]
    :param tries: Number of times to try (not retry) before giving up,
                  defaults to 4.
    :type tries: int, optional
    :param delay: Initial delay between retries in seconds, defaults to 5.
    :type delay: int, optional
    :param backoff: Backoff multiplier (e.g. value of 2 will double the delay
                    with each retry), defaults to 2.0.
    :type backoff: float, optional
    :param max_delay: The maximum value the delay between retries can grow,
                      defaults to None.
    :type max_delay: int|float, optional
    """
    def deco_retry(f):
        @wraps(f)
        def f_retry(*args, **kwargs):
            remaining_tries, retry_delay = tries, delay
            while remaining_tries > 1:
                try:
                    return f(*args, **kwargs)
                except exceptions:
                    remaining_tries -= 1
                    logger.warning('(%i/%i): Retrying in %i seconds...',
                        tries - remaining_tries,
                        tries,
                        retry_delay,
                    )
                    time.sleep(retry_delay)
                    if max_delay is not None:
                        retry_delay = min(retry_delay*backoff, max_delay)
                    else:
                        retry_delay *= backoff
            return f(*args, **kwargs)
        return f_retry  # true decorator
    return deco_retry


SKIP_RELUKKO = RelukkoDTO.from_dict({
    "id": "00000000-0000-0000-0000-000000000000",
    "lock_name": "WE TRUST YOU",
    "creator": "Dummy Dummy",
    "ip": "0.0.0.0",
    "expires_at": "1970-01-01T00:00:00Z",
    "created_at": "1970-01-01T00:00:00Z",
    "updated_at": "1970-01-01T00:00:00Z"
})


def skip_http_call():
    """
    Decorator for pyrelukko methods to skip HTTP calls.

    It skips the actual method if the environment variable
    ``RELUKKO_TRUST_ME_IT_IS_LOCKED`` is set and returns instead a static lock
    dictionary or list with the same static lock dictionary.

    Useful when developing and the resource is for sure locked, e.g through the
    Web UI.
    """
    def deco_skip(f):

        @wraps(f)
        def f_skip(*args, **kwargs):
            if os.environ.get('RELUKKO_TRUST_ME_IT_IS_LOCKED'):
                if f.__name__ == "get_locks":
                    return [ SKIP_RELUKKO ]
                return SKIP_RELUKKO
            return f(*args, **kwargs)
        return f_skip  # true decorator
    return deco_skip
