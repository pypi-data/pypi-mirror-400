import pathlib
from typing import Any

from boltons.setutils import IndexedSet
from telegraph import Telegraph
from tqdm import tqdm
from unidecode import unidecode

from grabber.core.utils import (
    headers_mapping,
    run_downloader,
    send_post_to_telegram,
)
from grabber.core.utils.constants import query_mapping
from grabber.core.utils.media import build_unique_img_urls
from grabber.core.utils.scraper import get_tags

NUMBERS_PATTERN = r"\d+(?:,\d+)*"


# @retry(
#     wait=wait_chain(
#         *[wait_fixed(3) for _ in range(5)]
#         + [wait_fixed(7) for _ in range(4)]
#         + [wait_fixed(9) for _ in range(3)]
#         + [wait_fixed(15)],
#     ),
#     reraise=True,
# )
# async def get_tags(
#     url: str,
#     query: str,
#     headers: dict[str, Any] | None = None,
#     uses_js: bool | None = False,
#     should_retry: bool | None = True,
#     bypass_cloudflare: bool | None = False,
# ) -> tuple[list[Tag], BeautifulSoup]:
#     """Wait 3s for 5 attempts
#     7s for the next 4 attempts
#     9s for the next 3 attempts
#     then 15 for all attempts thereafter
#     """
#     async with Chrome() as driver:
#         tab = await driver.start()
#         await tab.enable_auto_solve_cloudflare_captcha()
#         await tab.go_to(url)
#         await asyncio.sleep(5)
#         soup = BeautifulSoup(driver.page_source, features="lxml")
#         tags = soup.select(query)
#         if not tags and should_retry:
#             driver.refresh()
#             await asyncio.sleep(5)
#             soup = BeautifulSoup(driver.page_source, features="lxml")
#             tags = soup.select(query)
#             if not tags:
#                 print("Page not rendered properly. Retrying one more time...")
#                 return await get_tags(
#                     url=url,
#                     query=query,
#                     headers=headers,
#                     uses_js=uses_js,
#                     should_retry=False,
#                 )
#     else:
#         soup = await get_soup(target_url=url, headers=headers)
#         tags = soup.select(query)
#
#     return tags, soup


async def get_sources_for_chunmomo(
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
    query, src_attr = query_mapping[entity]

    for source_url in tqdm_sources_iterable:
        final_dest = pathlib.Path(str(original_folder_path)) if final_dest else ""
        all_sources.append(source_url)

        image_tags, soup = await get_tags(
            url=source_url,
            query=query,
            headers=headers,
            max_pages=max_pages,
            bypass_cloudflare=True,
        )
        ordered_unique_img_urls = await build_unique_img_urls(image_tags, src_attr)
        page_title = soup.find("title").get_text(strip=True).split("–")[0].replace("_", "")
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
