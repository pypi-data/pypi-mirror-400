import abc
import pathlib
from typing import TypeVar, cast
from urllib import parse

from boltons.setutils import IndexedSet
from bs4 import BeautifulSoup, Tag
from telegraph import Telegraph
from tqdm import tqdm

from src.grabber.core.settings import TELEGRAPH_TOKEN
from src.grabber.core.utils import (
    downloader,
    get_tags,
    split_every,
    telegraph_uploader,
)

from .constants import HEADERS_MAPPING, PAGE_TITLE_SPLIT_MAPPING, QUERY_MAPPING

T = TypeVar("T", bound="BaseExtractor")


class BaseExtractor(abc.ABC):
    def __init__(
        self,
        sources: list[str],
        final_dest: str | pathlib.Path = "",
        is_tag: bool = False,
        limit: int | None = None,
        save_to_telegraph: bool | None = False,
    ) -> None:
        self.sources: list[str] = sources
        self.final_dest: pathlib.Path = pathlib.Path(final_dest)
        self.is_tag: bool = is_tag
        self.limit: int | None = limit
        self.save_to_telegraph: bool | None = save_to_telegraph
        self.entity: str = self.get_entity()
        self.telegraph_client: Telegraph = Telegraph(access_token=TELEGRAPH_TOKEN)

    def get_entity(self) -> str:
        parsed_url = parse.urlparse(self.sources[0])
        return parsed_url.netloc

    def get_title(self, soup: BeautifulSoup) -> str:
        title_query = PAGE_TITLE_SPLIT_MAPPING[self.entity]
        title_tag = cast(Tag, soup.select_one("title"))
        title = title_tag.get_text(strip=True)
        cleaned_title = [title.split(t)[0] for t in title_query][0]

        return cleaned_title.rstrip().strip()

    def run(self) -> None:
        tqdm_sources_iterable = tqdm(
            enumerate(self.sources),
            total=len(self.sources),
            desc="Retrieving URLs...",
        )
        query, src_attr = QUERY_MAPPING[self.entity]
        headers = HEADERS_MAPPING.get(self.entity, None)

        if headers is None:
            headers = HEADERS_MAPPING.get("common")

        page_title = ""
        title_folder_mapping = {}
        posts_sent_counter = 0
        titles = IndexedSet()

        if self.final_dest:
            if not self.final_dest.exists():
                self.final_dest.mkdir(parents=True, exist_ok=True)

        for idx, source_url in tqdm_sources_iterable:
            folder_name = ""
            image_tags = IndexedSet()

            tags, soup = get_tags(
                source_url,
                headers=headers,
                query=query,
            )
            image_tags.update(*tags)

            page_title = self.get_title(soup)
            titles.add(page_title)

            unique_img_urls = IndexedSet()
            for idx, img_tag in enumerate(image_tags):
                image_name_prefix = f"{idx + 1}".zfill(3)
                img_src = img_tag.attrs[src_attr]
                img_src = img_src.strip().rstrip().replace("\r", "").replace("\n", "")
                img_name: str = img_src.split("/")[-1].split("?")[0]
                img_name = img_name.strip().rstrip().replace("\r", "").replace("\n", "")
                unique_img_urls.add((image_name_prefix, f"{image_name_prefix}-{img_name}", img_src))

            tqdm_sources_iterable.set_description(f"Finished retrieving images for {page_title}")
            ordered_unique_img_urls = IndexedSet(sorted(unique_img_urls, key=lambda x: x[0]))

            if self.final_dest:
                folder_name = f"{page_title}"
                title_dest = self.final_dest / folder_name
                if not title_dest.exists():
                    title_dest.mkdir(parents=True, exist_ok=True)
                title_folder_mapping[page_title] = (ordered_unique_img_urls, title_dest)

            if self.save_to_telegraph:
                if len(ordered_unique_img_urls) >= 90:
                    for chunk in split_every(50, ordered_unique_img_urls):
                        telegraph_uploader(
                            unique_img_urls=IndexedSet(chunk),
                            page_title=page_title,
                            posts_sent_counter=posts_sent_counter,
                            telegraph_client=self.telegraph_client,
                            tqdm_iterable=tqdm_sources_iterable,
                        )
                        posts_sent_counter += 1
                else:
                    telegraph_uploader(
                        unique_img_urls=IndexedSet(ordered_unique_img_urls),
                        page_title=page_title,
                        posts_sent_counter=posts_sent_counter,
                        telegraph_client=self.telegraph_client,
                        tqdm_iterable=tqdm_sources_iterable,
                    )
            page_title = ""

        if self.final_dest:
            downloader(
                titles=list(titles),
                title_folder_mapping=title_folder_mapping,
                headers=headers,
            )
