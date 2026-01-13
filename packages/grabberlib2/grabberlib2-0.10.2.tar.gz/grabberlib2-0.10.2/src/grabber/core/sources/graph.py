import asyncio
import pathlib
from typing import Any, cast

from boltons.setutils import IndexedSet
from bs4 import Tag
from telegraph import Telegraph
from tqdm import tqdm
from unidecode import unidecode

from grabber.core.utils import (
    build_unique_img_urls,
    get_tags,
    headers_mapping,
    query_mapping,
    run_downloader,
    send_post_to_telegram,
)


async def get_for_telegraph(
    sources: list[str],
    entity: str,
    telegraph_client: Telegraph,
    final_dest: str | pathlib.Path = "",
    save_to_telegraph: bool | None = False,
    **kwargs: dict[str, Any],
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
    failed_sources: list[str] = []
    ordered_unique_img_urls = None
    unique_video_urls = None
    ordered_unique_video_urls = None
    all_sources: list[str] = []
    original_folder_path = final_dest
    channel = kwargs.get("channel", "")

    for source_url in tqdm_sources_iterable:
        final_dest = pathlib.Path(str(original_folder_path)) if final_dest else ""
        all_sources.append(source_url)

        image_tags, soup = await get_tags(
            source_url,
            headers=headers,
            query=query,
        )

        video_query = "video"
        video_tags, soup = await get_tags(
            source_url,
            headers=headers,
            query=video_query,
        )

        unique_video_urls = IndexedSet()
        for idx, video_tag in enumerate(video_tags):
            video_src = video_tag.attrs["src"]
            video_prefix = f"{idx + 1}".zfill(4)
            video_filename: str = video_src.split(".mp4")[0]
            video_filename = video_filename.strip().rstrip()
            unique_video_urls.add((video_prefix, f"{video_prefix}-{video_filename}", video_src))

        page_title = (
            cast(Tag, soup.find("title"))
            .get_text(strip=True)
            .split("– Telegraph")[0]
            .split("- Telegraph")[0]
            .strip()
            .rstrip()
        )
        page_title = unidecode(
            " ".join(
                f"#{part.strip().replace(' ', '').replace('.', '_').replace('-', '_')}"
                for part in page_title.split("/")
            )
        )
        titles.add(page_title)

        ordered_unique_img_urls = await build_unique_img_urls(image_tags, src_attr)
        if unique_video_urls:
            ordered_unique_video_urls = IndexedSet(sorted(unique_video_urls, key=lambda x: list(x).pop(0)))
            ordered_unique_video_urls = IndexedSet([a[1:] for a in ordered_unique_video_urls])
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
            await asyncio.sleep(5)
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
