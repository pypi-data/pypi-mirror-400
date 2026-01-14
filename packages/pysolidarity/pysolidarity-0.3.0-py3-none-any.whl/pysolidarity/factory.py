import os
from typing import Optional
import requests

from .client import SolidarityClient
from .http import attach_defaults
from .types import TimeoutType

DEFAULT_RPS = 4

def make_client_from_env(
    *,
    session: Optional[requests.Session] = None,
    timeout: TimeoutType = (10, 60),
    user_agent: str = "pysolidarity/0.1",
) -> SolidarityClient:
    return SolidarityClient.from_env(session=session, timeout=timeout, user_agent=user_agent)


def make_rate_limited_client(
    redis_client,
    *,
    namespace: str = "solidarity",
    req_per_sec: int = DEFAULT_RPS,
    timeout: TimeoutType = (10, 60),
    user_agent: str = "pysolidarity/0.1",
) -> SolidarityClient:
    base_url = os.getenv("SOLIDARITY_BASE_URL", "https://api.solidarity.tech")
    api_key = os.getenv("SOLIDARITY_API_KEY")
    if not api_key:
        raise RuntimeError("Missing env: SOLIDARITY_API_KEY")

    try:
        from ratelimit import RedisFixedIntervalGate, RateLimitedSession  # type: ignore
    except Exception as e:
        raise RuntimeError(
            "The optional ratelimit dependency is not available. Install it or use make_client_from_env()."
        ) from e

    rps = max(1, int(req_per_sec))
    gate = RedisFixedIntervalGate(
        redis_client,
        namespace=namespace,
        interval_ms=int(1000 / rps),
    )

    # force Zapier into the UA string
    if "Zapier" not in user_agent:
        user_agent = f"{user_agent} Zapier"

    sess = RateLimitedSession(gate)
    attach_defaults(sess, api_key=api_key, timeout=timeout, user_agent=user_agent)

    return SolidarityClient(base_url, api_key, session=sess, timeout=timeout, user_agent=user_agent)
