import pathlib
from urllib.parse import urlparse

import requests
from boltons.setutils import IndexedSet
from telegraph import Telegraph
from tqdm import tqdm
from unidecode import unidecode

from grabber.core.utils import (
    downloader,
    get_tags,
    headers_mapping,
    query_mapping,
    telegraph_uploader,
)


async def get_sources_for_notion(
    sources: list[str],
    entity: str,
    telegraph_client: Telegraph,
    final_dest: str | pathlib.Path = "",
    save_to_telegraph: bool | None = False,
    **kwargs,
) -> None:
    query, src_attr = query_mapping[entity]
    headers = headers_mapping.get(entity, None)
    page_title = ""
    title_folder_mapping = {}
    posts_sent_counter = 0
    titles = []

    if final_dest:
        final_dest = pathlib.Path(final_dest) / unidecode(f"{page_title} - {entity}")
        if not final_dest.exists():
            final_dest.mkdir(parents=True, exist_ok=True)

    tqdm_sources_iterable = tqdm(
        enumerate(sources),
        total=len(sources),
        desc="Retrieving URLs...",
    )

    for idx, source_url in tqdm_sources_iterable:
        image_tags, soup = await get_tags(source_url, headers=headers, query=query, uses_js=True)
        parsed_url = urlparse(source_url)
        base_url = f"https://{parsed_url.netloc}"

        if not page_title:
            page_title = soup.find("title").get_text(strip=True).strip().rstrip()
            titles.append(page_title)

        unique_media_urls = IndexedSet()
        for idx, img_tag in enumerate(image_tags):
            img_src = img_tag.attrs[src_attr].split("?")[0]
            img_name: str = img_src.split("?")[0]
            img_name = img_name.strip().rstrip()
            img_source = f"{base_url}{img_src}"
            resp = requests.get(img_source, allow_redirects=True)
            img_url = resp.url
            unique_media_urls.add((f"{idx + 1}-{img_name}", img_url))

        tqdm_sources_iterable.set_description(f"Finished retrieving images for {page_title}")

        if final_dest:
            folder_name = f"{page_title}"
            # title_dest = final_dest / folder_name / f"{str(uuid.uuid4())}"
            # if not title_dest.exists():
            # title_dest.mkdir(parents=True, exist_ok=True)
            title_folder_mapping[page_title] = (unique_media_urls, title_dest)

        if save_to_telegraph:
            await telegraph_uploader(
                unique_img_urls=unique_media_urls,
                page_title=page_title,
                posts_sent_counter=posts_sent_counter,
                telegraph_client=telegraph_client,
            )
            posts_sent_counter += 1

        page_title = None

    if final_dest:
        await downloader(
            titles=titles,
            title_folder_mapping=title_folder_mapping,
            headers=headers,
        )
