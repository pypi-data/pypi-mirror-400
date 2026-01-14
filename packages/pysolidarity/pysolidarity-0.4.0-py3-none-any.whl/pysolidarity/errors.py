from typing import Any, Optional
import json
import requests

class SolidarityError(Exception):
    """Base exception for this SDK."""

class HTTPError(SolidarityError):
    def __init__(self, message: str, *, status_code: int, payload: Optional[Any] = None):
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload

class RetryExhausted(Exception):
    """Raised by the client when a retryable request ultimately fails.
    Attributes:
        method, url, status_code, attempts, last_response, last_exception
    """
    def __init__(self, method, url, attempts, last_response=None, last_exception=None):
        self.method = method
        self.url = url
        self.attempts = attempts
        self.response = last_response
        self.status_code = getattr(last_response, "status_code", None)
        self.last_exception = last_exception
        super().__init__(f"Retry exhausted after {attempts} attempts for {method} {url} "
                         f"(status={self.status_code})")


class NotFound(HTTPError):
    pass

class ValidationError(HTTPError):
    pass

class Unauthorized(HTTPError):
    pass

class RateLimited(HTTPError):
    pass

class ServerError(HTTPError):
    pass


def _safe_json(resp: requests.Response):
    try:
        return resp.json()
    except Exception:
        try:
            return json.loads(resp.text)
        except Exception:
            return None


def raise_for_status(resp: requests.Response) -> None:
    if 200 <= resp.status_code < 300:
        return

    payload = _safe_json(resp)
    msg = None
    if isinstance(payload, dict):
        msg = payload.get("error") or payload.get("message")
    msg = msg or f"HTTP {resp.status_code}: {resp.text[:300]}"

    if resp.status_code == 401:
        raise Unauthorized(msg, status_code=resp.status_code, payload=payload)
    if resp.status_code == 404:
        raise NotFound(msg, status_code=resp.status_code, payload=payload)
    if resp.status_code == 422:
        raise ValidationError(msg, status_code=resp.status_code, payload=payload)
    if resp.status_code == 429:
        raise RateLimited(msg, status_code=resp.status_code, payload=payload)
    if resp.status_code >= 500:
        raise ServerError(msg, status_code=resp.status_code, payload=payload)

    raise HTTPError(msg, status_code=resp.status_code, payload=payload)


