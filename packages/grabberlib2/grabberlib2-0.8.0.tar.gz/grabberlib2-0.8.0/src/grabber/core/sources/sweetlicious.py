import asyncio
import pathlib
from typing import cast

from aiogram import Bot, exceptions
from aiogram.types import InputFile, URLInputFile
from aiogram.utils.media_group import MediaGroupBuilder
from bs4 import Tag
from telegraph import Telegraph
from tqdm import tqdm

from grabber.core.settings import BOT_TOKEN
from grabber.core.utils import (
    build_unique_img_urls,
    get_tags,
    headers_mapping,
    query_mapping,
    send_post_to_telegram,
    split_every,
)

CHUNK_SIZE = (1024 * 1024) * 10


async def get_sources_for_sweetlicious(
    sources: list[str],
    entity: str,
    telegraph_client: Telegraph,
    final_dest: str | pathlib.Path = "",
    save_to_telegraph: bool | None = False,
    **kwargs: dict[str, str],
) -> None:
    query, src_attr = query_mapping[entity]
    headers = headers_mapping.get(entity)
    page_title = ""
    posts_sent_counter = 0
    downloaded_videos: list[tuple[InputFile | pathlib.Path, str]] = []
    images_query = "div.article__entry.entry-content div.gallery dl.gallery-item dt img"
    images_src_attr = "src"
    tqdm_sources_iterable = tqdm(
        sources,
        total=len(sources),
        desc="Retrieving URLs...",
    )
    bot = Bot(token=f"{BOT_TOKEN}")
    ordered_unique_img_urls = None
    all_sources: list[str] = []
    original_folder_path = final_dest
    channel = kwargs.get("channel", "")

    for source_url in tqdm_sources_iterable:
        final_dest = pathlib.Path(str(original_folder_path)) if final_dest else ""
        all_sources.append(source_url)

        image_tags, soup = await get_tags(
            source_url,
            headers=headers,
            query=images_query,
        )
        video_tags, soup = await get_tags(source_url, headers=headers, query=query)
        page_title = cast(Tag, soup.find("title")).get_text().split("- Sweetlicious")[0].strip().rstrip()

        for video_tag in video_tags:
            video_src = video_tag.attrs[src_attr]
            video_input = URLInputFile(url=video_src, headers=headers, chunk_size=CHUNK_SIZE)
            downloaded_videos.append((video_input, page_title))

        if image_tags:
            ordered_unique_img_urls = await build_unique_img_urls(image_tags, images_src_attr)
            tqdm_sources_iterable.set_description(f"Finished retrieving images for {page_title}")

            if save_to_telegraph:
                _ = await send_post_to_telegram(
                    ordered_unique_img_urls=ordered_unique_img_urls,
                    page_title=page_title,
                    telegraph_client=telegraph_client,
                    posts_sent_counter=posts_sent_counter,
                    tqdm_sources_iterable=tqdm_sources_iterable,
                    all_sources=all_sources,
                    source_url=source_url,
                )
            page_title = ""

    tqdm_sources_iterable.set_description(f"Sending {len(downloaded_videos)} videos to Telegram")
    async for videos_chunk in split_every(3, downloaded_videos):
        builder = MediaGroupBuilder()
        for video_input, page_title in videos_chunk:
            builder.add_video(media=video_input, caption=page_title)
        # channel = "@backupcos0000"
        # channel = "@backprn0099"
        channel = "@costriage"
        tqdm_sources_iterable.set_description(f"Sending video {page_title} to channel {channel}")
        try:
            _ = await bot.send_media_group(chat_id=channel, media=builder.build())
        except exceptions.TelegramRetryAfter as exc:
            sleep_time = exc.retry_after
            _ = await asyncio.sleep(sleep_time)
            _ = await bot.send_media_group(chat_id=channel, media=builder.build())
        except exceptions.TelegramEntityTooLarge as exc:
            print(f"Error: {exc}")
            _ = await asyncio.sleep(10)
            continue
        else:
            channels_sent = [channel]
            for source_url in sources:
                for channel in channels_sent:
                    data = {
                        "url": source_url,
                        "title": page_title,
                        "channel": channel,
                    }
                    if not await repository.was_already_posted_in_channel(url=source_url, channel=channel):
                        _ = await repository.create(attributes=data)
