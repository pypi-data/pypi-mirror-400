import logging
import requests

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from adoc_link_checker.config import USER_AGENT, RETRY_CONFIG
from adoc_link_checker.utils.url import is_blacklisted

logger = logging.getLogger(__name__)


def create_session() -> requests.Session:
    """
    Create a configured HTTP session with retries and User-Agent.
    """
    session = requests.Session()
    retries = Retry(**RETRY_CONFIG)

    session.mount("https://", HTTPAdapter(max_retries=retries))
    session.mount("http://", HTTPAdapter(max_retries=retries))
    session.headers.update({"User-Agent": USER_AGENT})

    return session


def check_url(
    session: requests.Session,
    url: str,
    timeout: int,
    blacklist: tuple,
) -> bool:
    """
    Check if a URL is accessible.
    Strategy: HEAD first, fallback to GET.
    """
    if is_blacklisted(url, list(blacklist)):
        logger.debug(f"Ignoring blacklisted URL: {url}")
        return True

    try:
        response = session.head(
            url,
            timeout=timeout,
            allow_redirects=True,
        )

        if response.status_code >= 400:
            logger.debug(
                f"HEAD failed for {url} "
                f"(status {response.status_code}), retrying with GET"
            )
            response = session.get(
                url,
                timeout=timeout,
                stream=True,
            )

        return response.status_code < 400

    except requests.RequestException as e:
        logger.warning(f"⚠️ {url} failed: {e}")
        return False
