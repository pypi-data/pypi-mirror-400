import asyncio

from aiogram import Bot
from aiogram.types import URLInputFile
from aiogram.utils.media_group import MediaGroupBuilder
from tqdm import tqdm

from grabber.core.settings import BOT_TOKEN


async def send_message(
    post_text: str,
    image_urls: set[tuple[str, str]] | None = None,
    channel: str | None = "@fans_posting",
    retry: bool | None = False,
    posts_counter: int = 0,
    retry_counter: int = 0,
    sleep_time: int | None = 0,
    tqdm_iterable: tqdm | None = None,
    send_images: bool | None = False,
    entity: str | None = "",
) -> tuple[bool, list[str]]:
    was_successful = False
    post_images: set[URLInputFile] = set()
    # channels = CHANNELS
    # channel = "@costriage"
    cosplay_sources = [
        "4kup.net",
        "bestgirlsexy.com",
        "buondua.com",
        "cosplaytele.com",
        "cosxuxi.club",
        "cup2d.com",
        "e-hentai.org",
        "en.jrants.com",
        "en.taotu.org",
        "fuligirl.top",
        "happy.5ge.net",
        "hotgirl.asia",
        "hotgirl.biz",
        "hotgirlchina.com",
        "imgcup.com",
        "jrants.com",
        "en.jrants.com",
        "misskon.com",
        "nudebird.biz",
        "nudecosplay.biz",
        "nudecosplaygirls.com",
        "tokyocafe.org",
        "ugirls.pics",
        "www.4khd.com",
        "www.everiaclub.com",
        "www.hentaiclub.net",
        "www.hotgirl2024.com",
        "www.lovecos.net",
        "www.nncos.com",
        "www.xasiat.com",
        "xiunice.com",
        "xiuren.biz",
        "xlust.org",
        "youwu.lol",
    ]

    if not channel:
        channel = "@fans_posting"

    # if entity in ["www.erome.com", "erome.com", "es.erome.com"]:
    #     # channel = "@erome0000"
    #     channel = "@fans_posting"
    # elif entity in ["nudogram.com", "dvir.ru"]:
    #     # channel = "@nudogramposts0000"
    #     # channel = "@mycosplayposts0000"
    #     channel = "@fans_posting"
    # elif entity in ["fapello.com", "fapeza.com"]:
    #     # channel = "@fapello0000"
    #     channel = "@fans_posting"
    # elif entity in cosplay_sources:
    #     # channel = "@cosplayerscollection0000"
    #     channel = "@fans_posting"
    # elif entity == "custom":
    #     # channel = "@fapello0000"
    #     channel = "@fans_posting"

    channels = [channel]
    # channels = ["@bestcosplayersever"]
    # channel = "@yuuhui0099"

    if tqdm_iterable is not None:
        console_printer = tqdm_iterable.set_description
    else:
        console_printer = print

    if image_urls and send_images:
        counter = 1

        for image_filename, image_src in image_urls:
            if "?w=" in image_src:
                image_src = image_src.split("?w=")[0]

            post_images.add(URLInputFile(image_src, filename=image_filename))

            if counter >= 6:
                break
            counter += 1

    try:
        bot = Bot(token=f"{BOT_TOKEN}")
        async with bot.context():
            if post_images:
                builder = MediaGroupBuilder(caption=post_text)
                for image in post_images:
                    builder.add_photo(media=image)

                for c in channels:
                    _ = await bot.send_media_group(chat_id=c, media=builder.build())
                    console_printer(f"Post sent to the channel {c}: {post_text}")
            else:
                for c in channels:
                    _ = await bot.send_message(chat_id=c, text=post_text)
                    console_printer(f"Post sent to the channel {c}: {post_text}")
            was_successful = True
    except Exception as exc:
        console_printer(f"Error sending post {post_text} to channel: {exc}")
        sleep_time = 1
        if entity == "leakgallery.com":
            retry_counter += 1
            await asyncio.sleep(sleep_time)
            console_printer(f"Retry number {retry_counter} sending post {post_text} to channel")
            print(f"Retry number {retry_counter} sending post {post_text} to channel")

            _ = await send_message(
                post_text=post_text,
                channel=channel,
                retry=retry and retry_counter <= 3,
                posts_counter=posts_counter,
                retry_counter=retry_counter,
                sleep_time=sleep_time,
                image_urls=image_urls,
            )
        elif retry or posts_counter >= 15:
            retry_counter += 1
            await asyncio.sleep(sleep_time)
            console_printer(f"Retry number {retry_counter} sending post {post_text} to channel")
            print(f"Retry number {retry_counter} sending post {post_text} to channel")

        _ = await send_message(
            post_text=post_text,
            channel=channel,
            retry=retry and retry_counter <= 50,
            posts_counter=posts_counter,
            retry_counter=retry_counter,
            sleep_time=sleep_time,
            image_urls=image_urls,
        )

    return was_successful, channels
