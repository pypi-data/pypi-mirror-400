from contextlib import asynccontextmanager
import logging
import time
from types import SimpleNamespace
from typing import AsyncGenerator, Optional, Tuple, Unpack

import aiohttp
from aiohttp import ClientResponse
from aiohttp.client import _RequestOptions  # type: ignore

from tooi import USER_AGENT

logger = logging.getLogger(__name__)


class APIError(Exception):
    """Represents an error response from the API."""

    def __init__(self, message: str | None = None, cause: Exception | None = None):
        assert message or cause
        self.message = message or str(cause)
        self.cause = cause
        super().__init__(self.message)


class ResponseError(APIError):
    """Raised when the API returns a response with status code >= 400."""

    def __init__(self, status_code: int, error: str | None, description: str | None):
        self.status_code = status_code
        self.error = error
        self.description = description

        msg = f"HTTP {status_code}"
        msg += f". Error: {error}" if error else ""
        msg += f". Description: {description}" if description else ""
        super().__init__(msg)


def _create_client_session(
    *,
    base_url: str | None = None,
    access_token: str | None = None,
):
    headers = {"User-Agent": USER_AGENT}

    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"

    return aiohttp.ClientSession(
        base_url=base_url,
        trace_configs=[logger_trace_config()],
        headers=headers,
    )


_session: aiohttp.ClientSession | None = None


def get_session():
    """Returns an authenticated session to interact with the logged in instance"""
    global _session
    if not _session:
        from tooi.credentials import get_active_credentials

        application, account = get_active_credentials()
        _session = _create_client_session(
            base_url=application.base_url,
            access_token=account.access_token,
        )

    return _session


async def resolve_streaming_url(path: str) -> str | None:
    """
    Sometimes streaming urls redirect to another host (e.g. on mastodon.social),
    returns the resolved URL to the streaming host matching the given streaming
    path, like '/api/v1/streaming/user/notification'.

    Returns None if the streaming URL cannot be resolved.
    """
    session = get_session()

    async with session.get(path, allow_redirects=False) as response:
        if 200 <= response.status < 300:
            return str(response.url)
        elif 300 <= response.status < 400:
            if url := response.headers.get("location"):
                return url
            else:
                logger.error("Cannot determine redirect url, canceling streaming")
        else:
            logger.error("Cannot determine redirect url, canceling streaming")
    return None


async def stream_sse(path: str) -> AsyncGenerator[str, None]:
    """
    Stream server-sent events for a given streaming path, e.g.
    `/api/v1/streaming/user/notification`.

    Yields received lines. Does not do any parsing.

    Docs:
    https://docs.joinmastodon.org/methods/streaming/#http
    """
    from tooi.credentials import get_active_credentials

    _, account = get_active_credentials()
    streaming_url = await resolve_streaming_url(path)

    if not streaming_url:
        return

    async with _create_client_session(access_token=account.access_token) as session:
        async with session.get(streaming_url) as response:
            response.raise_for_status()
            async for line_bytes in response.content:
                line = line_bytes.decode()
                logger.debug(f"<<< {line}")
                yield line


async def close_session():
    """Close the session if active"""
    global _session
    if _session:
        await _session.close()
        _session = None


async def request(method: str, url: str, **kwargs: Unpack[_RequestOptions]) -> ClientResponse:
    session = get_session()

    try:
        async with session.request(method, url, **kwargs) as response:
            if response.ok:
                await response.read()
                return response
            else:
                error, description = await get_error(response)
                raise ResponseError(response.status, error, description)
    except aiohttp.ClientError as exc:
        logger.error(f"<-- {method} {url} Exception: {str(exc)}")
        logger.exception(exc)
        raise APIError(cause=exc)


async def anon_request(method: str, url: str, **kwargs: Unpack[_RequestOptions]) -> ClientResponse:
    try:
        async with _create_client_session() as session:
            async with session.request(method, url, **kwargs) as response:
                if response.ok:
                    await response.read()
                    return response
                else:
                    error, description = await get_error(response)
                    raise ResponseError(response.status, error, description)
    except aiohttp.ClientError as exc:
        logger.error(f"<-- {method} {url} Exception: {str(exc)}")
        logger.exception(exc)
        raise APIError(cause=exc)


async def get_error(response: ClientResponse) -> Tuple[Optional[str], Optional[str]]:
    """Attempt to extract the error and error description from response body.

    See: https://docs.joinmastodon.org/entities/error/
    """
    try:
        data = await response.json()
        return data.get("error"), data.get("error_description")
    except Exception:
        return None, None


def logger_trace_config() -> aiohttp.TraceConfig:
    async def on_request_start(
        session: aiohttp.ClientSession,
        context: SimpleNamespace,
        params: aiohttp.TraceRequestStartParams,
    ):
        context.start = time.monotonic()
        logger.info(f"--> {params.method} {params.url}")

    async def on_request_redirect(
        session: aiohttp.ClientSession,
        context: SimpleNamespace,
        params: aiohttp.TraceRequestRedirectParams,
    ):
        logger.info(f"--> redirected to {params.method} {params.url}")

    async def on_request_end(
        session: aiohttp.ClientSession,
        context: SimpleNamespace,
        params: aiohttp.TraceRequestEndParams,
    ):
        elapsed = round(1000 * (time.monotonic() - context.start))
        logger.info(f"<-- {params.method} {params.url} HTTP {params.response.status} {elapsed}ms")

    trace_config = aiohttp.TraceConfig()
    trace_config.on_request_start.append(on_request_start)
    trace_config.on_request_end.append(on_request_end)
    trace_config.on_request_redirect.append(on_request_redirect)
    return trace_config
