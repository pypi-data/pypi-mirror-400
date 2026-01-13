import pathlib
from collections.abc import AsyncGenerator, Iterable
from itertools import islice
from typing import Any
from urllib import parse


async def split_every(chunk_size: int, iterable: Iterable[Any]) -> AsyncGenerator[list[Any], None]:
    """
    Iterate in chunks.
    It's better when you have a big one that can
    overload the db/API/CPU.
    """
    i = iter(iterable)
    piece = list(islice(i, chunk_size))

    while piece:
        yield piece
        piece = list(islice(i, chunk_size))


async def get_entity(sources: list[str]) -> str:
    parsed_url = parse.urlparse(sources[0])
    return parsed_url.netloc


async def print_albums_message(albums_links: list[str]) -> None:
    albums_message = ""

    for album in albums_links:
        albums_message += f"\t- {album}\n"

    message = "All albums have been downloaded and saved to the specified folder.\n"
    message += "Albums saved are the following:\n"
    message += f"{albums_message}"
    print(message)


def sort_file(file: pathlib.Path) -> str:
    filename = file.name.split(".")[0]
    filename = filename.zfill(2)
    return filename
