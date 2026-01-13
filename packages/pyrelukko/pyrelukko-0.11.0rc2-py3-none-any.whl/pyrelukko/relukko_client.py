"""
PyRelukko main module with the Relukko client.
"""
import asyncio
import json
import logging
import os
import ssl
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Union

import requests
from urllib3.util import Url, parse_url
from urllib3.util.retry import Retry
from websockets import ConnectionClosed as WsConnectionClosed
from websockets.asyncio.client import connect as ws_connect

from pyrelukko.decorators import retry, skip_http_call
from pyrelukko import RelukkoDTO

SSL_KWARGS = [
    'check_hostname',
    'hostname_checks_common_name',
    'verify_mode',
    'verify_flags',
    'options',
]

RETRY_KWARGS = [
    'tries',
    'delay',
    'backoff',
    'max_delay',
    'exceptions',
]

OWN_KWARGS = [
    'acquire_wait_for_timeout',
    'acquire_modulo',
    'disable_websocket',
    'raise_when_acquire_fails',
    'ws_ping_interval',
    'ws_ping_timeout',
    'ws_wait_for_timeout',
]
OWN_KWARGS.extend(RETRY_KWARGS)

logger = logging.getLogger(__name__)


class RelukkoDoRetry(Exception):
    """
    Exception thrown on some errors which we still want to retry
    """

# pylint: disable=too-many-instance-attributes
class RelukkoClient:
    """
    RelukkuClient
    =============

    The RelukkoClient class provides a convenient and efficient way to interact
    with the Relukko API, allowing you to manage locks, acquire and release
    locks, and perform other operations related to the Relukko backend. The
    client handles the underlying HTTP requests and responses, providing a
    simple and intuitive interface for working with the Relukko API.

    .. _class-kwargs-label:

    Kwargs
    ------
  
    The methods ``__init__()`` and ``reconfigure_relukko()`` pass through the
    ``kwargs`` to underlying libraries, following a non-exhaustive selection
    of kwargs which are passed further and understood.
  
    =========================== ======================== ===============
    kwarg                       Used in                  Comments
    =========================== ======================== ===============
    check_hostname              SSLContext               [1]
    hostname_checks_common_name SSLContext               [1]
    verify_mode                 SSLContext               [1]
    verify_flags                SSLContext               [1]
    options                     SSLContext               [1]
    cafile                      SSLContext               [1], [5], [10]
    capath                      SSLContext               [1], [5], [10]
    cadata                      SSLContext               [1], [5], [10]
    tries                       pyrelukko.retry          [2]
    delay                       pyrelukko.retry          [2]
    backoff                     pyrelukko.retry          [2]
    max_delay                   pyrelukko.retry          [2]
    exceptions                  pyrelukko.retry          [2]
    total                       urllib3.util.Retry       [3]
    connect                     urllib3.util.Retry       [3]
    read                        urllib3.util.Retry       [3]
    redirect                    urllib3.util.Retry       [3]
    status                      urllib3.util.Retry       [3]
    other                       urllib3.util.Retry       [3]
    backoff_factor              urllib3.util.Retry       [3]
    backoff_max                 urllib3.util.Retry       [3]
    backoff_jitter              urllib3.util.Retry       [3]
    raise_on_redirect           urllib3.util.Retry       [3]
    raise_on_status             urllib3.util.Retry       [3]
    headers                     requests.Session         [4], [7]
    cookies                     requests.Session         [4]
    auth                        requests.Session         [4]
    proxies                     requests.Session         [4], (6]
    hooks                       requests.Session         [4]
    params                      requests.Session         [4]
    verify                      requests.Session         [4], [9], (10]
    cert                        requests.Session         [4], [9], (10]
    adapters                    requests.Session         [4], (8]
    stream                      requests.Session         [4]
    trust_env                   requests.Session         [4], [6]
    max_redirects               requests.Session         [4]
    acquire_wait_for_timeout    pyrelukko.relukko_client .
    acquire_modulo              pyrelukko.relukko_client .
    disable_websocket           pyrelukko.relukko_client .
    raise_when_acquire_fails    pyrelukko.relukko_client [11]
    ws_ping_interval            pyrelukko.relukko_client .
    ws_ping_timeout             pyrelukko.relukko_client .
    ws_wait_for_timeout         pyrelukko.relukko_client .
    =========================== ======================== ===============
  
    - **[1]** TLS settings only used for the WebSockets, not for the HTTP
      requests! See:
      `SSLContext <https://docs.python.org/3/library/ssl.html#ssl.SSLContext>`__
    - **[2]** See:
      `Retry <https://gitlab.com/relukko/pyrelukko/-/blob/master/src/pyrelukko/retry.py?ref_type=heads#L9>`__
    - **[3]** See:
      `urllib3.util.Retry <https://urllib3.readthedocs.io/en/stable/reference/urllib3.util.html#urllib3.util.Retry>`__
    - **[4]** See:
      `Request Sessions <https://docs.python-requests.org/en/latest/api/#request-sessions>`__
    - **[5]** Used in:
      `load_verify_locations <https://docs.python.org/3/library/ssl.html#ssl.SSLContext.load_verify_locations>`__
    - **[6]** Proxies only work for the HTTP requests! But not for the
      WebSockets used to monitor for deletions! So will probably not work as
      expected.
    - **[7]** This overwrites the header entry set for the API-KEY! Ensure to add
      it yourself (``X-api-Key``)!
    - **[8]** Interferes with the "Retry" from ``urllib3``!
    - **[9]** TLS settings only used for the HTTP requests, not for the
      WebSockets!
    - **[10]** Also takes the environment variables ``REQUESTS_CA_BUNDLE`` or
      ``CURL_CA_BUNDLE`` into account! But the arguments take precedence over
      the environment variables. For HTTP requests use of the variables see
      `SSL Cert Verification <https://requests.readthedocs.io/en/stable/user/advanced/#ssl-cert-verification>`__
      The behavior for the WebSockets should be the same.
    - **[11]** Do not change! It will break things.

    .. _class-dto-label:

    Relukko DTO
    -----------

    The Relukko JSON DTO::

      {
        "id": "950daa20-a814-451e-9407-ec496cf9c136",
        "lock_name": "eb3a4185-185b-4ac6-a63d-5d1f20e55134",
        "creator": "Demo Creator",
        "ip": "10.89.0.6",
        "expires_at": "2024-10-31T20:14:43.9313Z",
        "created_at": "2024-10-31T20:04:43.9313Z",
        "updated_at": "2024-10-31T20:04:43.9313Z"
      }

    Skip locking
    ------------

    Do the following to acquire the lock by hand and skip the actual locking:

    - Create the needed lock (or locks) by hand from the Web UI.
    - Set the expire time far in the future from the Web UI.
    - Set the environment variable ``RELUKKO_TRUST_ME_IT_IS_LOCKED`` to an
      value, e.g. ``yes``.
    - Start your coding session with debug runs.
    - Once you are done, unset the environment variable and delete the lock
      from the Web UI.

   """
    def __init__(
            self, base_url: Union[Url, str], api_key:str, **kwargs):
        """Initializes a new instance of the Relukko API client.

        Initializes a new instance of the Relukko API client with the
        specified base URL and API key. The kwargs parameter can be used to
        specify additional configuration options for the client.

        The ``kwargs`` offers additional configuration options for the Relukko
        API client. See the chapter :ref:`class-kwargs-label` for possible
        values.

        :param base_url: The base URL of the Relukko API.
        :type base_url: Union[Url, str]
        :param api_key: The API key for the Relukko API.
        :type api_key: str
        """
        self.session = requests.Session()
        self.api_key = api_key
        self.tries=4
        self.delay=5
        self.backoff=2.0
        self.max_delay=None
        self.exceptions = (
            requests.ConnectionError,
            RelukkoDoRetry,
        )
        self._setup_session(api_key, **kwargs)
        self._setup_http_adapters_retry(**kwargs)
        self.acquire_modulo = 100
        self.acquire_wait_for_timeout = 2
        self.disable_websocket = False
        self.raise_when_acquire_fails = True
        self.ws_ping_interval = 60
        self.ws_ping_timeout = 20
        self.ws_wait_for_timeout = 2
        self._setup_pyrelukko_kwargs(**kwargs)

        self.base_url = self._setup_base_url(base_url)
        self.ws_url = self._setup_ws_url(str(self.base_url))
        self.ssl_ctx: ssl.SSLContext = None
        self._setup_ssl_ctx(**kwargs)

        # event for websocket thread to signal it got a message
        self.message_received = threading.Event()
        # As long as it's set the websocket thread runs
        self.ws_running = threading.Event()
        self.ws_listener: threading.Thread = None

    def reconfigure_relukko(
            self, base_url: Union[Url, str]=None, api_key: str=None, **kwargs):
        """Reconfigures the Relukko API client with new settings.

        Reconfigures the Relukko API client with new settings, such as the
        base URL and API key. The function takes two optional parameters:
        ``base_url`` and ``api_key``, which can be used to update the client's
        configuration. If no value is provided for one of these fields, the
        existing value will be retained.

        The ``kwargs`` offers additional configuration options for the Relukko
        API client. See the chapter :ref:`class-kwargs-label` for possible values.

        :param base_url: The new base URL for the Relukko API client (optional).
        :type base_url: Union[Url, str], optional
        :param api_key: The new API key for the Relukko API client (optional).
        :type api_key: str, optional
        """
        self.api_key = api_key or self.api_key
        self._setup_session(self.api_key, **kwargs)
        self._setup_http_adapters_retry(**kwargs)
        self.base_url = self._setup_base_url(base_url or self.base_url)
        self.ws_url = self._setup_ws_url(str(self.base_url))
        self._setup_ssl_ctx(**kwargs)
        self._setup_pyrelukko_kwargs(**kwargs)

    def _setup_pyrelukko_kwargs(self, **kwargs):
        for kwarg in OWN_KWARGS:
            setattr(
                self,
                kwarg,
                kwargs.get(kwarg, getattr(self, kwarg))
            )

    def _setup_http_adapters_retry(self, **kwargs):
        for _, http_adapter in self.session.adapters.items():
            http_retry: Retry = http_adapter.max_retries
            for key, value in kwargs.items():
                if hasattr(http_retry, key):
                    setattr(http_retry, key, value)
            http_adapter.max_retries = http_retry

    def _setup_session(self, api_key: str, **kwargs):
        self.session.headers['X-api-Key'] = api_key
        for key, value in kwargs.items():
            if hasattr(self.session, key):
                setattr(self.session, key, value)

    def _setup_ssl_ctx(self, **kwargs) -> Union[ssl.SSLContext, None]:
        if self.ws_url.scheme == "wss":
            if self.ssl_ctx is None:
                self.ssl_ctx = ssl.create_default_context(
                    ssl.Purpose.SERVER_AUTH)
            for kwarg in SSL_KWARGS:
                setattr(
                    self.ssl_ctx,
                    kwarg,
                    kwargs.get(kwarg, getattr(self.ssl_ctx, kwarg)))

            # Try to behave like requests library and take *_CA_BUNDLE env vars
            # into account.
            ca_bundle = (
                os.environ.get("REQUESTS_CA_BUNDLE")
                or os.environ.get("CURL_CA_BUNDLE"))

            ca_bundle_file = None
            ca_bundle_path = None
            if ca_bundle is not None:
                ca_bundle = Path(ca_bundle)
                ca_bundle_file = ca_bundle if ca_bundle.is_file() else None
                ca_bundle_path = ca_bundle if ca_bundle.is_dir() else None

            # values from kwargs take precedence env vars
            ca_file = kwargs.get('cafile', ca_bundle_file)
            ca_path = kwargs.get('capath', f"{ca_bundle_path}/")
            ca_data = kwargs.get('cadata')

            if ca_file or ca_path or ca_data:
                self.ssl_ctx.load_verify_locations(
                    cafile=ca_file, capath=ca_path, cadata=ca_data)
        else:
            self.ssl_ctx = None

    def _setup_ws_url(self, ws_url: str) -> Url:
        url = ws_url.replace("http", "ws", 1)
        return parse_url(f"{url}/ws/broadcast")

    def _setup_base_url(self, base_url: Union[Url, str]) -> Url:
        if isinstance(base_url, str):
            base_url = parse_url(base_url)
        if not isinstance(base_url, Url):
            raise ValueError("must be URL or string!")

        return base_url

    async def _websocket_listener(self):
        """
        The WebSocket thread, which waits for messages from Relukko and
        notifies the HTTP thread in case deletions happened, so the HTTP
        can retry to get the lock. Does not verify the wanted lock got
        deleted yet.
        """
        additional_headers = { "X-API-KEY": self.api_key }
        async with ws_connect(
            str(self.ws_url),
            additional_headers=additional_headers,
            ssl=self.ssl_ctx,
            logger=logger,
            ping_interval=self.ws_ping_interval,
            ping_timeout=self.ws_ping_timeout,
        ) as websocket:
            while self.ws_running.is_set():
                try:
                    ws_message = await asyncio.wait_for(
                        websocket.recv(), timeout=self.ws_wait_for_timeout)
                    if ws_message:
                        logger.debug("Received message: '%s'", ws_message)
                        msg: Dict = json.loads(ws_message)
                        if msg.get('deleted'):
                            # Signal the HTTP thread to wake up
                            self.message_received.set()
                except TimeoutError:
                    # no messages, try in a moment again...
                    time.sleep(0.5)
                except WsConnectionClosed:
                    logger.error("Lost WS connection!")
                    continue

    def _acquire_relukko(
            self, url: Union[Url, str], max_run_time: int,
            payload: Dict, _thread_store: List):
        """
        The HTTP thread which tries to create the Relukko lock.
        """

        start_time = time.time()
        loop_counter = 0
        got_message = False
        res = None
        while True:
            elapsed_time = time.time() - start_time
            if elapsed_time > max_run_time:
                self.ws_running.clear()
                _thread_store.insert(0, None)
                break
            # If self.message_received is True try to get lock ASAP!
            # Otherwise only in every Nth run in case websocket broke.
            if got_message or loop_counter % self.acquire_modulo == 0:
                try:
                    res = self._make_request(
                        url=url, method="POST", payload=payload)
                except (
                    *self.exceptions, RuntimeError, requests.HTTPError) as e:
                    logger.warning("Last exception was: %s!\nGiving up!", e)
                    _thread_store.insert(0, e)
                    break
            loop_counter += 1
            if res is None:
                # Conflict 409
                got_message = self.message_received.wait(
                    timeout=self.acquire_wait_for_timeout)
                self.message_received.clear()
                continue

            _thread_store.insert(0, res)
            self.ws_running.clear()
            break

    def _check_response(self, response: requests.Response):
        match response.status_code:
            case 200 | 201:
                resp_json = response.json()
                if isinstance(resp_json, list):
                    return [RelukkoDTO.from_dict(x) for x in resp_json]
                return RelukkoDTO.from_dict(resp_json)
            case 404 | 422:
                return response.json()
            case 400 | 403:
                err = response.json()
                logger.warning("4xx HTTP Error [%d](%s) - %s:%s",
                    response.status_code, response.reason,
                    str(err.get('status')), err.get('message'))
                response.raise_for_status()
            case 409:
                err = response.json()
                logger.warning("409 HTTP Error [%d](%s) - %s:%s",
                    response.status_code, response.reason,
                    str(err.get('status')), err.get('message'))
                return None
            case 500 | 502 | 503 | 504:
                logger.warning("[%d](%s) %s",
                    response.status_code, response.reason, response.text)
                raise RelukkoDoRetry(
                    f"5xx HTTP Error: [{response.status_code}]"
                    f"({response.reason})")
            case _:
                logger.warning("[%d](%s) %s",
                    response.status_code, response.reason, response.text)
                raise RuntimeError(
                    f"Give up: [{response.status_code}]({response.reason})")

    def _make_request(
            self,
            url: str,
            method: str,
            payload: Dict=None) -> requests.Response:


        @retry(logger, exceptions=self.exceptions, tries=self.tries,
               delay=self.delay, backoff=self.backoff,
               max_delay=self.max_delay)
        def _do_request():
            response = self.session.request(
                method=method,
                url=url,
                json=payload,
            )
            return self._check_response(response)

        return _do_request()

    @skip_http_call()
    def acquire_relukko(
        self, lock_name: str,
        creator: Union[str, None],
        max_run_time: int,
    ) -> Union[RelukkoDTO, dict, None, Exception]:
        """Acquires a lock in Relukko.

        Attempts to acquire a lock with the specified name. If the lock is
        successfully acquired, the function returns a Relukko DTO object
        containing information about the lock. If the lock cannot be acquired
        within the specified ``max_run_time``, the function returns ``None``.

        ``acquire_relukko()`` is a blocking operation that continuously attempts
        to obtain the specified lock until it succeeds or the configured timeout
        is reached. While waiting, it performs periodic retry attempts and, when
        possible, establishes an optional WebSocket connection to the Relukko
        backend to receive immediate notifications of lock state changes. If a
        relevant change occurs — such as any lock being deleted — the function
        promptly retries acquisition without waiting for the next scheduled
        attempt. WebSocket usage is best-effort and may be unavailable in
        certain environments (e.g., when routed through proxies), in which case
        the function falls back to regular polling.

        :param lock_name: The name of the lock.
        :type lock_name: str
        :param creator: Optional name of the lock creator.
        :type creator: Union[str, None]
        :param max_run_time: How long to maximal try to get the lock in
                             seconds.
        :type max_run_time: int
        :return: The DTO of the created/acquired lock. Returns None if acquisition times out.
        :rtype: Union[RelukkoDTO, Dict, None, Exception]
        """
        payload = {
            "lock_name": lock_name,
            "creator": creator,
        }

        url = f"{self.base_url}/v1/locks/"

        if not self.disable_websocket:
            self.ws_running.set()
            self.ws_listener = threading.Thread(
                target=asyncio.run, args=(self._websocket_listener(),))
            self.ws_listener.start()

        thread_store = []
        http_thread = threading.Thread(
            target=self._acquire_relukko,
            args=(url, max_run_time, payload, thread_store))
        http_thread.start()
        http_thread.join()

        if not self.disable_websocket:
            self.ws_listener.join()

        if thread_store:
            if (
                self.raise_when_acquire_fails
                and isinstance(thread_store[0], Exception)
            ):
                raise thread_store[0]
            return thread_store[0]
        return None

    @skip_http_call()
    def get_lock(self, lock_id: str) -> Union[RelukkoDTO, Dict]:
        """Retrieves a single lock from Relukko by ID.

        :param lock_id: The ID of the lock to retrieve.
        :type lock_id: str
        :return: A Relukko DTO object of the retrieved lock on success, or Dict
                 with status code and error message if lock not found.
        :rtype: Union[RelukkoDTO, Dict]
        """
        url = f"{self.base_url}/v1/locks/{lock_id}"
        return self._make_request(url, "GET")

    @skip_http_call()
    def get_locks(self) -> Union[List[RelukkoDTO], Dict]:
        """Retrieves a list of *all* locks from Relukko.

        :return: A list of lock objects (Relukko DTO), each representing a
                 single lock on success, or Dict with status code and error
                 message.
        :rtype: List[Dict]
        """
        url = f"{self.base_url}/v1/locks/"
        return self._make_request(url, "GET")

    @skip_http_call()
    def update_relukko(
            self, lock_id: str, creator: str=None, expires_at: datetime=None,
        ) -> Union[RelukkoDTO, Dict]:
        """Updates an existing lock in Relukko.

        Updates the ``creator`` and/or ``expires_at`` of an existing lock. If no
        value is provided for one of these fields, the existing value will be
        retained.

        :param lock_id: The ID of the lock to update.
        :type lock_id: str
        :param creator: The new creator name for the lock, defaults to ``None``.
        :type creator: str, optional
        :param expires_at: The new expiration date and time for the lock,
                           defaults to ``None``.
        :type expires_at: datetime, optional.
        :raises ValueError: If the provided value for ``expires_at`` is not a
                            ``datetime`` object.
        :return: The updated Relukko DTO on success, or Dict with status code
                 and error message if lock not found or JSON parsing fails.
        :rtype: Union[RelukkoDTO, Dict]
        """
        if isinstance(expires_at, datetime):
            expires_at = expires_at.isoformat()
        elif expires_at is not None:
            raise ValueError("has to be datetime!")

        payload = {
            "creator": creator,
            "expires_at": expires_at,
        }
        url = f"{self.base_url}/v1/locks/{lock_id}"
        return self._make_request(url, "PUT", payload)

    @skip_http_call()
    def delete_relukko(self, lock_id: str) -> Union[RelukkoDTO, Dict]:
        """Releases a lock by deleting it from Relukko.
    
        This function permanently removes a lock from the Relukko system,
        releasing the exclusive access to the resource it was protecting.
        In distributed systems, proper lock deletion is critical to prevent
        resource starvation and ensure other processes can acquire locks when
        needed. This method should be called when an operation has completed
        its work with a protected resource or when explicit lock release is
        required before the natural expiration time.

        :param lock_id: The unique identifier of the lock to delete.
        :type lock_id: str
        :return: A Relukko DTO object of the deleted lock on success, or Dict
                 with status code and error message if lock not found or JSON
                 parsing fails.
        :rtype: Union[RelukkoDTO, Dict]
        """
        url = f"{self.base_url}/v1/locks/{lock_id}"
        return self._make_request(url, "DELETE")

    @skip_http_call()
    def keep_relukko_alive(self, lock_id: str) -> Union[RelukkoDTO, Dict]:
        """Maintains an active lock in Relukko by sending a keep-alive signal.

        This function extends the lifetime of an existing lock by 5 minutes from
        current time. This method prevents the lock from expiring. Use it to
        signal that the lock holder is still active and requires continued
        exclusive access to the locked resource.
    
        :param lock_id: The unique identifier of the lock to keep alive.
        :type lock_id: str
        :return: A Relukko DTO object of the updated lock on success, or Dict
                 with status code and error message if lock not found or JSON
                 parsing fails.
        :rtype: Union[RelukkoDTO, Dict]
        """
        url = f"{self.base_url}/v1/locks/{lock_id}/keep_alive"
        return self._make_request(url, "GET")

    @skip_http_call()
    def keep_relukko_alive_put(
        self, lock_id: str, seconds: int) -> Union[RelukkoDTO, Dict]:
        """Extends a lock's expiration time by a custom number of seconds in
        Relukko.

        This function provides granular control over lock lifetime extension by
        allowing the caller to specify an exact number of seconds to keep the
        lock from expiring.  Unlike the ``keep_relukko_alive`` variant which
        uses a fixed 5-minute extension, this method enables dynamic lock
        duration management based on the specific requirements of the holder of
        the lock. Use it to signal that the lock holder is still active for the
        next X seconds and requires continued exclusive access to the locked
        resource.

        :param lock_id: The unique identifier of the lock to extend.
        :type lock_id: str
        :param seconds: The number of seconds to add to the lock's expiration time.
        :type seconds: int
        :return: A Relukko DTO object of the updated lock on success, or Dict
                 with status code and error message if lock not found or JSON
                 parsing fails.
        :rtype: Union[RelukkoDTO, Dict]
        """
        url = f"{self.base_url}/v1/locks/{lock_id}/keep_alive"
        payload = {
            "seconds": seconds
        }
        return self._make_request(url, "PUT", payload)

    @skip_http_call()
    def add_to_expires_at_time(self, lock_id: str) -> Union[RelukkoDTO, Dict]:
        """Extends a lock's expiration time by adding 5 minutes to its current
        expiration timestamp.

        This function provides a mechanism to incrementally extend a lock's
        lifetime based on its existing expiration time rather than the current
        system time. Unlike the ``keep_alive*`` methods which reset expiration
        relative to the current time, this method adds a fixed 5-minute
        interval directly to the lock's current expires_at value. This approach
        is particularly useful when you want to extend a lock's duration while
        preserving the original timing relationship, such as when multiple
        extensions need to accumulate or when coordinating with other
        time-dependent operations.

        :param lock_id: The unique identifier of the lock to extend.
        :type lock_id: str
        :return: A Relukko DTO object of the updated lock on success, or Dict
                 with status code and error message if lock not found or JSON
                 parsing fails.
        :rtype: Union[RelukkoDTO, Dict]
        """
        url = f"{self.base_url}/v1/locks/{lock_id}/add_to_expire_at"
        return self._make_request(url, "GET")

    @skip_http_call()
    def add_to_expires_at_time_put(
        self, lock_id: str, seconds: int) -> Union[RelukkoDTO, Dict]:
        """Extends a lock's expiration time by adding a custom number of
        seconds to its current expiration timestamp.
    
        This function provides granular control over cumulative lock lifetime
        extensions by allowing the caller to specify an exact number of
        seconds to add to the lock's existing expires_at value. Unlike 
        ``keep_alive_put()`` which sets expiration relative to the current
        system time (``NOW()``), this method adds the specified interval
        directly to the lock's current expiration timestamp, enabling
        predictable, accumulating extensions that preserve the original timing
        relationship.

        :param lock_id: The unique identifier of the lock to extend.
        :type lock_id: str
        :param seconds: The number of seconds to add to the lock's expiration
                        time.
        :type seconds: int
        :return: A Relukko DTO object of the updated lock on success, or Dict
                 with status code and error message if lock not found or JSON
                 parsing fails.
        :rtype: Union[RelukkoDTO, Dict]
        """
        url = f"{self.base_url}/v1/locks/{lock_id}/add_to_expire_at"
        payload = {
            "seconds": seconds
        }
        return self._make_request(url, "PUT", payload)
