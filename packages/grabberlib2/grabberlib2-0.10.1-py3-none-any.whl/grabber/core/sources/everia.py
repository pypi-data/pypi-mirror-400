import pathlib
from typing import Any
from urllib.parse import urljoin, urlparse

from boltons.setutils import IndexedSet
from bs4.element import Tag
from telegraph import Telegraph
from tqdm import tqdm
from unidecode import unidecode

from grabber.core.utils import (
    build_unique_img_urls,
    get_soup,
    get_tags,
    headers_mapping,
    run_downloader,
    send_post_to_telegram,
)


async def get_pages_from_pagination(url: str) -> list[str]:
    parsed_url = urlparse(url)
    base_url = f"https://{parsed_url.netloc}"

    pagination_pages_query = "div.mainleft ul.page-numbers a.page-numbers"
    articles_from_pagination_query = "div.mainleft a"
    next_page_url_base = f"{url}/page/"
    source_urls = IndexedSet()

    first_page = await get_soup(url)
    articles = set(first_page.select(articles_from_pagination_query))
    pages = first_page.select(pagination_pages_query)

    if pages:
        pages_links: set[str] = set()
        last_page = pages[-2]
        number_last_page = last_page.text
        for idx in range(2, int(number_last_page) + 1):
            pages_links.add(f"{next_page_url_base}{idx}")

        for link in pages_links:
            soup = await get_soup(link)
            articles.update(set(soup.select(articles_from_pagination_query)))

    for a_tag in articles:
        if a_tag is not None and a_tag.attrs["href"] not in source_urls:
            href = a_tag.attrs["href"]
            link = urljoin(base_url, href)
            source_urls.add(link)

    return list(source_urls)


async def get_sources_for_everia(
    sources: list[str],
    entity: str,
    telegraph_client: Telegraph,
    final_dest: str | pathlib.Path = "",
    save_to_telegraph: bool | None = False,
    **kwargs: dict[str, Any],
) -> None:
    is_tag = kwargs.get("is_tag", False)
    soup_queries = [
        ("figure.wp-block-image.size-large img", "src"),
        ("div.separator a", "href"),
        ("div.divone div.mainleft img", "src"),
        ("div.divone div.mainleft img", "data-original"),
    ]
    query, src_attr = soup_queries[0]
    headers = headers_mapping.get(entity, None)
    page_title = ""
    title_folder_mapping: dict[str, tuple[IndexedSet, pathlib.Path]] = {}
    posts_sent_counter = 0
    titles = IndexedSet()
    image_tags: list[Tag] = []
    failed_sources: list[str] = []
    ordered_unique_img_urls = None
    all_sources: list[str] = []
    original_folder_path = final_dest
    channel = kwargs.get("channel", "")

    if is_tag:
        sources = list(await get_pages_from_pagination(sources[0]))

    tqdm_sources_iterable = tqdm(
        sources,
        total=len(sources),
        desc="Retrieving URLs...",
    )

    for source_url in tqdm_sources_iterable:
        final_dest = pathlib.Path(str(original_folder_path)) if final_dest else ""
        all_sources.append(source_url)

        for query, src_attr in soup_queries:
            image_tags, soup = await get_tags(source_url, headers=headers, query=query)
            page_title = (
                soup.find("title").get_text(strip=True).split("-")[0].split("– EVERIA.CLUB")[0].strip().rstrip()
            )
            titles.add(page_title)

            if image_tags:
                if entity == "www.everiaclub.com":
                    src_attr = "data-original"
                break

        if not image_tags:
            print(f"Could not retrieve images from {source_url}")
            failed_sources.append(source_url)
            continue

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

    if failed_sources:
        print("Failed sources:")
        for source in failed_sources:
            print(source)
