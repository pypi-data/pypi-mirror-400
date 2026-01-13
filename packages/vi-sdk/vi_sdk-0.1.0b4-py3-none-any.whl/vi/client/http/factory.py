#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   factory.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK requesterfactory module.
"""

from urllib.parse import urlparse

from vi.client.auth import Authentication
from vi.client.http.requester import Requester
from vi.client.http.retry import RetryConfig


def requester_from_url(
    auth: Authentication,
    url: str,
    retry_config: RetryConfig | None = None,
) -> Requester:
    """Get a Requester for an API endpoint URL.

    The API endpoint URL may be in one of the following forms:

    - `http://ENDPOINT`, `https://ENDPOINT`

        API Client will connect authenticated with the given
        authentication to the given HTTP or HTTPS endpoint

    Args:
        auth: Authentication instance
        url: API endpoint URL
        retry_config: Optional retry configuration

    Returns:
        Configured Requester instance

    """
    parsed_url = urlparse(url)

    if parsed_url.scheme in {"http", "https"}:
        return Requester(auth, url, retry_config=retry_config)

    raise RuntimeError(f"Unrecognized URL scheme '{parsed_url.scheme}'")
