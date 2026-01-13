import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


def is_valid_url(url: str) -> bool:
    """
    Vérifie si une URL est valide
    (scheme http/https et présence d'un netloc).
    """
    try:
        result = urlparse(url)
        return result.scheme in ("http", "https") and bool(result.netloc)
    except ValueError:
        return False


def normalize_url(url: str) -> str:
    """
    Normalize a URL by removing fragments, queries,
    surrounding quotes, trailing slashes and punctuation.
    """
    # Remove fragments and query parameters
    url = url.split("#")[0].split("?")[0]

    # Remove surrounding quotes / brackets
    url = url.strip('"\'<>')

    # Remove common trailing punctuation from prose
    url = url.rstrip(".,;:!?)[]")

    # Remove trailing slash
    url = url.rstrip("/")

    return url


def is_blacklisted(url: str, blacklist: list[str]) -> bool:
    """
    Return True if the URL's domain matches a blacklisted domain.

    Matching rules:
    - exact domain match
    - subdomain match
    """
    try:
        netloc = urlparse(url).netloc.lower()
    except ValueError:
        return False

    for domain in blacklist:
        domain = domain.lower()
        if netloc == domain or netloc.endswith("." + domain):
            return True

    return False


def youtube_id_to_url(youtube_id: str) -> str:
    """
    Convert a YouTube video ID into a full URL.
    """
    return f"https://www.youtube.com/watch?v={youtube_id}"
