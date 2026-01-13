from typing import cast

from boltons.setutils import IndexedSet
from bs4 import Tag


async def build_unique_img_urls(
    image_tags: list[Tag],
    src_attr: str,
    secondary_src_attr: str = "",
    entity: str | None = "",
) -> IndexedSet:
    unique_img_urls = IndexedSet()
    for idx, img_tag in enumerate(image_tags):
        img_src = (
            img_tag.attrs.get(src_attr, "")
            .strip()
            .rstrip()
            .replace("\r", "")
            .replace("\n", "")
            .replace("_300px", "")
            .replace("_320px", "")
            .replace("/300px/", "/full/")
            .replace("_400px", "")
            .replace("_280.jpg", ".jpg")
            .replace("_s.jpg", ".jpg")
            .replace("-thumbnail", "")
        )

        if not img_src or "gif" in img_src:
            img_src = img_tag.attrs.get(secondary_src_attr, "").strip().rstrip().replace("\r", "").replace("\n", "")
        if "https:" not in img_src:
            img_src = f"https://fapachi.com{img_src}" if entity and entity == "fapachi.com" else f"https:{img_src}"

        if entity == "avjb.com":
            img_src = img_src.replace("main/200x150", "sources")

        image_alt = img_tag.attrs.get("alt", "")
        image_name_prefix = f"{idx + 1}".zfill(3)

        if image_alt:
            img_name = image_alt.strip().rstrip().replace("\r", "").replace("\n", "")
        else:
            img_name: str = img_src.split("/")[-1].split("?")[0]
            img_name = img_name.strip().rstrip().replace("\r", "").replace("\n", "")

        if "html" in img_src:
            continue

        img_filename = img_src.split("/")[-1]
        unique_img_urls.add((image_name_prefix, f"{image_name_prefix}-{img_name}", f"{img_filename}", img_src))

    ordered_unique_img_urls = IndexedSet([a[1:] for a in unique_img_urls])

    return ordered_unique_img_urls


async def build_unique_video_urls(
    video_tags: list[Tag],
    src_attr: str,
    secondary_src_attr: str = "",
    entity: str | None = "",
) -> IndexedSet:
    unique_video_urls = IndexedSet()
    for idx, video_tag in enumerate(video_tags):
        try:
            if entity == "kemono.cr":
                video_src = video_tag.attrs.get(src_attr, "").strip().rstrip().replace("\r", "").replace("\n", "")
            elif (entity and entity != "kemono.cr") and (
                ".mp4" not in video_tag.attrs.get(src_attr, "") or ".mov" not in video_tag.attrs.get(src_attr, "")
            ):
                source_tag = cast(Tag, video_tag.find("source"))
                video_src = source_tag.attrs.get(src_attr, "").strip().rstrip().replace("\r", "").replace("\n", "")
            else:
                video_src = video_tag.attrs.get(src_attr, "").strip().rstrip().replace("\r", "").replace("\n", "")
        except Exception as exc:
            print(f"Error happened when building video URL for {video_tag} - {source_tag}: {exc}")
            continue

        video_poster = video_tag.attrs.get("poster", "")
        video_name_prefix = f"{idx + 1}".zfill(3)
        video_name: str = video_src.split("/")[-1].split("?")[0]
        video_name = video_name.strip().rstrip().replace("\r", "").replace("\n", "")

        unique_video_urls.add((video_name_prefix, f"{video_name_prefix}-{video_name}", video_poster, video_src))

    ordered_unique_video_urls = IndexedSet(sorted(unique_video_urls, key=lambda x: list(x).pop(0)))
    ordered_unique_video_urls = IndexedSet([a[1:] for a in ordered_unique_video_urls])

    return ordered_unique_video_urls
