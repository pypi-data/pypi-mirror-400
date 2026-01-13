import pathlib

from boltons.setutils import IndexedSet
from bs4 import Tag
from telegraph import Telegraph
from tqdm import tqdm
from unidecode import unidecode

from grabber.core.utils import (
    build_unique_img_urls,
    get_soup,
    get_tags,
    headers_mapping,
    query_mapping,
    run_downloader,
    send_post_to_telegram,
)


async def get_pages_from_pagination(url: str, headers: dict[str, str] | None = None) -> list[str]:
    pagination_query = "div.gtb table tr td a"
    images_pages_query = "div#gdt a"

    source_urls = IndexedSet()
    source_urls.add(url)
    soup = await get_soup(url, headers=headers)
    pagination_set = soup.select(pagination_query)
    images_pages_tags = soup.select(images_pages_query)
    images_links = IndexedSet()

    for image_tag in images_pages_tags:
        href = image_tag.attrs["href"]
        images_links.add(href)

    pages = []

    for a in pagination_set:
        text: str = a.attrs["href"]
        pages.append(text)

    for href in pages:
        source_urls.add(href)

    for url in list(source_urls)[1:]:
        soup = await get_soup(url, headers=headers)
        images_pages_tags = soup.select(images_pages_query)
        for image_tag in images_pages_tags:
            href = image_tag.attrs["href"]
            images_links.add(href)

    return list(images_links)


async def get_sources_for_ehentai(
    sources: list[str],
    entity: str,
    telegraph_client: Telegraph | None = None,
    final_dest: str | pathlib.Path = "",
    save_to_telegraph: bool | None = False,
    **kwargs,
) -> None:
    tqdm_sources_iterable = tqdm(
        sources,
        total=len(sources),
        desc="Retrieving URLs...",
    )
    query, src_attr = query_mapping[entity]
    headers = headers_mapping.get(entity, None)
    page_title = ""
    title_folder_mapping: dict[str, tuple[IndexedSet, pathlib.Path]] = {}
    posts_sent_counter = 0
    titles = IndexedSet()
    all_sources: list[str] = []
    original_folder_path = final_dest
    ordered_unique_img_urls = None
    channel = kwargs.get("channel", "")

    for source_url in tqdm_sources_iterable:
        final_dest = pathlib.Path(str(original_folder_path)) if final_dest else ""
        all_sources.append(source_url)

        urls = [
            *await get_pages_from_pagination(
                url=source_url,
                headers=headers,
            ),
        ]
        image_tags: list[Tag] = []

        for index, url in enumerate(urls):
            tags, soup = await get_tags(
                url,
                headers=headers,
                query=query,
            )
            image_tags.extend(tags or [])
            title_tag = soup.find("title")

            if title_tag:
                page_title = title_tag.get_text(strip=True).split("- E-Hentai")[0].strip().rstrip()

            else:
                page_title = f"Post for {source_url}"

            if index == 0 or not page_title:
                if title_tag:
                    page_title = title_tag.get_text(strip=True).split("- E-Hentai")[0].strip().rstrip()
                else:
                    page_title = f"Post for {source_url}"

            titles.add(page_title)

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
