import logging
import time
import ssl
import socket
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict

import pytest
import requests
from requests_mock import ANY
from requests.adapters import HTTPAdapter
from requests.cookies import cookiejar_from_dict
from urllib3.util import parse_url

from pyrelukko import RelukkoClient, RelukkoDTO
from pyrelukko.decorators import retry
from pyrelukko.relukko_client import RelukkoDoRetry


SCRIPT_DIR = Path(__file__).parent.absolute()

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)


@retry(None, ConnectionRefusedError)
def _check_tls(ssl_ctx: ssl.SSLContext, port):
    with socket.create_connection(("127.0.0.1", port)) as sock:
        with ssl_ctx.wrap_socket(sock, server_hostname="relukko") as ssock:
            response = ssock.recv(20)
            assert response == b"Hello, TLS Client!"


def _check_has_serial_no(ssl_ctx: ssl.SSLContext):
    serial_numbers = [x["serialNumber"] for x in ssl_ctx.get_ca_certs()]
    assert "4573816C13FE0529EAD797EAB28DFED16930B76B" in serial_numbers


def test_init_relukko_client():
    relukko = RelukkoClient(base_url="", api_key="")

    assert isinstance(relukko, RelukkoClient)
    assert relukko.session.trust_env == True
    assert relukko.session.cookies._cookies == {}
    assert relukko.ssl_ctx is None
    http_adapter: HTTPAdapter = relukko.session.adapters.get("http://")
    assert http_adapter.max_retries.total == 0
    assert http_adapter.max_retries.connect is None
    assert http_adapter.max_retries.read == False
    assert http_adapter.max_retries.redirect is None
    assert http_adapter.max_retries.status is None
    assert http_adapter.max_retries.other is None
    assert http_adapter.max_retries.backoff_factor == 0
    assert http_adapter.max_retries.backoff_max == 120
    assert http_adapter.max_retries.backoff_jitter == 0.0
    assert http_adapter.max_retries.raise_on_redirect == True
    assert http_adapter.max_retries.raise_on_status == True
    assert relukko.tries == 4
    assert relukko.delay == 5
    assert relukko.backoff == 2.0
    assert relukko.max_delay is None
    assert relukko.exceptions == (requests.ConnectionError, RelukkoDoRetry)
    assert relukko.ws_wait_for_timeout == 2
    assert relukko.ws_ping_interval == 60
    assert relukko.ws_ping_timeout == 20
    assert relukko.acquire_wait_for_timeout == 2
    assert relukko.acquire_modulo == 100
    assert relukko.disable_websocket == False
    assert relukko.raise_when_acquire_fails == True

    with pytest.raises(ValueError):
        RelukkoClient(base_url=1000, api_key="")

def test_init_relukko_client_with_env_var(tls_listener):
    _, port = tls_listener

    capath = SCRIPT_DIR / "cert"
    cafile = capath / "rootCA.crt"

    pytest.MonkeyPatch().setenv("REQUESTS_CA_BUNDLE", str(cafile.absolute()))
    relukko = RelukkoClient(base_url="https://relukko", api_key="")
    pytest.MonkeyPatch().delenv("REQUESTS_CA_BUNDLE")
    _check_tls(relukko.ssl_ctx, port)
    _check_has_serial_no(relukko.ssl_ctx)

    pytest.MonkeyPatch().setenv("CURL_CA_BUNDLE", str(cafile.absolute()))
    relukko2 = RelukkoClient(base_url="https://relukko", api_key="")
    pytest.MonkeyPatch().delenv("CURL_CA_BUNDLE")
    _check_tls(relukko2.ssl_ctx, port)
    _check_has_serial_no(relukko2.ssl_ctx)

    pytest.MonkeyPatch().setenv("REQUESTS_CA_BUNDLE", str(capath.absolute()))
    relukko3 = RelukkoClient(base_url="https://relukko", api_key="")
    pytest.MonkeyPatch().delenv("REQUESTS_CA_BUNDLE")
    _check_tls(relukko3.ssl_ctx, port)
    _check_has_serial_no(relukko3.ssl_ctx)

    pytest.MonkeyPatch().setenv("CURL_CA_BUNDLE", str(capath.absolute()))
    relukko4 = RelukkoClient(base_url="https://relukko", api_key="")
    pytest.MonkeyPatch().delenv("CURL_CA_BUNDLE")
    _check_tls(relukko4.ssl_ctx, port)
    _check_has_serial_no(relukko4.ssl_ctx)


def test_init_relukko_client_with_cafile(tls_listener):
    _, port = tls_listener

    cafile = SCRIPT_DIR / "cert" / "rootCA.crt"

    relukko = RelukkoClient(
        base_url="https://relukko", api_key="", cafile=cafile)
    _check_tls(relukko.ssl_ctx, port)
    _check_has_serial_no(relukko.ssl_ctx)


def test_init_relukko_client_with_capath(tls_listener):
    _, port = tls_listener

    capath = SCRIPT_DIR / "cert"

    relukko = RelukkoClient(
        base_url="https://relukko", api_key="", capath=capath)
    _check_tls(relukko.ssl_ctx, port)
    _check_has_serial_no(relukko.ssl_ctx)


def test_init_relukko_client_with_cadata(tls_listener):
    _, port = tls_listener

    cafile = SCRIPT_DIR / "cert" / "rootCA.crt"
    cadata = cafile.read_text()

    relukko = RelukkoClient(
        base_url="https://relukko", api_key="", cadata=cadata)
    _check_tls(relukko.ssl_ctx, port)
    _check_has_serial_no(relukko.ssl_ctx)

    cader = SCRIPT_DIR / "cert" / "rootCA.der"
    cadata = cader.read_bytes()

    relukko2 = RelukkoClient(
        base_url="https://relukko", api_key="", cadata=cadata)
    _check_tls(relukko2.ssl_ctx, port)
    _check_has_serial_no(relukko2.ssl_ctx)


def test_check_tls_throws_error(tls_listener):
    _, port = tls_listener

    relukko = RelukkoClient(
        base_url="https://relukko", api_key="")
    with pytest.raises(ssl.SSLCertVerificationError):
        _check_tls(relukko.ssl_ctx, port)


def test_reconfigure_relukko_client():
    relukko = RelukkoClient(base_url="", api_key="")

    relukko.reconfigure_relukko(
        "https://relukko", api_key="secret-key")

    assert relukko.base_url == parse_url("https://relukko")
    assert relukko.ws_url == parse_url("wss://relukko/ws/broadcast")
    assert relukko.session.headers['X-api-Key'] == "secret-key"

    default_ctx = ssl.create_default_context()
    assert relukko.ssl_ctx.check_hostname == default_ctx.check_hostname
    assert relukko.ssl_ctx.hostname_checks_common_name == \
        default_ctx.hostname_checks_common_name
    assert relukko.ssl_ctx.keylog_filename == default_ctx.keylog_filename
    assert relukko.ssl_ctx.sni_callback == default_ctx.sni_callback
    assert relukko.ssl_ctx.verify_flags == default_ctx.verify_flags
    assert relukko.ssl_ctx.verify_mode == default_ctx.verify_mode
    assert relukko.ssl_ctx.options == default_ctx.options
    assert relukko.tries == 4
    assert relukko.delay == 5
    assert relukko.backoff == 2.0
    assert relukko.max_delay is None
    assert relukko.exceptions == (requests.ConnectionError, RelukkoDoRetry)
    assert relukko.ws_wait_for_timeout == 2
    assert relukko.ws_ping_interval == 60
    assert relukko.ws_ping_timeout == 20
    assert relukko.acquire_wait_for_timeout == 2
    assert relukko.acquire_modulo == 100
    assert relukko.disable_websocket == False
    assert relukko.raise_when_acquire_fails == True


def test_reconfigure_relukko_client_extended():
    relukko = RelukkoClient(base_url="", api_key="")

    cookies = cookiejar_from_dict({"cookie1": "value1"})
    verify_mode = ssl.VerifyMode.CERT_NONE
    verify_flags = ssl.VerifyFlags.VERIFY_DEFAULT
    options = ssl.Options.OP_ALL
    ws_wait_for_timeout = 27
    ws_ping_interval = 600
    ws_ping_timeout = 23
    acquire_wait_for_timeout = 22
    acquire_modulo = 202

    relukko.reconfigure_relukko(
        base_url="https://relukko", api_key="my-API-key", trust_env=False,
        cookies=cookies, total=100, connect=99, read=98, redirect=97,
        status=96, other=95, backoff_factor=94, backoff_max=1000,
        backoff_jitter=93, raise_on_redirect=False, raise_on_status=False,
        check_hostname=False, hostname_checks_common_name=False,
        verify_mode=verify_mode, verify_flags=verify_flags, options=options,
        ws_wait_for_timeout=ws_wait_for_timeout, acquire_modulo=acquire_modulo,
        ws_ping_interval=ws_ping_interval, ws_ping_timeout=ws_ping_timeout,
        acquire_wait_for_timeout=acquire_wait_for_timeout,
        disable_websocket=True, raise_when_acquire_fails=False,
    )

    assert relukko.session.trust_env == False
    assert relukko.session.cookies == cookies
    assert relukko.base_url == parse_url("https://relukko")
    assert relukko.ws_url == parse_url("wss://relukko/ws/broadcast")
    assert relukko.session.headers['X-api-Key'] == "my-API-key"
    http_adapter: HTTPAdapter = relukko.session.adapters.get("http://")
    assert http_adapter.max_retries.total == 100
    assert http_adapter.max_retries.connect == 99
    assert http_adapter.max_retries.read == 98
    assert http_adapter.max_retries.redirect == 97
    assert http_adapter.max_retries.status == 96
    assert http_adapter.max_retries.other == 95
    assert http_adapter.max_retries.backoff_factor == 94.0
    assert http_adapter.max_retries.backoff_max == 1000.0
    assert http_adapter.max_retries.backoff_jitter == 93.0
    assert http_adapter.max_retries.raise_on_redirect == False
    assert http_adapter.max_retries.raise_on_status == False
    assert isinstance(relukko.ssl_ctx, ssl.SSLContext)
    assert relukko.ssl_ctx.check_hostname == False
    assert relukko.ssl_ctx.hostname_checks_common_name == False
    assert relukko.ssl_ctx.keylog_filename is None
    assert relukko.ssl_ctx.sni_callback is None
    assert relukko.ssl_ctx.verify_flags == verify_flags
    assert relukko.ssl_ctx.verify_mode == verify_mode
    assert relukko.ssl_ctx.options == options
    assert relukko.tries == 4
    assert relukko.delay == 5
    assert relukko.backoff == 2.0
    assert relukko.max_delay is None
    assert relukko.exceptions == (requests.ConnectionError, RelukkoDoRetry)
    assert relukko.ws_wait_for_timeout == ws_wait_for_timeout
    assert relukko.ws_ping_interval == ws_ping_interval
    assert relukko.ws_ping_timeout == ws_ping_timeout
    assert relukko.acquire_wait_for_timeout == acquire_wait_for_timeout
    assert relukko.acquire_modulo == acquire_modulo
    assert relukko.disable_websocket == True
    assert relukko.raise_when_acquire_fails == False


def test_init_relukko_client_extented():
    cookies = cookiejar_from_dict({"cookie1": "value1"})
    ws_wait_for_timeout = 27
    ws_ping_interval = 600
    ws_ping_timeout = 23
    acquire_wait_for_timeout = 22
    acquire_modulo = 202

    relukko = RelukkoClient(
        base_url="http://relukko", api_key="my-API-key", trust_env=False,
        cookies=cookies, total=100, connect=99, read=98, redirect=97,
        status=96, other=95, backoff_factor=94, backoff_max=1000,
        backoff_jitter=93, raise_on_redirect=False, raise_on_status=False,
        ws_wait_for_timeout=ws_wait_for_timeout, acquire_modulo=acquire_modulo,
        ws_ping_interval=ws_ping_interval, ws_ping_timeout=ws_ping_timeout,
        acquire_wait_for_timeout=acquire_wait_for_timeout,
        disable_websocket=True, raise_when_acquire_fails=False,
    )

    assert relukko.session.trust_env == False
    assert relukko.session.cookies == cookies
    assert relukko.base_url == parse_url("http://relukko")
    assert relukko.ws_url == parse_url("ws://relukko/ws/broadcast")
    assert relukko.session.headers['X-api-Key'] == "my-API-key"
    assert relukko.ssl_ctx is None
    http_adapter: HTTPAdapter = relukko.session.adapters.get("http://")
    assert http_adapter.max_retries.total == 100
    assert http_adapter.max_retries.connect == 99
    assert http_adapter.max_retries.read == 98
    assert http_adapter.max_retries.redirect == 97
    assert http_adapter.max_retries.status == 96
    assert http_adapter.max_retries.other == 95
    assert http_adapter.max_retries.backoff_factor == 94.0
    assert http_adapter.max_retries.backoff_max == 1000.0
    assert http_adapter.max_retries.backoff_jitter == 93.0
    assert http_adapter.max_retries.raise_on_redirect == False
    assert http_adapter.max_retries.raise_on_status == False
    assert relukko.tries == 4
    assert relukko.delay == 5
    assert relukko.backoff == 2.0
    assert relukko.max_delay is None
    assert relukko.exceptions == (requests.ConnectionError, RelukkoDoRetry)
    assert relukko.ws_wait_for_timeout == ws_wait_for_timeout
    assert relukko.ws_ping_interval == ws_ping_interval
    assert relukko.ws_ping_timeout == ws_ping_timeout
    assert relukko.acquire_wait_for_timeout == acquire_wait_for_timeout
    assert relukko.acquire_modulo == acquire_modulo
    assert relukko.disable_websocket == True
    assert relukko.raise_when_acquire_fails == False


def test_init_relukko_client_ssl_ctx():
    relukko = RelukkoClient(
        base_url="https://relukko", api_key="my-API-key",
    )

    default_ctx = ssl.create_default_context()

    assert isinstance(relukko.ssl_ctx, ssl.SSLContext)
    assert relukko.ssl_ctx.check_hostname == default_ctx.check_hostname
    assert relukko.ssl_ctx.hostname_checks_common_name == \
        default_ctx.hostname_checks_common_name
    assert relukko.ssl_ctx.keylog_filename == default_ctx.keylog_filename
    assert relukko.ssl_ctx.sni_callback == default_ctx.sni_callback
    assert relukko.ssl_ctx.verify_flags == default_ctx.verify_flags
    assert relukko.ssl_ctx.verify_mode == default_ctx.verify_mode
    assert relukko.ssl_ctx.options == default_ctx.options
    assert relukko.tries == 4
    assert relukko.delay == 5
    assert relukko.backoff == 2.0
    assert relukko.max_delay is None
    assert relukko.exceptions == (requests.ConnectionError, RelukkoDoRetry)


def test_init_relukko_client_ssl_ctx_extended():
    verify_mode = ssl.VerifyMode.CERT_NONE
    verify_flags = ssl.VerifyFlags.VERIFY_DEFAULT
    options = ssl.Options.OP_ALL

    relukko = RelukkoClient(
        base_url="https://relukko", api_key="my-API-key", check_hostname=False,
        hostname_checks_common_name=False, verify_mode=verify_mode,
        verify_flags=verify_flags, options=options
    )
    assert isinstance(relukko.ssl_ctx, ssl.SSLContext)
    assert relukko.ssl_ctx.check_hostname == False
    assert relukko.ssl_ctx.hostname_checks_common_name == False
    assert relukko.ssl_ctx.keylog_filename is None
    assert relukko.ssl_ctx.sni_callback is None
    assert relukko.ssl_ctx.verify_flags == verify_flags
    assert relukko.ssl_ctx.verify_mode == verify_mode
    assert relukko.ssl_ctx.options == options
    assert relukko.tries == 4
    assert relukko.delay == 5
    assert relukko.backoff == 2.0
    assert relukko.max_delay is None
    assert relukko.exceptions == (requests.ConnectionError, RelukkoDoRetry)


def test_init_relukko_client_retry():

    exceptions = (
        ValueError,
        ConnectionRefusedError,
        ConnectionResetError,
    )

    relukko = RelukkoClient(
        base_url="", api_key="", tries=100, delay=99, backoff=98.7,
        max_delay=97, exceptions=exceptions)

    assert relukko.tries == 100
    assert relukko.delay == 99
    assert relukko.backoff == 98.7
    assert relukko.max_delay == 97
    assert relukko.exceptions == exceptions


def test_reconfigre_relukko_client_retry():
    relukko = RelukkoClient(base_url="", api_key="")

    exceptions = (
        ValueError,
        ConnectionRefusedError,
        ConnectionResetError,
    )

    relukko.reconfigure_relukko(
        tries=100, delay=99, backoff=98.7,
        max_delay=97, exceptions=exceptions)

    assert relukko.tries == 100
    assert relukko.delay == 99
    assert relukko.backoff == 98.7
    assert relukko.max_delay == 97
    assert relukko.exceptions == exceptions


def test_aqcuire_http_status_code_400_with_raise(requests_mock):
    requests_mock.register_uri(
        ANY,
        ANY,
        status_code=400,
        reason="Bad Request",
        json={"status": 400, "message": "Bad Request"},
    )

    relukko = RelukkoClient(
        base_url="http://relukko", api_key="key",
        delay=1, backoff=1.01, disable_websocket=True,
    )
    with pytest.raises(requests.HTTPError):
        relukko.acquire_relukko("400Lock", "PyTest", 300)


def test_aqcuire_http_status_code_400_without_raise(requests_mock):
    requests_mock.register_uri(
        ANY,
        ANY,
        status_code=400,
        reason="Bad Request",
        json={"status": 400, "message": "Bad Request"},
    )

    relukko = RelukkoClient(
        base_url="http://relukko", api_key="key",disable_websocket=True,
        delay=1, backoff=1.01, raise_when_acquire_fails=False,
    )
    lock = relukko.acquire_relukko("500Lock", "PyTest", 300)
    assert isinstance(lock, requests.exceptions.HTTPError)


def test_aqcuire_http_status_code_418_with_raise(requests_mock):
    requests_mock.register_uri(
        ANY,
        ANY,
        status_code=418,
        reason="I'm a teapot",
        text="The server refuses the attempt to brew coffee with a teapot.",
    )

    relukko = RelukkoClient(
        base_url="http://relukko", api_key="key",
        delay=1, backoff=1.01, disable_websocket=True,
    )
    with pytest.raises(RuntimeError):
        relukko.acquire_relukko("418Lock", "PyTest", 300)


def test_aqcuire_http_status_code_418_without_raise(requests_mock):
    requests_mock.register_uri(
        ANY,
        ANY,
        status_code=418,
        reason="I'm a teapot",
        text="The server refuses the attempt to brew coffee with a teapot.",
    )

    relukko = RelukkoClient(
        base_url="http://relukko", api_key="key",disable_websocket=True,
        delay=1, backoff=1.01, raise_when_acquire_fails=False,
    )
    lock = relukko.acquire_relukko("418Lock", "PyTest", 300)
    assert isinstance(lock, RuntimeError)


def test_aqcuire_http_status_code_500_with_raise(requests_mock):
    requests_mock.register_uri(
        ANY,
        ANY,
        status_code=500,
        reason="Internal Server Error",
    )

    relukko = RelukkoClient(
        base_url="http://relukko", api_key="key",
        delay=1, backoff=1.01, disable_websocket=True,
    )
    with pytest.raises(RelukkoDoRetry):
        relukko.acquire_relukko("500Lock", "PyTest", 300)


def test_aqcuire_http_status_code_500_without_raise(requests_mock):
    requests_mock.register_uri(
        ANY,
        ANY,
        status_code=500,
        reason="Internal Server Error",
    )

    relukko = RelukkoClient(
        base_url="http://relukko", api_key="key",disable_websocket=True,
        delay=1, backoff=1.01, raise_when_acquire_fails=False,
    )
    lock = relukko.acquire_relukko("500Lock", "PyTest", 300)
    assert isinstance(lock, RelukkoDoRetry)


def test_aqcuire_relukko_retry_with_max_delay(requests_mock, caplog):
    requests_mock.register_uri(
        ANY,
        ANY,
        status_code=500,
        reason="Internal Server Error",
    )

    relukko = RelukkoClient(
        base_url="http://relukko", api_key="key",disable_websocket=True,
        delay=1, backoff=3, raise_when_acquire_fails=False,
        max_delay=2,
    )

    lock = relukko.acquire_relukko("MaxDelayLock", "PyTest", 300)

    one_sec_count = 0
    two_sec_count = 0
    for record in caplog.records:
        if "Retrying in 2 seconds..." in record.message:
            two_sec_count += 1
        elif "Retrying in 1 seconds..." in record.message:
            one_sec_count += 1

    assert one_sec_count == 1
    assert two_sec_count == 2
    assert isinstance(lock, RelukkoDoRetry)


def test_get_relukko_retry_400(requests_mock):
    requests_mock.register_uri(
        ANY,
        ANY,
        status_code=400,
        reason="Bad Request",
        json={"status": 400, "message": "Bad Request"},
    )

    relukko = RelukkoClient(
        base_url="http://relukko", api_key="key",disable_websocket=True,
        delay=1, backoff=0.5, raise_when_acquire_fails=False,
    )

    with pytest.raises(requests.HTTPError):
        relukko.get_lock("GetLock400")


def test_get_relukko_retry_418(requests_mock):
    requests_mock.register_uri(
        ANY,
        ANY,
        status_code=418,
        reason="I'm a teapot",
        text="The server refuses the attempt to brew coffee with a teapot.",
    )

    relukko = RelukkoClient(
        base_url="http://relukko", api_key="key",disable_websocket=True,
        delay=1, backoff=0.5, raise_when_acquire_fails=False,
    )

    with pytest.raises(RuntimeError):
        relukko.get_lock("GetLock418")


def test_get_relukko_retry_500(requests_mock):
    requests_mock.register_uri(
        ANY,
        ANY,
        status_code=500,
        reason="Internal Server Error",
    )

    relukko = RelukkoClient(
        base_url="http://relukko", api_key="key",disable_websocket=True,
        delay=1, backoff=0.5, raise_when_acquire_fails=False,
    )

    with pytest.raises(RelukkoDoRetry):
        relukko.get_lock("GetLock500")


def test_acquire_relukko(relukko_backend):
    relukko, _ = relukko_backend

    lock = relukko.acquire_relukko("pylock", "pytest", 10)
    assert isinstance(lock.to_dict(), Dict)
    assert isinstance(lock, RelukkoDTO)
    start_time = time.time()
    none_lock = relukko.acquire_relukko("pylock", "pytest", 30)
    end_time = time.time()
    assert none_lock is None
    assert 29 < end_time - start_time < 37


def test_acquire_relukko_with_del(relukko_backend):
    relukko, _ = relukko_backend
    lock = relukko.acquire_relukko("Pylock", "pytest", 10)
    id = lock['id']

    expires_at = datetime.now(timezone.utc) - timedelta(minutes=2, seconds=45)
    upd_lock = relukko.update_relukko(id, expires_at=expires_at)
    assert isinstance(upd_lock.to_dict(), Dict)
    assert isinstance(upd_lock, RelukkoDTO)
    assert id == upd_lock['id']

    start_time = time.time()
    lock = relukko.acquire_relukko("Pylock", "pytest", 60)
    end_time = time.time()

    assert lock is not None
    assert upd_lock['id'] != lock['id']
    assert 14 < end_time - start_time < 50


def test_delete_relukko(relukko_backend):
    relukko, _ = relukko_backend

    lock = relukko.acquire_relukko("del_lock", "pytest", 10)
    del_lock = relukko.delete_relukko(lock['id'])
    assert isinstance(lock.to_dict(), Dict)
    assert isinstance(lock, RelukkoDTO)
    assert lock == del_lock

    get_lock = relukko.get_lock(lock['id'])
    assert get_lock['status'] == 422

    locks = relukko.get_locks()
    assert lock not in locks


def test_get_relukko(relukko_backend):
    relukko, _ = relukko_backend

    lock = relukko.acquire_relukko("get_lock", "pytest", 10)
    assert isinstance(lock.to_dict(), Dict)

    get_lock = relukko.get_lock(lock['id'])
    assert isinstance(get_lock.to_dict(), Dict)
    assert isinstance(get_lock, RelukkoDTO)
    assert get_lock == lock

    locks = relukko.get_locks()
    assert lock in locks


def test_update_relukko_creator(relukko_backend):
    relukko, _ = relukko_backend

    lock = relukko.acquire_relukko("update_lock", "pytest", 10)
    assert lock['creator'] == "pytest"

    upd_lock = relukko.update_relukko(lock['id'], creator="tsetyp")
    assert upd_lock['creator'] == "tsetyp"

    get_lock = relukko.get_lock(lock['id'])
    assert get_lock['creator'] == "tsetyp"


def test_update_relukko_expires_at(relukko_backend):
    relukko, _ = relukko_backend

    lock = relukko.acquire_relukko("update_lock_exp", "pytest", 10)
    id = lock['id']

    expires_at = datetime.fromisoformat("2099-12-31T12:34:56.789Z")
    upd_lock = relukko.update_relukko(id, expires_at=expires_at)
    assert isinstance(upd_lock.to_dict(), Dict)
    assert isinstance(upd_lock, RelukkoDTO)
    assert upd_lock['expires_at'] == expires_at

    with pytest.raises(ValueError):
        relukko.update_relukko(id, expires_at="2099-12-01T23:12Z")


def test_keep_relukko_alive(relukko_backend):
    relukko, _ = relukko_backend

    lock = relukko.acquire_relukko("keep_me", "pytest", 10)
    id = lock['id']

    start_time = datetime.now(timezone.utc)
    keep_lock = relukko.keep_relukko_alive(id)
    assert isinstance(keep_lock.to_dict(), Dict)
    assert isinstance(keep_lock, RelukkoDTO)
    assert lock['expires_at'] is not keep_lock['expires_at']

    expires_diff = keep_lock.expires_at - start_time
    assert 295 < expires_diff.seconds < 305


def test_keep_relukko_alive_put(relukko_backend):
    relukko, _ = relukko_backend

    lock = relukko.acquire_relukko("keep_me_more", "pytest", 10)
    id = lock['id']

    start_time = datetime.now(timezone.utc)
    keep_lock = relukko.keep_relukko_alive_put(id, 3600)
    assert isinstance(keep_lock.to_dict(), Dict)
    assert isinstance(keep_lock, RelukkoDTO)
    assert lock['expires_at'] is not keep_lock['expires_at']

    expires_diff = keep_lock.expires_at - start_time
    assert 3595 < expires_diff.seconds < 3605


def test_add_to_expires_at_time(relukko_backend):
    relukko, _ = relukko_backend
    lock = relukko.acquire_relukko("add_me_up", "pytest", 10)
    id = lock['id']
    start_expires_at = lock.expires_at

    add_lock = relukko.add_to_expires_at_time(id)
    assert isinstance(add_lock.to_dict(), Dict)
    assert isinstance(add_lock, RelukkoDTO)
    assert lock['expires_at'] is not add_lock['expires_at']

    expires_diff = add_lock.expires_at - start_expires_at
    assert expires_diff.seconds == 300


def test_add_to_expires_at_time_put(relukko_backend):
    relukko, _ = relukko_backend
    lock = relukko.acquire_relukko("add_me_up_more", "pytest", 10)
    id = lock['id']
    start_expires_at = lock.expires_at

    add_lock = relukko.add_to_expires_at_time_put(id, 3600)
    assert isinstance(add_lock.to_dict(), Dict)
    assert isinstance(add_lock, RelukkoDTO)
    assert lock['expires_at'] is not add_lock['expires_at']

    expires_diff = add_lock.expires_at - start_expires_at
    assert expires_diff.seconds == 3600
