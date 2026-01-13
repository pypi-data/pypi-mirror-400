import pathlib
from typing import cast

from boltons.setutils import IndexedSet
from bs4 import Tag
from telegraph import Telegraph
from tqdm import tqdm
from unidecode import unidecode

from grabber.core.utils import (
    build_unique_img_urls,
    get_pages_from_pagination,
    get_tags,
    headers_mapping,
    query_mapping,
    run_downloader,
    send_post_to_telegram,
)


async def get_sources_for_nudecosplay(
    sources: list[str],
    entity: str,
    telegraph_client: Telegraph,
    final_dest: pathlib.Path | None = None,
    save_to_telegraph: bool | None = False,
    is_tag: bool | None = False,
    limit: int | None = None,
    **kwargs,
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
    split_text_mapping = {
        "nudebird.biz": "- Nude Bird",
        "nudecosplay.biz": "- nudecosplay.biz",
        "hotgirl.biz": "- Hotgirl.biz",
    }
    split_text_with = split_text_mapping[entity]
    post_tags = ""
    ordered_unique_img_urls = None
    all_sources: list[str] = []
    original_folder_path = final_dest
    channel = kwargs.get("channel", "")

    for source_url in tqdm_sources_iterable:
        final_dest = pathlib.Path(str(original_folder_path)) if final_dest else ""
        all_sources.append(source_url)

        if is_tag:
            urls = await get_pages_from_pagination(url=source_url, target="nudecosplay")
            targets = urls[:limit] if limit else urls
            return await get_sources_for_nudecosplay(
                sources=targets,
                entity=entity,
                telegraph_client=telegraph_client,
                final_dest=final_dest,
                save_to_telegraph=save_to_telegraph,
                is_tag=False,
            )

        image_tags, soup = await get_tags(
            source_url,
            headers=headers,
            query=query,
        )
        div_tag: Tag = cast(Tag, soup.find("div", {"class": "jeg_post_tags"}))

        if div_tag:
            a_tags = div_tag.findAll("a", {"rel": "tag"})
            post_tags = ""
            for a_tag in a_tags:
                cleaned_text = a_tag.text.replace(" ", "")
                post_tags += f"#{cleaned_text} "

        page_title = (
            soup.find("title")
            .get_text(strip=True)
            .split(split_text_with)[0]
            .strip()
            .rstrip()
            .split("/nudecosplay.biz/")[0]
        )
        page_title = unidecode(
            " ".join(
                f"#{part.strip().replace(' ', '').replace('.', '_').replace('-', '_')}"
                for part in page_title.split("/")
            )
        )

        titles.add(page_title)

        ordered_unique_img_urls = await build_unique_img_urls(image_tags, src_attr)
        tqdm_sources_iterable.set_description(f"Finished retrieving images for {page_title}")

        if final_dest:
            final_dest = pathlib.Path(final_dest) / unidecode(f"{page_title} - {entity}")
            if not final_dest.exists():
                final_dest.mkdir(parents=True, exist_ok=True)

            title_folder_mapping[page_title] = (ordered_unique_img_urls, final_dest)

        if save_to_telegraph:
            _ = await send_post_to_telegram(
                ordered_unique_img_urls=ordered_unique_img_urls,
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
