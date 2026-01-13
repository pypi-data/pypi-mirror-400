import asyncio
import pathlib
from typing import Any, cast

import cloudscraper
import httpx
import requests
from boltons.setutils import IndexedSet
from bs4 import BeautifulSoup
from telegraph import Telegraph
from tenacity import retry, wait_chain, wait_fixed
from tqdm import tqdm
from unidecode import unidecode
from url_parser import parse_url

from grabber.core.utils import (
    headers_mapping,
    run_downloader,
    send_post_to_telegram,
)

NUMBERS_PATTERN = r"\d+(?:,\d+)*"


@retry(
    wait=wait_chain(
        *[wait_fixed(3) for _ in range(5)]
        + [wait_fixed(7) for _ in range(4)]
        + [wait_fixed(9) for _ in range(3)]
        + [wait_fixed(15)],
    ),
    reraise=True,
)
async def get_response(url: str, headers: dict[str, str]) -> list[dict[str, Any]]:
    scraper = cloudscraper.create_scraper(interpreter="nodejs")
    try:
        response = scraper.get(url=url, headers=headers)
        response.raise_for_status()
        response_data = response.json()
    except requests.exceptions.JSONDecodeError as exc:
        print(f"JSONDecodeError occurred for {url}: {exc}")
        raise
    except requests.HTTPError as exc:
        print(f"Request error occurred for {url}: {exc}")
        raise
    return cast(list[dict[str, Any]], response_data)


async def get_pages_from_pagination(
    url: str,
    headers: dict[str, str],
    max_pages: int,
) -> tuple[IndexedSet, ...]:
    referer_header = {"Referer": url}
    headers.update(referer_header)
    parsed_url: dict[str, Any] = parse_url(url)
    url_file = parsed_url.get("file")

    if url_file is not None:
        model_name = url_file
    else:
        url_path = parsed_url["path"].replace("/", "")
        model_name = url_path
    base_url = "https://picazor.com"
    endpoint_url = "https://picazor.com/api/files/{model_name}/sfiles?page={page_number}"
    page_number = 1
    endpoint = endpoint_url.format(model_name=model_name, page_number=page_number)
    response = await get_response(endpoint, headers=headers)
    response_data: list[dict[str, Any]] = response
    images_tags = IndexedSet()
    videos_tags = IndexedSet()
    video_ids = IndexedSet()
    image_ids = IndexedSet()

    while page_number <= max_pages and response_data:
        for idx, data in enumerate(response_data):
            base_media_url = data["path"]
            if ".mp4" in base_media_url:
                video_url = f"{base_url}{base_media_url}"
                video_id = data["id"]
                if video_id not in video_ids:
                    video_ids.add(video_id)
                    parsed_video_url = parse_url(video_url)
                    image_prefix = f"{idx + 1}".zfill(4)
                    video_filename = parsed_video_url["file"]
                    filename = f"{video_id}-{video_filename}"
                    videos_tags.add((image_prefix, f"{image_prefix}-{filename}", f"{filename}", video_url))
            else:
                image_url = f"{base_url}{base_media_url}"
                image_id = data["id"]
                if image_id not in image_ids:
                    image_ids.add(image_id)
                    parsed_image_url = parse_url(image_url)
                    image_prefix = f"{idx + 1}".zfill(4)
                    image_filename = parsed_image_url["file"]
                    filename = f"{image_id}-{image_filename}"
                    images_tags.add((image_prefix, f"{image_prefix}-{filename}", f"{filename}", image_url))

        page_number += 1
        next_page_url = endpoint_url.format(model_name=model_name, page_number=page_number)

        await asyncio.sleep(0.5)  # To avoid hitting the server too hard
        try:
            response_data = await get_response(url=next_page_url, headers=headers)
        except (Exception, httpx.HTTPStatusError, httpx.RequestError) as exc:
            print(f"Error when requesting {next_page_url}: {exc}")
            continue

    ordered_unique_img_urls = IndexedSet([a[1:] for a in images_tags])
    ordered_unique_video_urls = IndexedSet([a[1:] for a in videos_tags])

    return ordered_unique_img_urls, ordered_unique_video_urls


async def get_sources_for_picazor(
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
    max_pages: int = kwargs.get("max_pages", 50)
    scraper = cloudscraper.create_scraper(interpreter="nodejs")

    for source_url in tqdm_sources_iterable:
        final_dest = pathlib.Path(str(original_folder_path)) if final_dest else ""
        all_sources.append(source_url)

        ordered_unique_img_urls, ordered_unique_video_urls = await get_pages_from_pagination(
            url=source_url,
            headers=headers,
            max_pages=max_pages,
        )
        parsed_url: dict[str, Any] = parse_url(source_url)
        url_file = parsed_url.get("file")

        if url_file is not None:
            model_name = url_file
        else:
            url_path = parsed_url["path"].replace("/", "")
            model_name = url_path

        soup = BeautifulSoup(scraper.get(source_url, headers=headers).content, features="lxml")
        title_query = "div.flex-1 p.text-sm"
        title_result = soup.select(title_query)

        if title_result and title_result[0].get_text(strip=True):
            title_tag = title_result[0]
            page_title = title_tag.get_text(strip=True).replace(",", "/")
        else:
            page_title = model_name
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


"""
scraper = cloudscraper.create_scraper(interpreter='nodejs')

base_url = "httpx://picazor.com"
url_page_1 = "https://picazor.com/api/files/teemori/sfiles?page=1"
page1 = scraper.get(url_page_1)
[d["path"] for d in page1.json()]

['/uploads/may25/sa3/teemori/fansly/bhqpk/teemori-fansly-6h0ds-9.jpg',
 '/uploads/may25/sa3/teemori/fansly/bhqpk/teemori-fansly-enl0f-8.jpg',
 '/uploads/may25/sa3/teemori/fansly/bhqpk/teemori-fansly-29ysw-7.jpg',
 '/uploads/may25/sa3/teemori/fansly/bhqpk/teemori-fansly-sytkf-6.jpg',
 '/uploads/may25/sa3/teemori/fansly/bhqpk/teemori-fansly-zcrer-5.jpg',
 '/uploads/may25/sa3/teemori/fansly/bhqpk/teemori-fansly-bsk8b-4.jpg',
 '/uploads/may25/sa3/teemori/fansly/bhqpk/teemori-fansly-7bbyk-3.jpg',
 '/uploads/may25/sa3/teemori/fansly/bhqpk/teemori-fansly-ju2nw-2.jpg',
 '/uploads/may25/sa3/teemori/fansly/bhqpk/teemori-fansly-93vp3-1.jpg',
 '/uploads/may25/sa3/teemori/fansly/klnil/teemori-fansly-lmryl-4.jpg',
 '/uploads/may25/sa3/teemori/fansly/klnil/teemori-fansly-fbl5a-3.jpg',
 '/uploads/may25/sa3/teemori/fansly/klnil/teemori-fansly-8fkzt-2.jpg']

full image URL will be: f{base_url}{path_from_list_above}

To grab
https://picazor.com/en/maria-bolona
https://picazor.com/en/kiakuromi
https://picazor.com/en/amber-chan
https://picazor.com/en/cami
https://picazor.com/en/joj-838 (with videos)
https://picazor.com/en/rainbunny
https://picazor.com/en/niparat-konyai
https://www.xpics.me/@ramierah
https://picazor.com/en/emma-lvxx
https://picazor.com/en/dollyliney
https://picazor.com/en/misaki-sai
https://picazor.com/en/dollifce


Huges

https://picazor.com/en/lady-melamori
https://picazor.com/en/potatogodzilla-3
https://picazor.com/en/vixenp
https://picazor.com/en/saizneko
https://picazor.com/en/hannapunzell

"""
