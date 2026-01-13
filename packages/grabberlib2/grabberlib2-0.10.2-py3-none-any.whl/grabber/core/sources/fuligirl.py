import pathlib

from boltons.setutils import IndexedSet
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


async def get_pages_from_pagination(url: str, headers: dict | None = None) -> list[str]:
    pagination_query = "nav.my-2 div a[rel!='next']"
    pagination_prefix = "?page="

    source_urls = IndexedSet()
    source_urls.add(url)
    soup = await get_soup(url, headers=headers)
    pagination_set = soup.select(pagination_query)
    first_page_tag = pagination_set[0]
    last_page_tag = pagination_set[-1]
    first_page = int(first_page_tag.get_text(strip=True))
    last_page = int(last_page_tag.get_text(strip=True))

    for index in range(first_page, last_page + 1):
        source_urls.add(f"{url}{pagination_prefix}{index}")

    # for a in pagination_set:
    #     source_urls.add(a.attrs["href"])

    return list(source_urls)


async def get_sources_for_fuligirl(
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

        urls = [
            *await get_pages_from_pagination(
                url=source_url,
                headers=headers,
            ),
        ]
        image_tags = []

        for index, url in enumerate(urls):
            tags, soup = await get_tags(
                url,
                headers=headers,
                query=query,
            )
            image_tags.extend(tags or [])
            page_title = soup.find("title").get_text(strip=True)
            second_part = page_title.split("|")[-1].strip()
            page_title = page_title.split("|")[0].split("Page")[0].strip() + second_part

            if index == 0 or not page_title:
                page_title = soup.find("title").get_text(strip=True)
                second_part = page_title.split("|")[-1].strip()
                page_title = page_title.split("|")[0].split("Page")[0].strip() + second_part
                folder_name = f"{page_title}"

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
