import asyncio
import pathlib
from asyncio import as_completed, sleep
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import Any

from boltons.setutils import IndexedSet
from casefy.casefy import snakecase
from telegraph import Telegraph
from telegraph import exceptions as telegraph_exceptions
from tqdm import tqdm

from grabber.core.bot.core import send_message
from grabber.core.settings import AUTHOR_NAME, AUTHOR_URL, MAX_IMAGES_PER_POST, SHORT_NAME, get_media_root

from .constants import DEFAULT_THREADS_NUMBER
from .helpers import print_albums_message, sort_file, split_every


async def upload_file(
    file: pathlib.Path,
    telegraph_client: Telegraph,
    try_again: bool | None = True,
) -> str | None:
    source = None
    try:
        uploaded = telegraph_client.upload_file(file)
    except (
        Exception,
        telegraph_exceptions.TelegraphException,
        telegraph_exceptions.RetryAfterError,
    ) as exc:
        error_message = str(exc)
        if "try again" in error_message.lower() or "retry" in error_message.lower():
            await asyncio.sleep(5)
            if try_again:
                telegraph_client = await get_new_telegraph_client()
                return await upload_file(file=file, telegraph_client=telegraph_client, try_again=False)
        uploaded = None

    if uploaded:
        source = uploaded[0]["src"]

    return source


async def get_new_telegraph_client() -> Telegraph:
    telegraph_factory = Telegraph()
    resp = telegraph_factory.create_account(
        short_name=SHORT_NAME,
        author_name=AUTHOR_NAME,
        author_url=AUTHOR_URL,
        replace_token=True,
    )
    access_token = resp["access_token"]
    telegraph_client = Telegraph(access_token=access_token)
    return telegraph_client


async def telegraph_uploader(
    unique_img_urls: IndexedSet,
    page_title: str,
    posts_sent_counter: int = 0,
    telegraph_client: Telegraph | None = None,
    tqdm_iterable: tqdm = None,
    entity: str | None = "",
    send_to_telegram: bool | None = True,
    channel: str | None = "",
    **kwargs: Any,
) -> tuple[bool, list[str]]:
    was_successful = False

    if telegraph_client is None:
        telegraph_client = await get_new_telegraph_client()

    posts: list[str] = []
    tqdm_iterable.set_description(f"Creating Telegraph post for {page_title}...")
    html_post = await create_html_template(unique_img_urls, entity=entity)
    tqdm_iterable.set_description(f"Uploading to Telegraph: {page_title}...")
    post_url = await create_page(
        title=page_title,
        html_content=html_post,
        tqdm_iterable=tqdm_iterable,
        telegraph_client=telegraph_client,
    )
    channels_sent: list[str] = [""]

    if not post_url:
        tqdm_iterable.set_description(f"Failed to create post for {page_title}")
        was_successful, channels_sent = False, [""]
        return was_successful, channels_sent

    telegraph_post = f"{page_title} - {post_url}"
    tqdm_iterable.set_description(f"Successfully created Telegraph post for {page_title}: {post_url}")
    posts.append(telegraph_post)

    if posts_sent_counter == 10:
        await asyncio.sleep(10)

    if send_to_telegram:
        tqdm_iterable.set_description(f"Sending Telegraph post to Telegram: {page_title}...")
        try:
            was_successful, channels_sent = await send_message(
                post_text=telegraph_post,
                retry=True,
                posts_counter=posts_sent_counter,
                tqdm_iterable=tqdm_iterable,
                image_urls=set(unique_img_urls),
                entity=entity,
                channel=channel,
            )
            tqdm_iterable.set_description(f"Successfully sent Telegraph post to Telegram: {page_title}")
        except Exception as exc:
            tqdm_iterable.set_description(f"Error sending Telegraph post to Telegram: {page_title}: {exc}")
            tqdm_iterable.set_description("Retrying...")
            await asyncio.sleep(20)
            was_successful, channels_sent = await send_message(
                post_text=telegraph_post,
                retry=True,
                posts_counter=posts_sent_counter,
                tqdm_iterable=tqdm_iterable,
                image_urls=set(unique_img_urls),
                entity=entity,
                channel=channel,
            )
    else:
        albums_dir = pathlib.Path.home() / ".albums_data"
        albums_dir.mkdir(parents=True, exist_ok=True)
        albums_file = albums_dir / "pages.txt"

        with albums_file.open("w") as f:
            _ = f.write("\n".join(posts))

        albums_links = albums_file.read_text().split("\n")
        await print_albums_message(albums_links)

    return was_successful, channels_sent


async def upload_folders_to_telegraph(
    folder_name: pathlib.Path | None,
    telegraph_client: Telegraph,
    limit: int | None = 0,
    send_to_channel: bool | None = False,
) -> None:
    folders = []

    if folder_name:
        root = get_media_root() / folder_name
        folders += [f for f in list(root.iterdir()) if f.is_dir()]
    else:
        root_folders = [folder for folder in get_media_root().iterdir() if folder.is_dir()]
        for folder in root_folders:
            if folder.is_dir():
                nested_folders = [f for f in folder.iterdir() if f.is_dir()]
                if nested_folders:
                    folders += nested_folders
                else:
                    folders = root_folders

    futures_to_folder = {}
    selected_folders = folders[:limit] if limit else folders
    with ThreadPoolExecutor(max_workers=DEFAULT_THREADS_NUMBER) as executor:
        future_counter = 0
        for folder in selected_folders:
            partial_upload = partial(
                upload_to_telegraph,
                folder,
                send_to_telegram=send_to_channel,
                telegraph_client=telegraph_client,
            )
            future = executor.submit(partial_upload)
            futures_to_folder[future] = folder
            future_counter += 1

        page_urls: list[tuple[str, str]] = []
        for future in tqdm(
            as_completed(futures_to_folder),
            total=future_counter,
            desc=f"Uploading {future_counter} albums to Telegraph...",
        ):
            result = future.result()
            page_urls.append(result)

        content = "\n".join([f"{page_url}" for page_url in page_urls])
        print(content)


async def create_page(
    title: str,
    html_content: str,
    tqdm_iterable: tqdm,
    telegraph_client: Telegraph,
    try_again: bool | None = True,
) -> str | None:
    source = None
    try:
        tqdm_iterable.set_description(f"Creating Telegraph page for {title}...")
        page = telegraph_client.create_page(
            title=title,
            html_content=html_content,
            author_name=AUTHOR_NAME,
            author_url=AUTHOR_URL,
        )
        source = page["url"]
        tqdm_iterable.set_description(f"Successfully created Telegraph page for {title}: {source}")
    except (
        Exception,
        telegraph_exceptions.TelegraphException,
        telegraph_exceptions.RetryAfterError,
    ) as exc:
        error_message = str(exc)
        tqdm_iterable.set_description(f"Error creating Telegraph page for {title}: {error_message}")
        await sleep(5)
        if try_again:
            telegraph_client = await get_new_telegraph_client()
            return await create_page(
                title=title,
                html_content=html_content,
                tqdm_iterable=tqdm_iterable,
                telegraph_client=telegraph_client,
                try_again=False,
            )

    return source


async def create_html_template(image_tags: IndexedSet, entity: str | None = "") -> str:
    if entity == "e-hentai.org":
        img_html_template = """<figure contenteditable="false"><img style="height:722px;width:1280px" src="{file_path}" data-original="{file_path}"><figcaption dir="auto" class="editable_text" data-placeholder="{title}"></figcaption></figure>"""
    elif entity == "buondua.com":
        img_html_template = """<figure contenteditable="false"><img loading="lazy" referrerpolicy="strict-origin" width="1024" height="1365" src="{file_path}"><figcaption dir="auto" class="editable_text" data-placeholder="{title}"></figcaption></figure>"""
    else:
        img_html_template = """<figure contenteditable="false"><img src="{file_path}" data-original="{file_path}"><figcaption dir="auto" class="editable_text" data-placeholder="{title}"></figcaption></figure>"""

    video_html_template = (
        '<video src="{video_path}" preload="metadata" controls="controls" poster="{video_poster}" muted></video>'
    )

    template_tags: list[str] = []
    for title, poster, media_src in image_tags:
        if "mp4" in media_src and entity != "fapello.su":
            template_tags.append(video_html_template.format(title=title, video_path=media_src, video_poster=poster))
        else:
            template_tags.append(img_html_template.format(file_path=media_src, title=title))

    html_post = f"Source: <a href='{entity}'>{entity}</a>\n" if entity else ""
    html_post += "\n".join(template_tags)
    return html_post


async def upload_to_telegraph(
    folder: pathlib.Path,
    telegraph_client: Telegraph,
    page_title: str | None = "",
    send_to_telegram: bool | None = False,
) -> str:
    files = sorted(list(folder.iterdir()), key=sort_file)
    title = page_title or folder.name
    title = title.strip().rstrip()

    contents = []
    files_urls = []
    html_template = """<figure contenteditable="false"><img src="{file_path}"><figcaption dir="auto" class="editable_text" data-placeholder="{title}"></figcaption></figure>"""

    uploaded_files_url_path = pathlib.Path(f"{snakecase(title)}.txt")
    if uploaded_files_url_path.exists() and uploaded_files_url_path.stat().st_size > 0:
        contents = uploaded_files_url_path.read_text().split("\n")
    else:
        iterable_files = tqdm(
            files,
            total=len(files),
            desc=f"Uploading files for {folder.name}",
            leave=False,
        )
        image_title = f"{title}"
        for file in iterable_files:
            file_url = await upload_file(file, telegraph_client=telegraph_client)
            if not file_url:
                continue
            files_urls.append(file_url)
            contents.append(html_template.format(file_path=file_url, title=image_title))

    if contents:
        content = "\n".join(contents)
        try:
            page_url = create_page(
                title=title,
                html_content=content,
                telegraph_client=telegraph_client,
            )
        except telegraph_exceptions.TelegraphException as exc:
            return f"Error: {exc} - {title} - {folder}"

        post = f"{title} - {page_url}"

        if send_to_telegram:
            await send_message(post, image_urls=files_urls)

        pages_file = get_media_root() / "assets/pages.txt"

        if not pages_file.exists():
            pages_file.touch(exist_ok=True)

        with open(pages_file, "a") as f:
            f.write(f"{post}\n")

        return post

    return "No content, please try again later"


async def send_post_to_telegram(
    page_title: str,
    ordered_unique_img_urls: IndexedSet,
    posts_sent_counter: int,
    telegraph_client: Telegraph | None,
    tqdm_sources_iterable: tqdm,
    all_sources: list[str] | None,
    source_url: str,
    ordered_unique_video_urls: IndexedSet | None = None,
    entity: str | None = "",
    send_to_telegram: bool | None = True,
    channel: str | None = "",
    **kwargs: Any,
) -> list[str] | None:
    if not all_sources:
        all_sources = []

    total_imgs = len(ordered_unique_img_urls)
    videos_chunk_size = 2

    match total_imgs:
        case total_imgs if total_imgs in list(range(100, 150)):
            chunk_size = 50
        case total_imgs if total_imgs in list(range(150, 200)):
            chunk_size = 55
        case total_imgs if total_imgs in list(range(200, 250)):
            chunk_size = 60
        case total_imgs if total_imgs in list(range(250, 300)):
            chunk_size = 65
        case _:
            chunk_size = 70

    tqdm_sources_iterable.set_description(f"Uploading to Telegraph in chunks of {chunk_size} images...")

    if len(ordered_unique_img_urls) >= MAX_IMAGES_PER_POST:
        async for chunk in split_every(chunk_size, ordered_unique_img_urls):
            _, _ = await telegraph_uploader(
                unique_img_urls=IndexedSet(chunk),
                page_title=page_title,
                posts_sent_counter=posts_sent_counter,
                telegraph_client=telegraph_client,
                tqdm_iterable=tqdm_sources_iterable,
                entity=entity,
                send_to_telegram=send_to_telegram,
                channel=channel,
            )
            posts_sent_counter += 1
            tqdm_sources_iterable.set_description("Waiting 1 seconds before next chunk upload...")
            await asyncio.sleep(1)
    else:
        _, _ = await telegraph_uploader(
            unique_img_urls=IndexedSet(ordered_unique_img_urls),
            page_title=page_title,
            posts_sent_counter=posts_sent_counter,
            telegraph_client=telegraph_client,
            tqdm_iterable=tqdm_sources_iterable,
            entity=entity,
            send_to_telegram=send_to_telegram,
            channel=channel,
        )

    if ordered_unique_video_urls is not None:
        async for chunk in split_every(videos_chunk_size, ordered_unique_video_urls):
            _, _ = await telegraph_uploader(
                unique_img_urls=IndexedSet(chunk),
                page_title=page_title,
                posts_sent_counter=posts_sent_counter,
                telegraph_client=telegraph_client,
                tqdm_iterable=tqdm_sources_iterable,
                entity=entity,
                send_to_telegram=send_to_telegram,
                channel=channel,
            )
            posts_sent_counter += 1
            tqdm_sources_iterable.set_description("Waiting 1 seconds before next chunk upload...")
            await asyncio.sleep(1)

    return all_sources
