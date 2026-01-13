from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.parse import urljoin

import httpx

from casper_client.errors import CasperError, CasperErrorKind, classify_http_error


@dataclass
class _HTTPResult:
    status_code: int
    content: bytes
    headers: httpx.Headers
    reason_phrase: str


class ApiClient:
    """
    Minimal httpx-based transport inspired by qdrant_client.http.ApiClient.
    """

    def __init__(self, host: str, *, timeout: float | None = 30.0, **kwargs: Any) -> None:
        self.host = host
        # Avoid failing on exotic proxy schemes in env (e.g. socks://) unless user opts in.
        if "trust_env" not in kwargs:
            kwargs["trust_env"] = False
        self._client = httpx.Client(timeout=timeout, **kwargs)

    def close(self) -> None:
        self._client.close()

    def _build_url(self, url: str, path_params: dict[str, Any] | None = None) -> str:
        if path_params is None:
            path_params = {}
        host = self.host if self.host.endswith("/") else self.host + "/"
        url = url[1:] if url.startswith("/") else url
        return urljoin(host, url.format(**path_params))

    def request_bytes(
        self,
        *,
        method: str,
        url: str,
        path_params: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> bytes:
        full_url = self._build_url(url, path_params)
        req = self._client.build_request(method, full_url, **kwargs)
        try:
            resp = self._client.send(req)
        except Exception as e:
            raise CasperError(kind=CasperErrorKind.CLIENT, message="request failed", cause=e) from e

        content = resp.content
        if 200 <= resp.status_code < 300:
            return content

        msg = ""
        if content:
            # Casper often returns {"error": "..."}; fall back to raw bytes.
            try:
                parsed = json.loads(content)
                if isinstance(parsed, dict) and isinstance(parsed.get("error"), str) and parsed.get("error"):
                    msg = parsed["error"]
                else:
                    msg = content.decode("utf-8", errors="replace")
            except Exception:
                msg = content.decode("utf-8", errors="replace")

        if not msg:
            msg = resp.reason_phrase or "request failed"

        raise classify_http_error(resp.status_code, msg)

    def request_json(
        self,
        *,
        method: str,
        url: str,
        path_params: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Any:
        raw = self.request_bytes(method=method, url=url, path_params=path_params, **kwargs)
        if raw == b"":
            return None
        try:
            return json.loads(raw)
        except Exception as e:
            raise CasperError(
                kind=CasperErrorKind.INVALID_RESPONSE,
                message=f"failed to parse JSON response: {e}",
                cause=e,
            ) from e


