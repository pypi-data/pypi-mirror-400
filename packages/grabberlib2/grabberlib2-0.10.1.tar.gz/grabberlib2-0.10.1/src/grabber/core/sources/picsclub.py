import pathlib
from typing import Any, cast
from urllib.parse import urljoin

import httpx
from boltons.setutils import IndexedSet
from bs4 import BeautifulSoup, Tag
from telegraph import Telegraph
from tqdm import tqdm
from unidecode import unidecode
from url_parser import get_base_url, parse_url

from grabber.core.utils import (
    get_soup,
    headers_mapping,
    query_mapping,
    run_downloader,
    send_post_to_telegram,
)


async def get_pages_from_pagination(
    url: str,
    headers: dict[str, str],
    media_query_attr: str = "src",
    query: str = "",
) -> IndexedSet:
    first_page_response = httpx.get(url=url, headers=headers)
    page_content = first_page_response.content.decode("utf-8")
    raw_images = IndexedSet()
    image_links = IndexedSet()
    base_url = get_base_url(url)

    while page_content:
        soup = BeautifulSoup(page_content, features="html.parser")
        image_tags = soup.select(query)
        raw_images.update(*[tag for tag in image_tags if ".svg" not in tag.attrs[media_query_attr]])

        pagination = soup.select(":-soup-contains-own('NEXT')")
        if pagination:
            next_page = pagination[0]
            next_page_link = next_page.attrs.get("href", "")

            if not next_page_link:
                break

            target_url = urljoin(base_url, next_page_link)
            try:
                page_response = httpx.get(url=target_url, headers=headers)
            except Exception as exc:
                print(f"Error when requesting {target_url}: {exc}")
                continue
            page_content = page_response.content.decode("utf-8")
        else:
            break

    for idx, image_tag in enumerate(raw_images):
        image_src: str = image_tag.attrs[media_query_attr]
        final_image_src = image_src.replace(".md", "")
        parsed_url = parse_url(final_image_src)
        image_prefix = f"{idx + 1}".zfill(4)
        image_filename = parsed_url["file"]
        image_links.add((image_prefix, f"{image_prefix}-{image_filename}", f"{image_filename}", final_image_src))

    ordered_unique_img_urls = IndexedSet(sorted(image_links, key=lambda x: list(x).pop(0)))
    ordered_unique_img_urls = IndexedSet([a[1:] for a in ordered_unique_img_urls])

    return ordered_unique_img_urls


async def get_sources_for_picsclub(
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
    query, media_query_attr = query_mapping[entity]
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
            media_query_attr=media_query_attr,
            query=query,
        )

        page_title = unidecode(cast(Tag, soup.find("title")).get_text(strip=True).strip().rstrip())
        page_title = page_title.split("sliv")[0].split("foto")[0].replace("https:", "")
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
