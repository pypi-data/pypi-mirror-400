from bs4 import BeautifulSoup
from lxml import etree
from selenium import webdriver

from grabber.core.utils import (
    query_pagination_mapping,
)


async def get_pages_from_pagination(
    url: str,
    target: str,
    headers: dict[str, str] | None = None,
) -> list[str]:
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    driver.get(url)

    pagination_params = query_pagination_mapping[target]
    source_urls = set()
    soup = BeautifulSoup(driver.page_source)
    dom = etree.HTML(str(soup))
    pagination_set = soup.select(pagination_params.pages_count_query)

    if not pagination_set:
        for a_tag in dom.xpath(pagination_params.posts_query_xpath):
            if a_tag is not None and a_tag.attrib["href"] not in source_urls:
                source_urls.add(a_tag.attrib["href"])
        return list(source_urls)

    pagination = pagination_set[0]
    pagination_text = pagination.text
    if "Page" in pagination_text:
        first, last = pagination_text.split("Page")[-1].strip().split("of")
        first_page, last_page = int(first), int(last)
    else:
        first = pagination_set[0]
        first_page = int(first.get_text(strip=True))
        last_page = 0
        for pagination in pagination_set:
            page_text = pagination.get_text(strip=True)

            if page_text.isdigit():
                page_counter = int(page_text)
                if page_counter > last_page:
                    last_page = page_counter

    first_link_pagination = soup.select(pagination_params.pagination_base_url_query)[0]
    href = first_link_pagination.attrs["href"]
    base_pagination_url = url.rsplit("/", 2)[0]

    for a_tag in dom.xpath(pagination_params.posts_query_xpath):
        source_urls.add(a_tag.attrib["data-src"])

    for index in range(first_page, last_page + 1):
        if index == 1:
            continue

        target_url = f"{base_pagination_url}{href}&page={index}"

        driver.get(target_url)
        soup = BeautifulSoup(driver.page_source)
        dom = etree.HTML(str(soup))
        breakpoint()
        source_urls.update([a_tag.attrib["href"] for a_tag in dom.xpath(pagination_params.posts_query_xpath)])

    return list(source_urls)
