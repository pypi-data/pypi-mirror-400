import logging

from adoc_link_checker.http.checker import check_url
from adoc_link_checker.core.context import LinkCheckContext

logger = logging.getLogger(__name__)


class LinkChecker:
    """
    Service responsible for checking URLs with caching support.
    """

    def __init__(self, session, context: LinkCheckContext):
        self.session = session
        self.context = context

    def check(self, url: str) -> bool:
        """
        Check a URL, using the shared cache when possible.
        """
        cached = self.context.get_cached(url)
        if cached is not None:
            logger.debug(f"🔁 Cached result for {url}")
            return cached

        result = check_url(
            session=self.session,
            url=url,
            timeout=self.context.timeout,
            blacklist=tuple(self.context.blacklist),
        )

        self.context.set_cached(url, result)
        return result
