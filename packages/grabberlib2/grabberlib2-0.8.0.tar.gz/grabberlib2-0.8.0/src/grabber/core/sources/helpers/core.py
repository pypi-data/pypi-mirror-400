import pathlib
from pathlib import Path
from typing import Any, cast

import unidecode
from boltons.setutils import IndexedSet
from bs4 import Tag


def get_page_title(soup: Tag, strings_to_remove: list[str]) -> str:
    page_title = cast(Tag, soup.find("title")).get_text(strip=True).strip().rstrip()

    for string_to_remove in strings_to_remove:
        page_title = page_title.split(string_to_remove)[0]

    page_title = page_title.replace("https:", "")
    page_title = unidecode.unidecode(
        " ".join(
            f"#{part.strip().replace(' ', '').replace('.', '_').replace('-', '_')}" for part in page_title.split("/")
        )
    )
    return unidecode.unidecode(page_title)


def handle_final_destination(
    page_title: str,
    entity: str,
    ordered_unique_img_urls: IndexedSet,
    title_folder_mapping: dict[str, tuple[IndexedSet, Any]],
    final_dest: str | Path | None = None,
) -> tuple[str | Path | None, dict[str, tuple[IndexedSet, Any]]]:
    if final_dest:
        final_dest = pathlib.Path(final_dest) / unidecode(f"{page_title} - {entity}")
        if not final_dest.exists():
            final_dest.mkdir(parents=True, exist_ok=True)

        title_folder_mapping[page_title] = (ordered_unique_img_urls, final_dest)
    return final_dest, title_folder_mapping
