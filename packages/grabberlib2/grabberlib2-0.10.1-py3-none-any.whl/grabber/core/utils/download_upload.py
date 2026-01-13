import asyncio
import pathlib
import re
import time
from collections.abc import Coroutine, Iterable
from typing import Any, TypeVar

import aiofiles
import aiohttp
import httpx
from boltons.setutils import IndexedSet
from bs4 import BeautifulSoup
from PIL import Image
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_chain, wait_fixed
from tqdm import tqdm

from grabber.core.settings import get_media_root

from .constants import (
    CONNECT_TIMEOUT_S,
    DEFAULT_PER_IMAGE_CONCURRENCY,
    PER_HOST_LIMIT,
    PER_IMAGE_HARD_TIMEOUT_S,
    READ_TIMEOUT_S,
    headers_mapping,
)

T = TypeVar("T")


# --- Async retried fetch, returns full bytes ---
class TemporaryHTTPError(Exception):
    """Errors worth retrying (e.g., 429/5xx)."""


def wrapper(coro: Coroutine[Any, Any, T]) -> T:
    return asyncio.run(coro)


async def convert_from_webp_to_jpg(folder: pathlib.Path) -> None:
    files = list(folder.iterdir())
    tqdm_iterable = tqdm(
        files,
        total=len(files),
        desc="Converting images from WebP to JPEG",
        leave=False,
    )

    for file in tqdm_iterable:
        if file.suffix == ".webp":
            image = Image.open(file).convert("RGB")
            new_file = file.with_suffix(".jpg")
            image.save(new_file, "JPEG")
            file.unlink()


@retry(
    wait=wait_chain(
        *[wait_fixed(3) for _ in range(5)]
        + [wait_fixed(7) for _ in range(4)]
        + [wait_fixed(9) for _ in range(3)]
        + [wait_fixed(15)]
    ),
    stop=stop_after_attempt(20),  # be explicit; can adjust
    retry=retry_if_exception_type(
        (
            TemporaryHTTPError,
            aiohttp.ClientOSError,
            aiohttp.ServerDisconnectedError,
            aiohttp.ClientPayloadError,
            asyncio.TimeoutError,
        )
    ),
    reraise=True,
)
async def get_image_bytes(
    session: aiohttp.ClientSession,
    url: str,
    headers: dict[str, str] | None = None,
) -> bytes:
    """
    GET the url and return the full body as bytes.
    Retries on timeouts, disconnects, payload errors, 429 and 5xx.
    """
    async with session.get(url, headers=headers) as resp:
        # Retry on 429/5xx; raise for other 4xx (probably permanent)
        if resp.status == 429 or 500 <= resp.status < 600:
            # Optionally, honor Retry-After (simple parse)
            ra = resp.headers.get("Retry-After")
            # We *let* tenacity handle waiting; we just classify as temporary
            text_preview = ""
            try:
                text_preview = await resp.text(errors="ignore")
                text_preview = text_preview[:300]
            except Exception:
                pass
            raise TemporaryHTTPError(f"HTTP {resp.status} for {url}; Retry-After={ra}; {text_preview}")
        if resp.status >= 400:
            # Permanent error; don't retry
            preview = ""
            try:
                preview = await resp.text(errors="ignore")
                preview = preview[:300]
            except Exception:
                pass
            raise aiohttp.ClientResponseError(
                request_info=resp.request_info,
                history=resp.history,
                status=resp.status,
                message=f"Permanent error fetching {url}: {preview}",
                headers=resp.headers,
            )
        return await resp.read()


async def downloader(
    titles: list[str],
    title_folder_mapping: dict[str, tuple[Iterable[IndexedSet], pathlib.Path]],
    headers: dict[str, str] | None = None,
    per_image_concurrency: int = DEFAULT_PER_IMAGE_CONCURRENCY,
) -> None:
    """
    Kick off downloads for multiple titles in parallel (one task per title).
    Each title downloads its images concurrently (bounded by per_image_concurrency).
    """
    tasks = [
        download_images(
            images_set=title_folder_mapping[title][0],
            new_folder=title_folder_mapping[title][1],
            title=title,
            headers=headers,
            per_image_concurrency=per_image_concurrency,
        )
        for title in titles
    ]
    # Run all titles concurrently
    await asyncio.gather(*tasks)


@retry(
    wait=wait_chain(
        *[wait_fixed(3) for _ in range(5)]
        + [wait_fixed(7) for _ in range(4)]
        + [wait_fixed(9) for _ in range(3)]
        + [wait_fixed(15)]
    ),
    stop=stop_after_attempt(20),
    retry=retry_if_exception_type(
        (
            TemporaryHTTPError,
            aiohttp.ClientOSError,
            aiohttp.ServerDisconnectedError,
            aiohttp.ClientPayloadError,
            asyncio.TimeoutError,  # includes our asyncio.timeout() and read timeouts
        )
    ),
    reraise=True,
)
async def get_image_bytes_with_stall_guard(
    session: aiohttp.ClientSession,
    url: str,
    headers: dict[str, str] | None = None,
) -> bytes:
    """
    GET the URL and return bytes. Retries on 429/5xx and transport timeouts.
    Aborts and retries if no progress (no new bytes) for STALL_TIMEOUT_S.
    """
    CHUNK_SIZE = 1 << 15  # 32 KiB
    STALL_TIMEOUT_S = 15
    async with session.get(url, headers=headers) as resp:
        if resp.status == 429 or 500 <= resp.status < 600:
            text_preview = ""
            try:
                text_preview = await resp.text(errors="ignore")
                text_preview = text_preview[:300]
            except Exception:
                pass
            raise TemporaryHTTPError(f"HTTP {resp.status} for {url} :: {text_preview}")

        if resp.status >= 400:
            # Treat other 4xx as permanent
            preview = ""
            try:
                preview = await resp.text(errors="ignore")
                preview = preview[:300]
            except Exception:
                pass
            raise aiohttp.ClientResponseError(
                request_info=resp.request_info,
                history=resp.history,
                status=resp.status,
                message=f"Permanent error fetching {url}: {preview}",
                headers=resp.headers,
            )

        # Stream with stall detection so trickle attacks can't hang forever
        last_progress = time.monotonic()
        chunks: list[bytes] = []

        async for chunk in resp.content.iter_chunked(CHUNK_SIZE):
            if chunk:
                chunks.append(chunk)
                last_progress = time.monotonic()
            # Check for stall (no *new* bytes for too long)
            if time.monotonic() - last_progress > STALL_TIMEOUT_S:
                raise asyncio.TimeoutError(f"No progress for {STALL_TIMEOUT_S}s while reading {url}")

        return b"".join(chunks)


async def download_images(
    images_set: Iterable[tuple[int, str, str]],
    new_folder: pathlib.Path,
    title: str,
    headers: dict[str, str] | None = None,
    per_image_concurrency: int = DEFAULT_PER_IMAGE_CONCURRENCY,
) -> str:
    """
    Concurrent (bounded) downloads for one title.
    images_set: iterable of (index, filename, url)
    """
    new_folder.mkdir(parents=True, exist_ok=True)
    images_list = list(images_set)
    total = len(images_list)
    pbar = tqdm(total=total, desc=f"Downloading images for {title} in {new_folder}")

    if not headers:
        headers = headers_mapping["common"]

    merged_headers = {**(headers or {})}
    timeout = aiohttp.ClientTimeout(total=None, sock_connect=CONNECT_TIMEOUT_S, sock_read=READ_TIMEOUT_S)
    connector = aiohttp.TCPConnector(
        limit=max(2, per_image_concurrency),  # overall socket cap
        limit_per_host=PER_HOST_LIMIT,
        ttl_dns_cache=300,
    )
    sem = asyncio.Semaphore(per_image_concurrency)

    async with aiohttp.ClientSession(headers=merged_headers, timeout=timeout, connector=connector) as session:

        async def fetch_one(_idx: int, img_filename: str, image_url: str) -> pathlib.Path:
            path = new_folder / img_filename
            async with sem:
                # Absolute per-image timeout; ANY stall beyond this cancels the task
                async with asyncio.timeout(PER_IMAGE_HARD_TIMEOUT_S):
                    content = await get_image_bytes_with_stall_guard(session, image_url)
                tmp_path = path.with_suffix(path.suffix + ".part")
                async with aiofiles.open(tmp_path, "wb") as f:
                    await f.write(content)
                tmp_path.replace(path)
                pbar.set_description(f"Saved {path.name}")
                pbar.update(1)
                return path

        tasks = [asyncio.create_task(fetch_one(*t)) for t in images_list]

        results: list[pathlib.Path] = []
        try:
            for fut in asyncio.as_completed(tasks):
                try:
                    results.append(await fut)
                except Exception as e:
                    # Keep going; the retry logic lives inside get_image_bytes_with_stall_guard
                    pbar.set_description(f"Failed once: {e!s}")
        finally:
            for t in tasks:
                if not t.done():
                    t.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)

    pbar.close()

    if any(p.suffix.lower() == ".webp" for p in results):
        await convert_from_webp_to_jpg(new_folder)

    return "Done"


async def download_from_bunkr(
    links: list[str],
    headers: dict[str, str] | None = None,
) -> None:
    if headers is None:
        headers = headers_mapping["bunkr"]

    query = "div.grid-images div.grid-images_box div a.grid-images_box-link"

    for link in links:
        sources = set()
        soup = BeautifulSoup(httpx.get(link, headers=headers).content)
        a_tags = soup.select(query)
        for a_tag in a_tags:
            sources.add(a_tag.attrs["href"])

        for source in sources:
            second_soup = BeautifulSoup(httpx.get(source, headers=headers).content)
            video_source = second_soup.find("source")
            video_url = video_source.attrs["src"]
            filename = video_url.rsplit("/", 2)[-1]
            video_resp = httpx.get(video_url, headers=headers, stream=True)
            with open(get_media_root() / filename, "wb") as file:
                for chunk in video_resp.iter_content(chunk_size=1024):
                    if chunk:
                        file.write(chunk)
                        file.flush()


async def run_downloader(
    final_dest: pathlib.Path | str,
    page_title: str,
    unique_img_urls: IndexedSet,
    titles: IndexedSet,
    title_folder_mapping: dict[str, tuple[IndexedSet, pathlib.Path]],
    headers: dict[str, str] | None = None,
) -> None:
    await downloader(
        titles=list(titles),
        title_folder_mapping=title_folder_mapping,
        headers=headers,
    )


async def upload_to_r2_and_post_to_telegram(
    folder: pathlib.Path,
) -> None:
    pass


def generate_hashtags(text: str) -> str:
    # Split into parts (separates words and emojis)
    parts = text.split()

    # Separate words (alphanumeric + underscore) from emojis/symbols
    words = [part for part in parts if re.match(r"^[a-zA-Z0-9_]+$", part)]
    non_words = [part for part in parts if not re.match(r"^[a-zA-Z0-9_]+$", part)]

    if not words:
        return ""

    # First hashtag: ALL words before emojis (if any) combined
    # If there are non-words (emojis), split into before & after emoji
    if non_words:
        # Find where the first emoji appears
        first_emoji_pos = parts.index(non_words[0])
        words_before_emoji = [p for p in parts[:first_emoji_pos] if re.match(r"^[a-zA-Z0-9_]+$", p)]
        hashtag1 = "".join(words_before_emoji)
    else:
        hashtag1 = "".join(words)  # No emojis, combine all

    # Second hashtag: Last word (if different)
    hashtag2 = words[-1] if (len(words) > 1 and words[-1].lower() != hashtag1.lower()) else None

    # Generate result
    result = f"#{hashtag1}"
    if hashtag2:
        result += f" #{hashtag2}"

    return result
