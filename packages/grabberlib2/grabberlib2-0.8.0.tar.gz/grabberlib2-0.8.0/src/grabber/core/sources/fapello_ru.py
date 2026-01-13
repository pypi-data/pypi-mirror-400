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
    query: str = "",
) -> IndexedSet:
    first_page_response = httpx.get(url=url, headers=headers)
    page_content = first_page_response.content.decode("utf-8")
    soup = BeautifulSoup(page_content, features="html.parser")
    raw_images = IndexedSet()
    image_links = IndexedSet()
    parsed_url = parse_url(url)
    model_id = parsed_url["file"]
    pagination_query = "a[aria-label^='Go to page']"
    pagination_tags = soup.select(pagination_query)
    pagination_base_url = "https://fapello.ru/galleries/{model_id}?page={page_number}"

    if pagination_tags:
        first_page_href = pagination_tags[0]
        last_page_href = pagination_tags[-1]
        first_page_number = int(first_page_href.text.strip())
        last_page_number = int(last_page_href.text.strip())
    else:
        first_page_number = 1
        last_page_number = 1

    for page_number in range(first_page_number, last_page_number + 1):
        image_tags = soup.select(query)
        raw_images.update(*[tag for tag in image_tags if ".svg" not in tag.attrs["src"]])

        if page_number < last_page_number:
            target_url = pagination_base_url.format(model_id=model_id, page_number=page_number + 1)
            try:
                page_response = httpx.get(url=target_url, headers=headers)
            except Exception as exc:
                print(f"Error when requesting {target_url}: {exc}")
                continue
            page_content = page_response.content.decode("utf-8")
            soup = BeautifulSoup(page_content, features="html.parser")
        else:
            break

    for idx, image_tag in enumerate(raw_images):
        if "src" not in image_tag.attrs:
            if "data-src" in image_tag.attrs:
                src_attr = "data-src"
            else:
                continue
        else:
            src_attr = "src"
        image_src = image_tag.attrs[src_attr]
        parsed_url = parse_url(image_src)
        image_prefix = f"{idx + 1}".zfill(4)
        image_filename = parsed_url["file"]
        image_links.add((image_prefix, f"{image_prefix}-{image_filename}", f"{image_filename}", image_src))

    ordered_unique_img_urls = IndexedSet([a[1:] for a in image_links])

    return ordered_unique_img_urls


async def get_sources_for_fapello_ru(
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

    for source_url in tqdm_sources_iterable:
        final_dest = pathlib.Path(str(original_folder_path)) if final_dest else ""
        all_sources.append(source_url)
        soup = await get_soup(
            target_url=source_url,
            headers=headers,
        )
        base_url = get_base_url(source_url)
        galery_link_tag = soup.select_one("a[href*='/galleries/']")
        gallery_url = ""

        if galery_link_tag:
            gallery_url = urljoin(base_url, galery_link_tag.attrs["href"])
        else:
            continue

        ordered_unique_img_urls = await get_pages_from_pagination(
            url=gallery_url,
            headers=headers,
            query=query,
        )

        page_title = "".join(cast(Tag, soup.select_one("div.flex-1.min-w-0 p")).get_text(strip=True).split(","))
        page_title = unidecode(
            " ".join(f"#{part.replace('.', '_').replace('-', '_')}" for part in page_title.split(" "))
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
