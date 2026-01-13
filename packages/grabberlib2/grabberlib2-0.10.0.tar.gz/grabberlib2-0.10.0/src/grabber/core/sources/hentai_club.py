import pathlib
from urllib.parse import urljoin

from boltons.setutils import IndexedSet
from telegraph import Telegraph
from tqdm import tqdm
from unidecode import unidecode

from grabber.core.utils import (
    build_unique_img_urls,
    downloader,
    get_soup,
    get_tags,
    headers_mapping,
    query_mapping,
    send_post_to_telegram,
)
from grabber.core.utils.download_upload import run_downloader


async def get_pages_from_pagination(
    url: str,
    headers: dict[str, str] | None = None,
) -> list[str]:
    url = urljoin(url, "1/")
    pagination_pages_query = "ol.page-navigator li a"
    posts_query = "div.item-title a.item-link"
    all_posts = set()
    soup = await get_soup(url, headers=headers)
    pages = soup.select(pagination_pages_query)

    counter = set()
    for tag in pages:
        if "»" not in tag.text:
            counter.add(int(tag.text))

    if counter:
        first = min(counter)
        last = max(counter)

        for idx in range(first, last + 1):
            target_page = url.replace("1", str(idx))
            soup = await get_soup(target_page, headers=headers)
            all_posts.update({a.attrs["href"] for a in soup.select(posts_query)})
    else:
        all_posts.update({a.attrs["href"] for a in soup.select(posts_query)})

    return list(all_posts)


async def get_sources_for_hentai_club(
    sources: list[str],
    entity: str,
    telegraph_client: Telegraph | None = None,
    final_dest: str | pathlib.Path = "",
    save_to_telegraph: bool | None = False,
    is_tag: bool | None = False,
    **kwargs,
) -> None:
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

    if is_tag:
        sources = await get_pages_from_pagination(url=sources[0], headers=headers)

    tqdm_sources_iterable = tqdm(
        sources,
        total=len(sources),
        desc="Retrieving URLs...",
    )

    for source_url in tqdm_sources_iterable:
        final_dest = pathlib.Path(str(original_folder_path)) if final_dest else ""
        all_sources.append(source_url)

        image_tags, soup = await get_tags(source_url, headers=headers, query=query)

        page_title = soup.find("title").text.split("-")[0].strip().rstrip()
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
