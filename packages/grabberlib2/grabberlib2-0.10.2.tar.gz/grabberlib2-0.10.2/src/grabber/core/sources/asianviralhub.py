import pathlib
import tempfile

from aiogram import Bot
from aiogram.types import InputFile, URLInputFile
from aiogram.utils.media_group import MediaGroupBuilder
from telegraph import Telegraph
from tqdm import tqdm

from grabber.core.settings import BOT_TOKEN
from grabber.core.utils import (
    get_tags,
    headers_mapping,
    query_mapping,
)

CHUNK_SIZE = (1024 * 1024) * 10


async def get_sources_for_asianviralhub(
    sources: list[str],
    entity: str,
    telegraph_client: Telegraph,
    final_dest: str | pathlib.Path = "",
    save_to_telegraph: bool | None = False,
    **kwargs,
) -> None:
    query, src_attr = query_mapping[entity]
    headers = headers_mapping.get(entity)
    # headers = {
    #     "Accept": "*/*",
    #     "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    #     "referer": "https://nsfw247.to/",
    # }
    page_title = ""
    downloaded_videos: list[tuple[InputFile | pathlib.Path, str]] = []

    tqdm_sources_iterable = tqdm(
        sources,
        total=len(sources),
        desc="Retrieving URLs...",
    )
    bot = Bot(token=f"{BOT_TOKEN}")
    builder = MediaGroupBuilder()
    temp_dir = tempfile.TemporaryDirectory()

    for source_url in tqdm_sources_iterable:
        video_tags, soup = await get_tags(source_url, headers=headers, query=query)
        page_title = soup.find("title").get_text(strip=True).strip().rstrip()

        # for idx, video_tag in enumerate(video_tags):
        #     video_src = video_tag.attrs[src_attr].split("?")[0]
        #
        #     video_response = requests.get(video_src, stream=True)
        #     file_path = pathlib.Path(f"{temp_dir.name}video.mp4")
        #     with open(file_path, 'wb') as f:
        #         video_response.raw.decode_content = True
        #         shutil.copyfileobj(video_response.raw, f)
        #         downloaded_videos.append((file_path, page_title))
        # for chunk in video_response.iter_content(chunk_size=1024):
        #     if chunk:
        #         f.write(chunk)
        #         f.flush()
        #         downloaded_videos.append((file_path, page_title))

        for video_tag in video_tags:
            video_src = video_tag.attrs[src_attr]
            video_input = URLInputFile(url=video_src, headers=headers, chunk_size=CHUNK_SIZE)
            downloaded_videos.append((video_input, page_title))

    for video_input, page_title in downloaded_videos:
        # video_input = FSInputFile(path=video.as_posix())
        builder.add_video(media=video_input, caption=page_title)
        channel = "@backupcos0000"
        # channel = "@backprn0099"
        tqdm_sources_iterable.set_description(f"Sending video {page_title} to channel {channel}")
        await bot.send_media_group(chat_id=channel, media=builder.build())
