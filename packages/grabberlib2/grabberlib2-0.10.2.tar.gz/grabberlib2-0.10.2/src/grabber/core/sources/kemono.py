import asyncio
import pathlib
from typing import Any, cast
from urllib.parse import urlparse

import ftfy
from boltons.setutils import IndexedSet
from bs4 import BeautifulSoup, Tag
from pydoll.browser.chromium import Chrome
from pydoll.browser.options import ChromiumOptions as Options
from telegraph import Telegraph
from tqdm import tqdm
from unidecode import unidecode

from grabber.core.utils import (
    build_unique_img_urls,
    build_unique_video_urls,
    headers_mapping,
    query_mapping,
    run_downloader,
    send_post_to_telegram,
)


async def get_images_from_pagination(url: str, headers: dict[str, str] | None = None) -> tuple[list[Tag], list[Tag]]:
    parsed_url = urlparse(url)
    base_url = f"https://{parsed_url.netloc}"
    pagination_query = "menu a[aria-current='page']"
    images_query = "div.post__files div.post__thumbnail figure a"
    videos_query = "div.post__body ul li div.fluid_video_wrapper video source"
    posts_query = "div.card-list__items article.post-card.post-card--preview a"
    pagination_links = IndexedSet()

    images_tags = IndexedSet()
    videos_tags = IndexedSet()
    sources = IndexedSet()
    pagination_set: set[Tag] = set()
    pagination_links.add(url)
    options = Options()
    options.add_argument("--headless")

    async with Chrome(connection_port=9222, options=options) as browser:
        page = await browser.start()
        await page.go_to(url)
        soup = BeautifulSoup(ftfy.fix_text(await page.page_source), features="lxml")

        if not soup.select(posts_query) or not soup.select(pagination_query):
            await page.refresh()
            page_source = ftfy.fix_text(await page.page_source)
            soup = BeautifulSoup(page_source, features="lxml")

        for a in soup.select(pagination_query):
            a_tag_value = a.get_text(strip=True).strip().rstrip()
            if a_tag_value.isdigit() and a_tag_value != "1":
                pagination_set.add(a)

        posts_tags = soup.select(posts_query)
        for tag in posts_tags:
            href = tag.attrs["href"]
            sources.add(f"{base_url}{href}")

        if pagination_set:
            for page_url in pagination_set:
                link: str = page_url.attrs["href"]
                sources.add(f"{base_url}{link}")

        for link in sources:
            await page.go_to(link)
            # driver.refresh()
            soup = BeautifulSoup(ftfy.fix_text(await page.page_source), features="lxml")
            images_tags.update(*soup.select(images_query))
            videos = soup.select(videos_query)
            if videos:
                videos_tags.update(*[video for video in videos if video is not None and hasattr(video, "attrs")])

    return list(images_tags), list(videos_tags)


async def get_sources_for_kemono(
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
    _, src_attr = query_mapping[entity]
    _ = "div.box div div div a"
    headers = headers_mapping.get(entity, None)
    page_title = ""
    title_folder_mapping = {}
    posts_sent_counter = 0
    titles = IndexedSet()
    ordered_unique_img_urls = None
    all_sources: list[str] = []
    original_folder_path = final_dest
    ordered_unique_video_urls = IndexedSet()
    channel = kwargs.get("channel", "")

    for source_url in tqdm_sources_iterable:
        final_dest = pathlib.Path(str(original_folder_path)) if final_dest else ""
        all_sources.append(source_url)

        if posts_sent_counter in [50, 100, 150, 200, 250]:
            await asyncio.sleep(10)

        image_tags, videos_tags = [
            *await get_images_from_pagination(
                url=source_url,
                headers=headers,
            ),
        ]
        if not image_tags:
            tqdm_sources_iterable.set_postfix_str(f"Error retrieving image URLs for {source_url}. Skipping it..")
            continue
        options = Options()
        options.add_argument("--headless")
        async with Chrome(connection_port=9222, options=options) as browser:
            page = await browser.start()
            await page.go_to(source_url)
            soup = BeautifulSoup(ftfy.fix_text(await page.page_source), features="lxml")

        page_title = cast(Tag, soup.find("title")).get_text(strip=True).strip().rstrip()
        replace_words = ["| Kemono", "Posts of ", "from ", "Fantia", "Patreon", '"']
        for word in replace_words:
            page_title = page_title.replace(word, "")

        page_title = unidecode(
            " ".join(
                f"#{part.strip().replace(' ', '').replace('.', '_').replace('-', '_')}"
                for part in page_title.split("/")
            )
        )
        titles.add(page_title)

        image_tags = sorted(image_tags, key=lambda tag: tag.attrs["href"] if "href" in tag.attrs else tag.attrs["src"])
        ordered_unique_img_urls = await build_unique_img_urls(image_tags, src_attr, "src")

        if videos_tags:
            ordered_unique_video_urls = await build_unique_video_urls(videos_tags, "src")

        tqdm_sources_iterable.set_description(f"Finished retrieving images for {page_title}")

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
