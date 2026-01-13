import asyncio
from typing import Any

import httpx
from bs4 import BeautifulSoup, Tag
from lxml import etree
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.service import Service
from tenacity import retry, wait_chain, wait_fixed
from webdriver_manager.chrome import ChromeDriverManager

from .pagination import query_pagination_mapping


async def get_webdriver() -> webdriver.Chrome:
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    options.add_argument("--headless")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    )
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    # executable_path = "/Users/mazulo/Dev/packages/chromedriver/chromedriver"
    # executable_path = "/home/mazulo/packages/chrome/chromedriver-linux64/chromedriver"
    executable_path = ChromeDriverManager().install()
    chrome_executable: Service = ChromeService(executable_path=executable_path)
    driver = webdriver.Chrome(options=options, service=chrome_executable)
    # driver = webdriver.Chrome(ChromeDriverManager().install())

    # stealth(
    #     driver,
    #     languages=["en-US", "en"],
    #     vendor="Google Inc.",
    #     platform="Win32",
    #     webgl_vendor="Intel Inc.",
    #     renderer="Intel Iris OpenGL Engine",
    #     fix_hairline=True,
    # )

    return driver


@retry(
    wait=wait_chain(
        *[wait_fixed(3) for _ in range(5)]
        + [wait_fixed(7) for _ in range(4)]
        + [wait_fixed(9) for _ in range(3)]
        + [wait_fixed(15)],
    ),
    reraise=True,
)
async def get_tags(
    url: str,
    query: str,
    headers: dict[str, Any] | None = None,
    uses_js: bool | None = False,
    should_retry: bool | None = True,
    bypass_cloudflare: bool | None = False,
) -> tuple[list[Tag], BeautifulSoup]:
    """Wait 3s for 5 attempts
    7s for the next 4 attempts
    9s for the next 3 attempts
    then 15 for all attempts thereafter
    """
    if uses_js or bypass_cloudflare:
        driver = await get_webdriver()
        driver.get(url)
        await asyncio.sleep(5)
        soup = BeautifulSoup(driver.page_source, features="lxml")
        tags = soup.select(query)
        if not tags and should_retry:
            driver.refresh()
            await asyncio.sleep(5)
            soup = BeautifulSoup(driver.page_source, features="lxml")
            tags = soup.select(query)
            if not tags:
                print("Page not rendered properly. Retrying one more time...")
                return await get_tags(
                    url=url,
                    query=query,
                    headers=headers,
                    uses_js=uses_js,
                    should_retry=False,
                )
    else:
        soup = await get_soup(target_url=url, headers=headers)
        tags = soup.select(query)

    return tags, soup


async def get_soup(
    target_url: str,
    headers: dict[str, str] | None = None,
    use_web_driver: bool | None = False,
) -> BeautifulSoup:
    if use_web_driver:
        driver = await get_webdriver()
        driver.get(target_url)
        page_source = driver.page_source
    else:
        response = httpx.get(target_url, headers=headers, verify=False)
        page_source = response.content

    return BeautifulSoup(page_source, features="lxml")


async def get_pages_from_pagination(
    url: str,
    target: str,
    headers: dict[str, str] | None = None,
) -> list[str]:
    pagination_params = query_pagination_mapping[target]
    source_urls = set()
    soup = await get_soup(url, headers=headers)
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
    else:
        first = pagination.get_text(strip=True)
        last_page = pagination_set[-1]
        last = last_page.get_text(strip=True)

    first_page, last_page = int(first), int(last)

    first_link_pagination = soup.select(pagination_params.pagination_base_url_query)[0]
    href = first_link_pagination.attrs["href"]
    base_pagination_url = href.rsplit("/", 2)[0]

    for a_tag in dom.xpath(pagination_params.posts_query_xpath):
        source_urls.add(a_tag.attrib["href"])

    for index in range(first_page, last_page + 1):
        if index == 1:
            continue

        target_url = f"{base_pagination_url}/{index}/"

        soup = await get_soup(target_url)
        dom = etree.HTML(str(soup))
        source_urls.update([a_tag.attrib["href"] for a_tag in dom.xpath(pagination_params.posts_query_xpath)])

    return list(source_urls)
