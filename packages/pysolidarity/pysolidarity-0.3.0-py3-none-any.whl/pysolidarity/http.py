import requests
from typing import Optional
from .types import TimeoutType

DEFAULT_TIMEOUT: TimeoutType = (10, 60)

def attach_defaults(
    session: requests.Session,
    *,
    api_key: str,
    timeout: TimeoutType = DEFAULT_TIMEOUT,
    user_agent: str = "pysolidarity/0.1",
) -> None:
    session.headers.update({
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": user_agent,
    })
    setattr(session, "_default_timeout", timeout)


def make_default_session(
    *,
    api_key: str,
    timeout: TimeoutType = DEFAULT_TIMEOUT,
    user_agent: str = "pysolidarity/0.1",
) -> requests.Session:
    sess = requests.Session()
    attach_defaults(sess, api_key=api_key, timeout=timeout, user_agent=user_agent)
    return sess