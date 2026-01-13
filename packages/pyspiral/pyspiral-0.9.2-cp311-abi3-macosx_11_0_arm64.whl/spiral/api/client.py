from __future__ import annotations

import logging
import time
from collections.abc import Iterable, Iterator, Mapping
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from typing import Any, Generic, TypeVar

import httpx
from httpx import HTTPStatusError
from pydantic import BaseModel, Field, TypeAdapter

from spiral.core.authn import Authn

log = logging.getLogger(__name__)


E = TypeVar("E")


class PagedRequest(BaseModel):
    page_token: str | None = None
    page_size: int = 50


class PagedResponse(BaseModel, Generic[E]):
    items: list[E] = Field(default_factory=list)
    next_page_token: str | None = None


PagedReqT = TypeVar("PagedReqT", bound=PagedRequest)


class Paged(Iterable[E], Generic[E]):
    def __init__(
        self,
        client: _Client,
        path: str,
        page_token: str | None,
        page_size: int | None,
        response_cls: type[PagedResponse[E]],
        params: Mapping[str, str] | None = None,
    ):
        self._client = client
        self._path = path
        self._response_cls = response_cls

        self._page_size = page_size

        self._params = params or {}
        if page_token is not None:
            self._params["page_token"] = str(page_token)
        if page_size is not None:
            self._params["page_size"] = str(page_size)

        self._response: PagedResponse[E] = client.get(path, response_cls, params=self._params)

    @property
    def page(self) -> PagedResponse[E]:
        return self._response

    def _fetch_next_page(self):
        assert self._response.next_page_token

        params = self._params.copy()
        params["page_token"] = self._response.next_page_token
        self._response = self._client.get(self._path, self._response_cls, params=params)

    def __iter__(self) -> Iterator[E]:
        while True:
            yield from self._response.items

            if self._response.next_page_token is None:
                break

            self._fetch_next_page()


class ServiceBase:
    def __init__(self, client: _Client):
        self.client = client


class SpiralHTTPError(Exception):
    def __init__(self, body: str, code: int):
        super().__init__(body)
        self.body = body
        self.code = code


class _Client:
    RequestT = TypeVar("RequestT")
    ResponseT = TypeVar("ResponseT")

    def __init__(self, http: httpx.Client, authn: Authn):
        self.http = http
        self.authn = authn

    def _handle_deprecation(self, response: httpx.Response, path: str) -> None:
        """Handle deprecation headers from API responses.

        - Logs warnings if the endpoint is deprecated
        - Sleeps progressively longer as sunset date approaches
        - Logs errors if past the sunset date
        """
        deprecation_header = response.headers.get("Deprecation")
        sunset_header = response.headers.get("Sunset")

        if not deprecation_header:
            return

        try:
            deprecation_date = parsedate_to_datetime(deprecation_header)
            sunset_date = parsedate_to_datetime(sunset_header) if sunset_header else None
        except (ValueError, TypeError):
            log.warning("Failed to parse deprecation headers for path %s", path)
            return

        sunset_str = sunset_date.isoformat() if sunset_date else "unknown"
        log.warning(
            "SpiralDB is using a deprecated API endpoint, please migrate to a supported version "
            "(path=%s, deprecation_date=%s, sunset_date=%s)",
            path,
            deprecation_date.isoformat(),
            sunset_str,
        )

        if sunset_date:
            now = datetime.now(UTC)

            if now > sunset_date:
                # Past sunset date - log error and use maximum sleep
                days_past_sunset = (now - sunset_date).days
                log.error(
                    "SpiralDB API endpoint has been sunset, please migrate to a supported version "
                    "(path=%s, sunset_date=%s, days_past_sunset=%d)",
                    path,
                    sunset_date.isoformat(),
                    days_past_sunset,
                )
                sleep_ms = 5000  # Max sleep after sunset
            else:
                # Before sunset - calculate progressive sleep
                time_until_sunset = (sunset_date - now).total_seconds()
                time_since_deprecation = (now - deprecation_date).total_seconds()
                total_deprecation_window = max((sunset_date - deprecation_date).total_seconds(), 1.0)

                # Calculate progress: 0.0 (just deprecated) to 1.0 (at sunset)
                progress = max(0.0, min(1.0, time_since_deprecation / total_deprecation_window))

                # Exponential backoff: 0ms → 5000ms as we approach sunset
                sleep_ms = int((progress**2) * 5000.0)

                if sleep_ms > 0:
                    days_until_sunset = int(time_until_sunset / 86400) + 1
                    log.warning(
                        "Sleeping due to deprecated endpoint usage (path=%s, sleep_ms=%d, days_until_sunset=%d)",
                        path,
                        sleep_ms,
                        days_until_sunset,
                    )

            if sleep_ms > 0:
                time.sleep(sleep_ms / 1000.0)

    def get(
        self, path: str, response_cls: type[ResponseT], *, params: Mapping[str, str | list[str]] | None = None
    ) -> ResponseT:
        return self.request("GET", path, None, response_cls, params=params)

    def post(
        self,
        path: str,
        req: RequestT,
        response_cls: type[ResponseT],
        *,
        params: Mapping[str, str | list[str]] | None = None,
    ) -> ResponseT:
        return self.request("POST", path, req, response_cls, params=params)

    def put(
        self,
        path: str,
        req: RequestT,
        response_cls: type[ResponseT],
        *,
        params: Mapping[str, str | list[str]] | None = None,
    ) -> ResponseT:
        return self.request("PUT", path, req, response_cls, params=params)

    def delete(
        self, path: str, response_cls: type[ResponseT], *, params: Mapping[str, str | list[str]] | None = None
    ) -> ResponseT:
        return self.request("DELETE", path, None, response_cls, params=params)

    def request(
        self,
        method: str,
        path: str,
        req: RequestT | None,
        response_cls: type[ResponseT],
        *,
        params: Mapping[str, str | list[str]] | None = None,
    ) -> ResponseT:
        req_data: dict[str, Any] = {}
        if req is not None:
            req_data = dict(json=TypeAdapter(req.__class__).dump_python(req, mode="json", exclude_none=True))

        token = self.authn.token()
        resp = self.http.request(
            method,
            path,
            params=params or {},
            headers={"Authorization": f"Bearer {token.expose_secret()}"} if token else None,
            **req_data,
        )

        # Handle deprecation headers before processing response
        self._handle_deprecation(resp, path)

        try:
            resp.raise_for_status()
        except HTTPStatusError as e:
            # Enrich the exception with the response body
            raise SpiralHTTPError(body=resp.text, code=resp.status_code) from e

        if response_cls == type[None]:
            return None

        return TypeAdapter(response_cls).validate_python(resp.json())

    def paged(
        self,
        path: str,
        response_cls: type[PagedResponse[E]],
        *,
        page_token: str | None = None,
        page_size: int | None = None,
        params: Mapping[str, str] | None = None,
    ) -> Paged[E]:
        # TODO(DK): When paging is uniformly supported, set a default page size *here* rather than in the callers.
        return Paged(self, path, page_token, page_size, response_cls, params)
