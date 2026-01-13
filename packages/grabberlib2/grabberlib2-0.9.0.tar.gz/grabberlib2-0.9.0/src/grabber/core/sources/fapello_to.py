import pathlib
from typing import Any, cast

import httpx
from boltons.setutils import IndexedSet
from bs4 import Tag
from telegraph import Telegraph
from tqdm import tqdm
from unidecode import unidecode
from url_parser import parse_url

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
) -> IndexedSet:
    referer_header = {"Referer": url}
    headers.update(referer_header)
    parsed_url: dict[str, str] = parse_url(url)
    model_id: str = parsed_url["file"]
    base_url = "https://fapello.to//api/media/{model_id}/{page_number}/1"
    page_number = 1
    endpoint = base_url.format(model_id=model_id, page_number=page_number)
    response = httpx.get(url=endpoint, headers=headers)
    response_data: dict[str, Any] = response.json()
    images_tags = IndexedSet()

    while response_data:
        for idx, data in enumerate(response_data):
            image_url = data["newUrl"]
            parsed_image_url = parse_url(image_url)
            image_prefix = f"{idx + 1}".zfill(4)
            image_filename = parsed_image_url["file"]

            images_tags.add((image_prefix, f"{image_prefix}-{image_filename}", f"{image_filename}", image_url))

            page_number += 1
            next_page_url = base_url.format(model_id=model_id, page_number=page_number)
            response = httpx.get(url=next_page_url, headers=headers)
            response_data = response.json()

    ordered_unique_img_urls = IndexedSet([a[1:] for a in images_tags])

    return ordered_unique_img_urls


async def get_sources_for_fapello_to(
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
    headers = headers_mapping[entity] if entity in headers_mapping else headers_mapping["common"]
    page_title = ""
    title_folder_mapping = {}
    posts_sent_counter = 0
    titles = IndexedSet()
    ordered_unique_img_urls = None
    ordered_unique_video_urls = None
    all_sources: list[str] = []
    original_folder_path = final_dest
    first_link_tag_query = "link[rel='shortlink']"
    channel = kwargs.get("channel", "")

    for source_url in tqdm_sources_iterable:
        final_dest = pathlib.Path(str(original_folder_path)) if final_dest else ""
        all_sources.append(source_url)
        # breakpoint()
        soup = await get_soup(
            target_url=source_url,
            headers=headers,
        )
        # first_link_tag = soup.select_one(first_link_tag_query)
        #
        # if first_link_tag is None:
        #     continue

        ordered_unique_img_urls = await get_pages_from_pagination(
            url=source_url,
            headers=headers,
        )

        page_title = cast(Tag, soup.find("title")).get_text(strip=True).strip().rstrip()
        page_title = page_title.split("- fapello")[0].split("Nude")[0].replace("https:", "")
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
