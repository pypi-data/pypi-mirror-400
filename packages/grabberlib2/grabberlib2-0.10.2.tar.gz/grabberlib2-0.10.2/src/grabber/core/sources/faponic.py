import pathlib
from typing import Any
from urllib.parse import urlparse

import httpx
from boltons.setutils import IndexedSet
from bs4 import BeautifulSoup, Tag
from telegraph import Telegraph
from tqdm import tqdm
from unidecode import unidecode

from grabber.core.sources.helpers.core import get_page_title, handle_final_destination
from grabber.core.utils import (
    build_unique_img_urls,
    build_unique_video_urls,
    get_tags,
    headers_mapping,
    query_mapping,
    run_downloader,
    send_post_to_telegram,
)


async def get_pages_from_pagination(
    url: str,
    headers: dict[str, str] | None = None,
    query: str = "",
) -> list[Tag]:
    base_url = "https://faponic.com/ajax/model/{model_slug}/page-{page_number}/"
    parsed_url = urlparse(url)
    model_slug = parsed_url.path.replace("/", "")
    page_number = 1
    first_page_url = base_url.format(model_slug=model_slug, page_number=page_number)
    first_page_response = httpx.get(url=first_page_url, headers=headers)
    page_content = first_page_response.content.decode("utf-8")
    images_tag = IndexedSet()

    while page_content:
        soup = BeautifulSoup(page_content, features="lxml")
        image_tags = soup.select(query)
        images_tag.update(*[tag for tag in image_tags if ".svg" not in tag.attrs["src"]])

        page_number += 1
        target_url = base_url.format(model_slug=model_slug, page_number=page_number)
        try:
            page_response = httpx.get(url=target_url, headers=headers)
        except Exception as exc:
            print(f"Error when requesting {target_url}: {exc}")
            continue
        page_content = page_response.content.decode("utf-8")

    return list(images_tag)


async def get_sources_for_faponic(
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
    title_folder_mapping: dict[str, tuple[IndexedSet, Any]] = {}
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

        image_tags = [
            *await get_pages_from_pagination(
                url=source_url,
                headers=headers,
                query=query,
            ),
        ]

        _, soup = await get_tags(
            source_url,
            headers=headers,
            query=query,
        )
        page_title = get_page_title(soup=soup, strings_to_remove=["aka", "- Faponic", "Nude"])
        titles.add(page_title)

        image_tags = sorted(image_tags, key=lambda tag: tag.attrs["src"])
        ordered_unique_img_urls = await build_unique_img_urls(image_tags, src_attr)

        tqdm_sources_iterable.set_description(f"Finished retrieving images for {page_title}")
        final_dest, title_folder_mapping = handle_final_destination(
            page_title=page_title,
            entity=entity,
            ordered_unique_img_urls=ordered_unique_img_urls,
            title_folder_mapping=title_folder_mapping,
            final_dest=final_dest,
        )

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
