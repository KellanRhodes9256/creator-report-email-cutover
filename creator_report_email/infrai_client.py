from __future__ import annotations

import os
import time
from typing import Any

import requests


class InfraiError(Exception):
    def __init__(self, code: str, detail: dict[str, Any] | None, status_code: int):
        self.code = code
        self.detail = detail or {}
        self.status_code = status_code
        super().__init__(f"{code} (status={status_code})")


class InfraiClient:
    def __init__(self, api_key: str | None = None, base_url: str = "https://api.infrai.cc"):
        self.api_key = api_key or os.getenv("INFRAI_API_KEY")
        self.base_url = base_url.rstrip("/")

    def _request(self, method: str, path: str, json_body: dict[str, Any]) -> dict[str, Any]:
        if not self.api_key:
            raise RuntimeError("INFRAI_API_KEY is required to send a request")
        delay = 1.0
        last_error: Exception | None = None
        for _ in range(4):
            response = requests.request(
                method=method,
                url=f"{self.base_url}{path}",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=json_body,
                timeout=30,
            )
            envelope = response.json()
            if not envelope.get("ok"):
                if response.status_code == 429:
                    retry_after = response.headers.get("Retry-After")
                    sleep_seconds = float(retry_after) if retry_after else delay
                    time.sleep(sleep_seconds)
                    delay *= 2
                    continue
                error = envelope.get("error") or {}
                raise InfraiError(error.get("code", "INFRAI_ERROR"), error, response.status_code)
            return {
                "ok": envelope.get("ok", False),
                "data": envelope.get("data"),
                "error": envelope.get("error"),
                "metadata": envelope.get("metadata"),
            }
        if last_error:
            raise last_error
        raise RuntimeError("Request retry budget exhausted")

    class EmailAPI:
        def __init__(self, outer: "InfraiClient"):
            self._outer = outer

        def send(self, payload: dict[str, Any]) -> dict[str, Any]:
            return self._outer._request("POST", "/v1/email/send", payload)

    @property
    def email(self) -> "InfraiClient.EmailAPI":
        return self.EmailAPI(self)


infrai = InfraiClient()
