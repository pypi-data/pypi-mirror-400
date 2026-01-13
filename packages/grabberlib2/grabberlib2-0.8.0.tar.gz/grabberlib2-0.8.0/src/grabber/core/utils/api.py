from typing import Any

import aiohttp
import requests
from tenacity import retry, retry_if_exception_type, wait_chain, wait_fixed


@retry(
    wait=wait_chain(
        *[wait_fixed(3) for _ in range(5)]
        + [wait_fixed(7) for _ in range(4)]
        + [wait_fixed(9) for _ in range(3)]
        + [wait_fixed(15)],
    ),
    reraise=True,
)
async def get_image_stream(
    url,
    headers: dict[str, Any] | None = None,
) -> requests.Response:
    """Wait 3s for 5 attempts
    7s for the next 4 attempts
    9s for the next 3 attempts
    then 15 for all attempts thereafter
    """
    response = (
        requests.get(url, headers=headers, stream=True) if headers is not None else requests.get(url, stream=True)
    )

    if response.status_code >= 300:
        raise Exception(f"Not able to retrieve {url}: {response.status_code}\n")

    return response


@retry(
    wait=wait_chain(
        *[wait_fixed(3) for _ in range(5)]
        + [wait_fixed(7) for _ in range(4)]
        + [wait_fixed(9) for _ in range(3)]
        + [wait_fixed(15)]
    ),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)
async def get_images_reponse_with_aiohttp(
    session: aiohttp.ClientSession,
    url: str,
    headers: dict[str, str] | None = None,
) -> bytes:
    """
    Async, retried fetch that returns the *full* response body as bytes.

    Retrying the whole 'GET + read()' ensures flaky networks are handled cleanly.
    If you want true streaming (chunked to disk) with retries, we can wrap the
    write loop in this function instead and keep the same signature.
    """
    # Per-request headers override (if provided)
    async with session.get(url, headers=headers) as resp:
        if resp.status >= 300:
            print(f"Response status: {resp.status}")
            # Read a little bit for context but don't blow memory if it's huge
            try:
                preview = await resp.text(errors="ignore")
                preview = preview[:500]
            except Exception:
                preview = ""
            raise Exception(f"Not able to retrieve {url}: HTTP {resp.status}\n{preview}")
        return await resp.read()
