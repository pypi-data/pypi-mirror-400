"""URL normalization helpers used by screenshot backends."""

from __future__ import annotations

from urllib.parse import urlparse, urlunparse


def normalize_url(url: str) -> str:
    """Return a canonical URL string suitable for queue de-duplication."""

    parsed = urlparse(url.strip())
    if not parsed.scheme or not parsed.netloc:
        return url.strip()

    hostname = parsed.hostname or ""
    port = parsed.port
    if port in (80, 443):
        port = None
    netloc = hostname.lower()
    if parsed.username:
        netloc = f"{parsed.username}@{netloc}"
    if port:
        netloc = f"{netloc}:{port}"

    path = parsed.path or "/"
    while "//" in path:
        path = path.replace("//", "/")
    if path.endswith("/") and path != "/":
        path = path.rstrip("/")

    return urlunparse(
        (
            parsed.scheme.lower(),
            netloc,
            path,
            parsed.params,
            parsed.query,
            "",
        )
    )
