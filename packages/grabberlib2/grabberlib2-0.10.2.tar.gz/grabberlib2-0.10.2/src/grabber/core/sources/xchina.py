import pathlib
import re
from typing import Any, cast
from urllib.parse import urljoin, urlparse

import cloudscraper
from boltons.setutils import IndexedSet
from bs4 import BeautifulSoup, Tag
from telegraph import Telegraph
from tqdm import tqdm
from unidecode import unidecode
from url_parser import parse_url

from grabber.core.utils import (
    headers_mapping,
    query_mapping,
    run_downloader,
    send_post_to_telegram,
)


async def get_pages_from_pagination(
    url: str,
    headers: dict[str, str],
    query: str = "",
) -> IndexedSet:
    scraper = cloudscraper.create_scraper(interpreter="nodejs")
    first_page_response = scraper.get(url=url, headers=headers)
    page_content = first_page_response.content.decode("utf-8")
    raw_images = IndexedSet()
    image_links = IndexedSet()
    parsed_url = urlparse(url)
    base_url = f"https://{parsed_url.netloc}"
    soup = BeautifulSoup(page_content, features="html.parser")
    image_tags = soup.select(query)
    raw_images.update(*image_tags)
    pagination_links = IndexedSet()
    pagination = []
    image_url_pattern = r"https?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+.webp"

    for page in soup.select("div.pager a:not(.current):not(.pager-next)"):
        if page.attrs["href"] in pagination_links:
            pagination_links.add(page.attrs["href"])
            pagination.append(page)

    if pagination:
        for next_page in pagination:
            target_url = urljoin(base_url, next_page.attrs["href"])
            try:
                page_response = scraper.get(url=target_url, headers=headers)
            except Exception as exc:
                print(f"Error when requesting {target_url}: {exc}")
                continue
            page_content = page_response.content.decode("utf-8")
            soup = BeautifulSoup(page_content, features="html.parser")
            image_tags = soup.select(query)
            raw_images.update(*image_tags)

    for idx, image_tag in enumerate(raw_images):
        image_string_result = re.findall(image_url_pattern, image_tag.attrs["style"])
        if image_string_result:
            image_src = image_string_result[0].replace(".webp", ".jpg").replace("_600x0", "")
        final_image_src = urljoin(base_url, image_src)
        parsed_url = parse_url(final_image_src)
        image_prefix = f"{idx + 1}".zfill(4)
        image_filename = parsed_url["file"]
        image_links.add((image_prefix, f"{image_prefix}-{image_filename}", f"{image_filename}", final_image_src))

    ordered_unique_img_urls = IndexedSet(sorted(image_links, key=lambda x: list(x).pop(0)))
    ordered_unique_img_urls = IndexedSet([a[1:] for a in ordered_unique_img_urls])

    return ordered_unique_img_urls


async def get_sources_for_xchina(
    sources: list[str],
    entity: str,
    telegraph_client: Telegraph | None = None,
    final_dest: str | pathlib.Path = "",
    save_to_telegraph: bool | None = False,
    **kwargs: Any,
) -> None:
    tqdm_sources_iterable = tqdm(
        sources,
        total=len(sources),
        desc="Retrieving URLs...",
    )
    query, _ = query_mapping[entity]
    headers = headers_mapping[entity] if entity in headers_mapping else headers_mapping["common"]
    page_title = ""
    title_folder_mapping = {}
    posts_sent_counter = 0
    titles = IndexedSet()
    ordered_unique_img_urls = None
    ordered_unique_video_urls = None
    all_sources: list[str] = []
    original_folder_path = final_dest
    channel = kwargs.get("channel", "")
    scraper = cloudscraper.create_scraper(interpreter="nodejs")

    for source_url in tqdm_sources_iterable:
        final_dest = pathlib.Path(str(original_folder_path)) if final_dest else ""
        all_sources.append(source_url)
        soup = BeautifulSoup(scraper.get(url=source_url, headers=headers).content)

        ordered_unique_img_urls = await get_pages_from_pagination(
            url=source_url,
            headers=headers,
            query=query,
        )

        page_title = cast(Tag, soup.find("title")).get_text(strip=True).split("- Chinese Nude")[0].strip()
        page_title = unidecode(page_title)
        titles.add(page_title)

        if final_dest:
            final_dest = pathlib.Path(final_dest) / unidecode(f"{page_title} - {entity}")
            if not final_dest.exists():
                final_dest.mkdir(parents=True, exist_ok=True)

            title_folder_mapping[page_title] = (ordered_unique_img_urls, final_dest)

        if save_to_telegraph:
            _ = await send_post_to_telegram(
                ordered_unique_img_urls=ordered_unique_img_urls,
                ordered_unique_video_urls=ordered_unique_video_urls,
                page_title=page_title,
                telegraph_client=telegraph_client,
                posts_sent_counter=posts_sent_counter,
                tqdm_sources_iterable=tqdm_sources_iterable,
                all_sources=all_sources,
                source_url=source_url,
                entity=entity,
                channel=channel,
            )
            page_title = ""

    if final_dest and ordered_unique_img_urls:
        await run_downloader(
            final_dest=final_dest,
            page_title=page_title,
            unique_img_urls=ordered_unique_img_urls,
            titles=titles,
            title_folder_mapping=title_folder_mapping,
            headers=headers,
        )
