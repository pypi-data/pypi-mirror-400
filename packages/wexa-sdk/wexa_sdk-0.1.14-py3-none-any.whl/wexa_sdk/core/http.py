from __future__ import annotations
import json
import time
from typing import Any, Dict, Optional

import httpx

RETRY_STATUS = {429, 500, 502, 503, 504}

class ApiError(Exception):
    def __init__(self, status: int, detail: Optional[str] = None, code: Optional[str] = None, request_id: Optional[str] = None, raw: Any = None):
        super().__init__(detail or f"API Error {status}")
        self.status = status
        self.code = code
        self.detail = detail
        self.request_id = request_id
        self.raw = raw

class HttpClient:
    def __init__(self, base_url: str, api_key: str, user_agent: Optional[str] = None, timeout: Optional[dict] = None, retries: Optional[dict] = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.bearer_token: Optional[str] = None
        self.user_agent = user_agent
        self.timeout = {
            "connectTimeoutMs": (timeout or {}).get("connectTimeoutMs", 5000),
            "readTimeoutMs": (timeout or {}).get("readTimeoutMs", 30000),
        }
        self.retries = {
            "attempts": (retries or {}).get("attempts", 3),
            "baseDelayMs": (retries or {}).get("baseDelayMs", 500),
            "maxDelayMs": (retries or {}).get("maxDelayMs", 30000),
        }
        self.cookies: Dict[str, str] = {}
        self._client = httpx.Client(timeout=self.timeout["readTimeoutMs"] / 1000)

    def set_bearer_token(self, token: str):
        self.bearer_token = token

    def set_api_key(self, api_key: str):
        self.api_key = api_key

    def request(self, method: str, path: str, *, params: Optional[Dict[str, Any]] = None, json: Any = None, headers: Optional[Dict[str, str]] = None, return_headers_and_cookies: bool = False):
        url = f"{self.base_url}{path}"
        hdrs = {
            "content-type": "application/json",
            "X-Wexa-SDK-Version": "py/0.1.14",
        }
        if self.api_key:
            hdrs["x-api-key"] = self.api_key
        elif self.bearer_token:
            hdrs["Authorization"] = f"Bearer {self.bearer_token}"

        if self.user_agent:
            hdrs["User-Agent"] = self.user_agent
        if headers:
            hdrs.update(headers)

        req_id = headers.get("x-client-request-id") if headers else None
        if not req_id:
            req_id = str(int(time.time() * 1000))
        hdrs["x-client-request-id"] = req_id

        attempt = 0
        last_err: Optional[Exception] = None
        while attempt < self.retries["attempts"]:
            try:
                resp = self._client.request(method, url, params=params, json=json, headers=hdrs)
                res_req_id = resp.headers.get("x-request-id") or req_id
                
                # Update cookies if present in response
                if "set-cookie" in resp.headers:
                    # Simple parsing, httpx handles this better if using a session but we're stateless-ish
                    # We'll just pass the full set-cookie header if needed by caller, or let caller handle it.
                    # Actually, for login we need the cookies.
                    pass 

                text = resp.text
                try:
                    data = resp.json() if text else None
                except Exception:
                    data = text
                if not resp.is_success:
                    detail = (isinstance(data, dict) and (data.get("detail") or data.get("error") or data.get("message"))) or text or f"HTTP {resp.status_code}"
                    if resp.status_code in RETRY_STATUS and attempt < self.retries["attempts"] - 1:
                        time.sleep(self._backoff(attempt) / 1000)
                        attempt += 1
                        continue
                    raise ApiError(status=resp.status_code, detail=detail, request_id=res_req_id, raw=data)
                
                if return_headers_and_cookies:
                    return data, resp.headers, resp.cookies
                return data
            except ApiError:
                raise
            except Exception as e:  # network error
                last_err = e
                if attempt < self.retries["attempts"] - 1:
                    time.sleep(self._backoff(attempt) / 1000)
                    attempt += 1
                    continue
                raise ApiError(status=0, detail=str(e), request_id=req_id, raw=e)
        raise last_err  # type: ignore

    def _backoff(self, attempt: int) -> int:
        import random
        jitter = random.random() * 0.2 + 0.9
        delay = min(self.retries["maxDelayMs"], int(self.retries["baseDelayMs"] * (2 ** attempt)))
        return int(delay * jitter)
