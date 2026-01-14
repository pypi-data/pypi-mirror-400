import logging
import os
from pathlib import Path
from urllib.parse import urlparse

import requests
import urllib3
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_fixed,
)

from arkindex import ArkindexClient
from teklia_toolbox import VERSION

logger = logging.getLogger(__name__)


def should_verify_cert(url: str) -> bool:
    """
    Skip SSL certification validation when hitting a development instance
    """
    if not url:
        return True

    host = urlparse(url).netloc
    return not host.endswith("ark.localhost")


def get_arkindex_client(**options) -> ArkindexClient:
    # Skip SSL verification in Arkindex API client for local development hosts
    verify = should_verify_cert(options.get("base_url"))
    if not verify:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        logger.warn("SSL certificate verification is disabled for Arkindex API calls")

    return ArkindexClient(verify=verify, **options)


# Time to wait before retrying the IIIF image information fetching
HTTP_GET_RETRY_BACKOFF = 10

# Specific User-Agent to bypass potential server limitations
USER_AGENT = os.getenv("REQUESTS_USER_AGENT", f"Teklia/Tools {VERSION}")

DOWNLOAD_CHUNK_SIZE = 8192


@retry(
    reraise=True,
    retry=retry_if_exception_type(requests.RequestException),
    stop=stop_after_attempt(3),
    wait=wait_fixed(HTTP_GET_RETRY_BACKOFF),
)
def download_file(url: str, path: Path) -> None:
    """
    Download a URL into a local path, retrying if necessary
    """
    with requests.get(
        url,
        stream=True,
        headers={"User-Agent": USER_AGENT},
        verify=should_verify_cert(url),
    ) as r:
        r.raise_for_status()
        with path.open("wb") as f:
            for chunk in r.iter_content(chunk_size=DOWNLOAD_CHUNK_SIZE):
                if chunk:  # Ignore empty chunks
                    f.write(chunk)
