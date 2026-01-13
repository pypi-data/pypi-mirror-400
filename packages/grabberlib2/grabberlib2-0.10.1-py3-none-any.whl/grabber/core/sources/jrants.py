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


async def get_images_from_pagination(url: str, headers: dict[str, str] | None = None) -> list[str]:
    pagination_query = "div.pgntn-page-pagination-block"
    first_page_query = f"{pagination_query} span.page-numbers.current"
    pages_count_query = f"{pagination_query} a"

    source_urls = IndexedSet()
    source_urls.add(url)
    soup = await get_soup(url, headers=headers)
    pagination_set = soup.select(pages_count_query)

    if not pagination_set:
        return list(source_urls)

    first_page = soup.select(first_page_query)[0]
    first_page_number = int(first_page.text)

    pages = []
    for a in soup.select(pages_count_query):
        text: str = a.get_text()
        if text.isdigit():
            pages.append(int(text))
    last_page_number = max(pages)

    for index in range(first_page_number, last_page_number + 1):
        if index == 1:
            continue

        target_url = f"{url}/{index}"
        source_urls.add(target_url)

    return list(source_urls)


async def get_sources_for_jrant(
    sources: list[str],
    entity: str,
    telegraph_client: Telegraph,
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
    secondary_img_attr = "data-wpfc-original-src"
    headers = headers_mapping.get(entity, None)
    page_title = ""
    title_folder_mapping = {}
    posts_sent_counter = 0
    titles = IndexedSet()
    ordered_unique_img_urls = None
    all_sources: list[str] = []
    original_folder_path = final_dest
    channel = kwargs.get("channel", "")

    for source_url in tqdm_sources_iterable:
        final_dest = pathlib.Path(str(original_folder_path)) if final_dest else ""
        all_sources.append(source_url)

        folder_name = ""
        urls = [*await get_images_from_pagination(url=source_url, headers=headers)]
        image_tags: list[Tag] = []

        for index, url in enumerate(urls):
            tags, soup = await get_tags(
                url,
                headers=headers,
                query=query,
            )
            image_tags.extend(tags or [])

            if index == 0:
                folder_name = soup.find("title").get_text(strip=True).split("– Jrants Fotos")[0].strip().rstrip()
                page_title = folder_name
                titles.add(page_title)

            if not page_title:
                page_title = soup.find("title").get_text(strip=True).split("– Jrants Fotos")[0].strip().rstrip()
                titles.add(page_title)

        ordered_unique_img_urls = await build_unique_img_urls(
            image_tags,
            src_attr,
            secondary_img_attr,
        )
        tqdm_sources_iterable.set_description(f"Finished retrieving images for {page_title}")

        if final_dest:
            final_dest = pathlib.Path(final_dest) / unidecode(f"{page_title} - {entity}")
            if not final_dest.exists():
                final_dest.mkdir(parents=True, exist_ok=True)

            folder_name = f"{page_title}"
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
