import pathlib
from typing import Any, cast

import httpx
from boltons.setutils import IndexedSet
from bs4 import BeautifulSoup, Tag
from telegraph import Telegraph
from tqdm import tqdm
from unidecode import unidecode
from url_parser import get_base_url, parse_url

from grabber.core.utils import (
    get_tags,
    headers_mapping,
    query_mapping,
    run_downloader,
    send_post_to_telegram,
)


async def get_all_images_tags(
    url: str,
    query: str,
    headers: dict[str, str],
) -> IndexedSet:
    images_tags = IndexedSet()
    base_url = get_base_url(url)
    soup = BeautifulSoup(httpx.get(url, headers=headers).content, features="lxml")
    tags = soup.select(query)
    first_tag = tags[0]
    image_src = first_tag.attrs["src"]
    parsed_image_src = parse_url(image_src)
    image_filename = parsed_image_src["file"]
    last_image_counter_str = image_filename.split("/")[-1].split("_")[1]
    model_name = image_filename.split("/")[-1].split("_")[0]
    image_counter = int(last_image_counter_str)
    image_base_url = "{base_url}{url_dir}{image_filename}"

    for image_counter in range(1, image_counter + 1):
        image_prefix = f"{image_counter}".zfill(4)
        img_filename = f"{model_name}_{image_prefix}.jpg"
        image_url = image_base_url.format(
            base_url=base_url,
            url_dir=parsed_image_src["dir"],
            image_filename=img_filename,
        )
        images_tags.add((image_prefix, f"{image_prefix}-{img_filename}", f"{img_filename}", image_url))

    ordered_unique_img_urls = IndexedSet(sorted(images_tags, key=lambda x: list(x).pop(0)))
    ordered_unique_img_urls = IndexedSet([a[1:] for a in ordered_unique_img_urls])

    return ordered_unique_img_urls


async def get_sources_for_fapomania(
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
    all_sources: list[str] = []
    original_folder_path = final_dest
    channel = kwargs.get("channel", "")

    for source_url in tqdm_sources_iterable:
        final_dest = pathlib.Path(str(original_folder_path)) if final_dest else ""

        ordered_unique_img_urls = await get_all_images_tags(
            url=source_url,
            headers=headers,
            query=query,
        )

        _, soup = await get_tags(
            source_url,
            headers=headers,
            query=query,
        )
        page_title = cast(Tag, soup.find("title")).get_text(strip=True).strip().rstrip()
        page_title = page_title.split("- Fapomania")[0].split("Nude")[0].replace("https:", "")
        page_title = unidecode(
            " ".join(
                f"#{part.strip().replace(' ', '').replace('.', '_').replace('-', '_')}"
                for part in page_title.split("/")
            )
        )
        titles.add(page_title)
        tqdm_sources_iterable.set_description(f"Finished retrieving images for {page_title}")

        if final_dest:
            final_dest = pathlib.Path(final_dest) / unidecode(f"{page_title} - {entity}")
            if not final_dest.exists():
                final_dest.mkdir(parents=True, exist_ok=True)
            title_folder_mapping[page_title] = (ordered_unique_img_urls, final_dest)

        if save_to_telegraph:
            result = await send_post_to_telegram(
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
            all_sources.extend(result or [])
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
