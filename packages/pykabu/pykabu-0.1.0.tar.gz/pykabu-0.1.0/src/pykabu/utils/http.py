"""HTTP client utilities for fetching web pages"""

import httpx

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
}


def fetch_page(base_url: str, path: str, timeout: float = 10.0) -> str:
    """Fetch a page from a website.

    Args:
        base_url: Base URL (e.g., "https://nikkei225jp.com")
        path: URL path (e.g., "/schedule/")
        timeout: Request timeout in seconds

    Returns:
        HTML content as string

    Raises:
        httpx.HTTPError: If the request fails
    """
    url = f"{base_url}{path}"
    with httpx.Client(headers=DEFAULT_HEADERS, timeout=timeout) as client:
        response = client.get(url)
        response.raise_for_status()
        return response.text
