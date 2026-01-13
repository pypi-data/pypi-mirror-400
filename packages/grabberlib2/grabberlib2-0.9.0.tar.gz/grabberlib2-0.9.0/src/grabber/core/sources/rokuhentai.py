import pathlib
from typing import cast

import httpx
from boltons.setutils import IndexedSet
from bs4 import BeautifulSoup, Tag
from telegraph import Telegraph
from tqdm import tqdm
from unidecode import unidecode
from url_parser import parse_url

from grabber.core.utils import (
    headers_mapping,
    query_mapping,
    send_post_to_telegram,
)
from grabber.core.utils.download_upload import run_downloader
from grabber.core.utils.scraper import get_soup


async def get_pages_from_pagination(
    url: str,
    headers: dict[str, str],
    query: str = "",
) -> IndexedSet:
    image_links = IndexedSet()
    base_image_url = "https://rokuhentai.com/_images/pages/{post_id}/{image_number}.jpg"

    page_response = httpx.get(url=url, headers=headers)
    page_content = page_response.content.decode("utf-8")
    soup = BeautifulSoup(page_content, features="html.parser")
    for a_tag in soup.select(query):
        parsed_href = parse_url(a_tag.attrs["href"])
        image_number = parsed_href.get("file", "").replace("/", "")
        post_id = parsed_href.get("dir", "").replace("/", "")
        final_image_src = base_image_url.format(post_id=post_id, image_number=image_number)
        image_prefix = f"{image_number}".zfill(4)
        image_filename = f"{image_number}.jpg"
        image_links.add((image_prefix, f"{image_prefix}-{image_filename}", f"{image_filename}", final_image_src))

    ordered_unique_img_urls = IndexedSet(sorted(image_links, key=lambda x: list(x).pop(0)))
    ordered_unique_img_urls = IndexedSet([a[1:] for a in ordered_unique_img_urls])

    return ordered_unique_img_urls


async def get_sources_for_rokuhentai(
    sources: list[str],
    entity: str,
    telegraph_client: Telegraph | None = None,
    final_dest: str | pathlib.Path = "",
    save_to_telegraph: bool | None = False,
    is_tag: bool | None = False,
    **kwargs,
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

    for source_url in tqdm_sources_iterable:
        final_dest = pathlib.Path(str(original_folder_path)) if final_dest else ""
        all_sources.append(source_url)
        soup = await get_soup(
            target_url=source_url,
            headers=headers,
        )

        ordered_unique_img_urls = await get_pages_from_pagination(
            url=source_url,
            headers=headers,
            query=query,
        )

        page_title = cast(Tag, soup.find("title")).get_text(strip=True).strip().rstrip()
        page_title = page_title.split("- Sort by Name")[0].split("- Always update")[0].replace("- Roku Hentai", "")
        page_title = unidecode(
            " ".join(
                f"#{part.strip().replace(' ', '').replace('.', '_').replace('-', '_')}"
                for part in page_title.split("/")
            )
        )
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
