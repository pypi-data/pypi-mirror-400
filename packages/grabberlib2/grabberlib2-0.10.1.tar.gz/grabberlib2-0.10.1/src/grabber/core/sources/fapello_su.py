import asyncio
import pathlib
import re
from typing import Any, cast

import httpx
from boltons.setutils import IndexedSet
from bs4 import BeautifulSoup, Tag
from telegraph import Telegraph
from tqdm import tqdm
from unidecode import unidecode
from url_parser import parse_url

from grabber.core.utils import (
    build_unique_img_urls,
    get_tags,
    headers_mapping,
    query_mapping,
    run_downloader,
    send_post_to_telegram,
)

NUMBERS_PATTERN = r"\d+(?:,\d+)*"


async def get_pages_from_pagination(
    url: str,
    headers: dict[str, str],
    query: str,
    max_pages: int = 50,
) -> list[Tag]:
    parsed_url = parse_url(url)
    model_name = parsed_url["path"].replace("/", "")
    page_number = 1
    target_url = url
    first_page_response = httpx.get(url=target_url, headers=headers)
    page_content = first_page_response.content.decode("utf-8")
    final_image_tags = IndexedSet()
    last_final_image_tags_count = len(final_image_tags)
    counter = 0
    query = f"div#content div {query}"

    while (page_content and page_number <= max_pages) and counter <= 10:
        print(f"Processing page {page_number} for model {model_name}...")
        soup = BeautifulSoup(page_content, features="html.parser")
        page_number += 1
        last_final_image_tags_count = len(final_image_tags)

        image_tags = soup.select(query)

        print(f"Found {len(image_tags)} images on page {page_number}")

        for image_tag in image_tags:
            if ".md." in image_tag.attrs["data-src"] or ".th." in image_tag.attrs["data-src"]:
                image_tag.attrs["src"] = image_tag.attrs["data-src"].replace(".md", "").replace(".th", "")
                image_tag.attrs["data-src"] = image_tag.attrs["data-src"].replace(".md", "").replace(".th", "")
                final_image_tags.add(image_tag)

        if last_final_image_tags_count == len(final_image_tags):
            print(f"No images found on page {page_number} for model {model_name}.")
            break

        pagination = soup.select(":-soup-contains-own('Next Page')")
        if pagination:
            next_page = pagination[0]
            target_url = next_page.attrs["href"]
            try:
                page_response = httpx.get(url=target_url, headers=headers)
                page_content = page_response.content.decode("utf-8")
            except Exception as exc:
                counter += 1
                print(f"Error when requesting {target_url}: {exc}\nRetry attempt {counter}/10")
                await asyncio.sleep(5)
                continue
        else:
            break
        await asyncio.sleep(0.5)

    return list(final_image_tags)


async def get_sources_for_fapello_su(
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
    query, src_attr = query_mapping[entity]
    headers = headers_mapping.get(entity, None)
    page_title = ""
    title_folder_mapping = {}
    posts_sent_counter = 0
    titles = IndexedSet()
    ordered_unique_img_urls = None
    all_sources: list[str] = []
    original_folder_path = final_dest
    channel = kwargs.get("channel", "")
    max_pages: int = kwargs.get("max_pages", 500)

    for source_url in tqdm_sources_iterable:
        final_dest = pathlib.Path(str(original_folder_path)) if final_dest else ""
        all_sources.append(source_url)

        image_tags: list[Tag] = [
            *await get_pages_from_pagination(
                url=source_url,
                headers=headers,
                query=query,
                max_pages=max_pages,
            ),
        ]

        _, soup = await get_tags(
            source_url,
            headers=headers,
            query=query,
        )
        page_title = cast(Tag, soup.find("title")).get_text(strip=True).strip().rstrip()
        page_title = (
            page_title.split("Leaked Files")[0]
            .split("- Fapello.su")[0]
            .split("LeakedOnlyFansFiles")[0]
            .replace("https:", "")
        )
        page_title = re.sub(NUMBERS_PATTERN, "", page_title).strip()
        page_title = unidecode(
            " ".join(
                f"#{part.strip().replace(' ', '').replace('.', '_').replace('-', '_')}"
                for part in page_title.split("/")
            )
        )
        page_title = f"{page_title}"
        titles.add(page_title)

        image_tags = sorted(image_tags, key=lambda tag: tag.attrs["src"])
        ordered_unique_img_urls = await build_unique_img_urls(image_tags, src_attr)
        tqdm_sources_iterable.set_description(f"Finished retrieving images for {page_title}")

        if final_dest:
            final_dest = pathlib.Path(final_dest) / unidecode(f"{page_title} - {entity}")
            if not final_dest.exists():
                final_dest.mkdir(parents=True, exist_ok=True)

            title_folder_mapping[page_title] = (ordered_unique_img_urls, final_dest)

        if save_to_telegraph:
            _ = await send_post_to_telegram(
                ordered_unique_img_urls=ordered_unique_img_urls,
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
