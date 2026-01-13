import pathlib
from typing import Any, cast

import httpx
from boltons.setutils import IndexedSet
from bs4 import BeautifulSoup, Tag
from telegraph import Telegraph
from tenacity import retry, retry_if_exception_type, wait_chain, wait_fixed
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


@retry(
    wait=wait_chain(
        *[wait_fixed(3) for _ in range(5)]
        + [wait_fixed(7) for _ in range(4)]
        + [wait_fixed(9) for _ in range(3)]
        + [wait_fixed(15)],
    ),
    reraise=True,
    retry=retry_if_exception_type(httpx.ReadTimeout),
)
async def get_response(
    url: str,
) -> httpx.Response:
    """Wait 3s for 5 attempts
    7s for the next 4 attempts
    9s for the next 3 attempts
    then 15 for all attempts thereafter
    """
    async with httpx.AsyncClient(http2=True) as client:
        r = await client.get(url=url)

    if r.status_code >= 300:
        raise Exception(f"Not able to retrieve {url}: {r.status_code}\n")

    return r


async def get_pages_from_pagination(
    url: str,
    query: str,
    src_attr: str,
    headers: dict[str, str] | None = None,
) -> IndexedSet:
    images_tags = IndexedSet()
    base_url = get_base_url(url)
    response = await get_response(url=url)
    page_content = response.content
    soup = BeautifulSoup(page_content, features="lxml")
    first_tag = soup.select(query)[0]
    image_src = first_tag.attrs[src_attr]
    parsed_image_src = parse_url(image_src)
    image_filename = parsed_image_src["file"]
    last_image_counter_str = image_filename.split("/")[-1].split("_")[1]
    model_name = image_filename.split("/")[-1].split("_")[0]
    image_url_dir = parsed_image_src["dir"]
    image_counter = int(last_image_counter_str.split(".")[0])
    image_base_url = "{base_url}{url_dir}{image_filename}"
    image_base_url = "{base_url}{url_dir}{image_filename}"

    for image_counter in range(1, image_counter + 1):
        image_prefix = f"{image_counter}".zfill(4)
        img_filename = f"{model_name}_{image_prefix}.jpg"
        image_url = image_base_url.format(
            base_url=base_url,
            url_dir=image_url_dir,
            image_filename=img_filename,
        )
        images_tags.add((image_prefix, f"{image_prefix}-{img_filename}", f"{img_filename}", image_url))

    ordered_unique_img_urls = IndexedSet([a[1:] for a in images_tags])

    return ordered_unique_img_urls


async def get_sources_for_fapello_pics(
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
        soup = await get_soup(
            target_url=source_url,
            headers=headers,
        )
        first_link_tag = soup.select_one(first_link_tag_query)

        if first_link_tag is None:
            continue

        ordered_unique_img_urls = await get_pages_from_pagination(
            url=source_url,
            headers=headers,
            query=query,
            src_attr=src_attr,
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
