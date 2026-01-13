import pathlib
from typing import Any, cast

import httpx
from boltons.setutils import IndexedSet
from bs4 import BeautifulSoup, Tag
from telegraph import Telegraph
from tqdm import tqdm
from unidecode import unidecode
from url_parser import parse_url

from grabber.core.utils import headers_mapping, send_post_to_telegram
from grabber.core.utils.download_upload import downloader

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
}


async def get_all_images_for_url(url: str, headers: dict[str, str]) -> tuple[IndexedSet, ...]:
    images = IndexedSet()
    videos = IndexedSet()
    model_name = url.split("@")[-1]
    base_image_url = "https://www.xpics.me/api/v1/user/{model_name}?page={page}&types[]=image&types[]=gallery&nsfw[]=0"
    base_video_url = "https://www.xpics.me/api/v1/user/{model_name}?page={page}&types[]=video&types[]=gallery&nsfw[]=0"

    counter = 1
    for page in tqdm(range(1, 100)):
        target_image_url = base_image_url.format(model_name=model_name, page=page)
        target_video_url = base_video_url.format(model_name=model_name, page=page)

        try:
            response_images = httpx.get(target_image_url, headers=headers)
            response_videos = httpx.get(target_video_url, headers=headers)
            response_image_data: dict[Any, Any] = response_images.json()
            response_video_data: dict[Any, Any] = response_videos.json()
            response_data = [
                *response_image_data.get("data", {}).get("posts", []),
                *response_video_data.get("data", {}).get("posts", []),
            ]
        except Exception as exc:
            print(f"Error when requesting {target_image_url}: {exc}")
            continue

        if len(response_data) >= 1:
            for post in response_data:
                video_data = post.get("data", {}).get("videos", {})
                if video_data and "mp4" in video_data:
                    video_url: str = video_data["mp4"]
                    video_filename = parse_url(video_url)["file"]
                    video_name_prefix = f"{counter}".zfill(3)
                    videos.add(
                        (
                            video_name_prefix,
                            f"{video_name_prefix}-{video_filename}",
                            f"{video_filename}",
                            video_url,
                        )
                    )
                else:
                    image_data = post["data"]
                    img_filename = parse_url(image_data["url"])["file"]
                    image_name_prefix = f"{counter}".zfill(3)
                    image_url: str = image_data["url"]
                    images.add(
                        (
                            image_name_prefix,
                            f"{image_name_prefix}-{img_filename}",
                            f"{img_filename}",
                            image_url,
                        )
                    )
                counter += 1
        else:
            print(f"There was no response for page {page}")
            break

    return images, videos


async def get_sources_for_xpics(
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
    headers = headers_mapping[entity]
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

        response = httpx.get(
            source_url,
            headers=headers,
            follow_redirects=True,
        )
        soup = BeautifulSoup(response.content, features="lxml")

        page_title = cast(Tag, soup.find("title")).get_text(strip=True).strip().rstrip()
        page_title = page_title.replace("Nude", "").split("porn")[0].strip()
        page_title = unidecode(
            " ".join(
                f"#{part.strip().replace(' ', '').replace('.', '_').replace('-', '_')}"
                for part in page_title.split("/")
            )
        )
        titles.add(page_title)

        image_urls, video_urls = await get_all_images_for_url(source_url, headers)
        ordered_unique_img_urls = IndexedSet(sorted(image_urls, key=lambda x: list(x).pop(0)))
        ordered_unique_img_urls = IndexedSet(a[1:] for a in ordered_unique_img_urls)
        ordered_unique_video_urls = IndexedSet(sorted(video_urls, key=lambda x: list(x).pop(0)))
        ordered_unique_video_urls = IndexedSet(a[1:] for a in ordered_unique_video_urls)

        tqdm_sources_iterable.set_description(f"Finished retrieving images for {page_title}")

        if final_dest:
            final_dest = pathlib.Path(final_dest) / unidecode(f"{page_title} - {entity}")
            if not final_dest.exists():
                final_dest.mkdir(parents=True, exist_ok=True)

            title_folder_mapping[page_title] = (ordered_unique_img_urls, final_dest)

        if save_to_telegraph:
            try:
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
            except Exception:
                print(f"There was an error when trying to send {page_title} - {source_url} to telegram")
            page_title = ""

    if final_dest and ordered_unique_img_urls:
        await downloader(
            titles=list(titles),
            title_folder_mapping=title_folder_mapping,
            headers=headers,
        )
