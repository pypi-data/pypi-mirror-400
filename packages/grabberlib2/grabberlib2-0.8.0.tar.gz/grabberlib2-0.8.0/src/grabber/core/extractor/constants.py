import multiprocessing
from dataclasses import dataclass

DEFAULT_THREADS_NUMBER = multiprocessing.cpu_count()
PAGINATION_QUERY = "div.jeg_navigation.jeg_pagination"
PAGINATION_PAGES_COUNT_QUERY = f"{PAGINATION_QUERY} span.page_info"
PAGINATION_BASE_URL_QUERY = "div.jeg_navigation.jeg_pagination a.page_number"
POSTS_QUERY_XPATH = (
    "/html/body/div[2]/div[5]/div/div[1]/div/div/div[2]/div/div/div[2]/div/div[1]/div/div/div/article/div/div/a"
)


QUERY_MAPPING = {
    "xiuren.biz": ("div.content-inner img", "src"),
    "nudebird.biz": ("div.thecontent a", "href"),
    "hotgirl.biz": ("div.thecontent a", "href"),
    "nudecosplay.biz": ("div.content-inner a img", "src"),
    "www.v2ph.com": (
        "div.photos-list.text-center img",
        "src",
    ),  # Needs to handle pagination
    "cgcosplay.org": ("div.gallery-icon.portrait img", "src"),
    "mitaku.net": ("img.msacwl-img", "data-lazy"),
    "www.xasiat.com": ("div.images a", "href"),
    "telegra.ph": ("img", "src"),
    "www.4khd.com": (
        "div.is-layout-constrained.entry-content.wp-block-post-content img",
        "src",
    ),
    "yellow": (
        "div.elementor-widget-container a[href^='https://terabox.com']",
        "href",
    ),
    "everia.club": ("div.divone div.mainleft img", "data-original"),
    "bestgirlsexy.com": ("div.elementor-widget-container p img", "src"),
    "asigirl.com": ("a.asigirl-item", "href"),
    "cosplaytele.com": ("img.attachment-full.size-full", "src"),
    "hotgirl.asia": ("div.galeria_img img", "src"),
    "4kup.net": ("div#gallery div.caption a.cp", "href"),
    "buondua.com": ("div.article-fulltext p img", "src"),
    "www.erome.com": (
        "div.col-sm-12.page-content div div.media-group div.img div.img-blur img",
        "data-src",
    ),
    "erome.com": (
        "div.col-sm-12.page-content div div.media-group div.img div.img-blur img",
        "data-src",
    ),
    "notion": (
        "div.notion-page-content > div > div > div > div > div > div.notion-cursor-default > div > div > div > img",
        "src",
    ),
    "new.pixibb.com": (
        "div.blog-post-wrap > article.post-details > div.entry-content img",
        "src",
    ),
    "spacemiss.com": ("div.tdb-block-inner.td-fix-index > img", "src"),
    "www.hentaiclub.net": (
        "div.content div.post.row img.post-item-img.lazy",
        "data-original",
    ),
    "ugirls.pics": ("div#main div.my-2 img", "src"),
    "xlust.org": (
        "div.entry-wrapper div.entry-content.u-clearfix div.rl-gallery-container a",
        "href",
    ),
}


@dataclass(kw_only=True)
class PaginationXPath:
    pagination_query: str
    pages_count_query: str
    pagination_base_url_query: str
    posts_query_xpath: str

    def __post_init__(self) -> None:
        self.pages_count_query = f"{self.pagination_query} {self.pages_count_query}"


QUERY_PAGINATION_MAPPING = {
    "xiuren.biz": PaginationXPath(
        pagination_query="div.jeg_navigation.jeg_pagination",
        pages_count_query="span.page_info",
        pagination_base_url_query="div.jeg_navigation.jeg_pagination a.page_number",
        posts_query_xpath=(
            "/html/body/div[2]/div[5]/div/div[1]/div/div/div[2]/div/div/div[2]/div/div[1]/div/div/div/article/div/div/a"
        ),
    ),
    "yellow": PaginationXPath(
        pagination_query="div.jeg_navigation.jeg_pagination",
        pages_count_query="span.page_info",
        pagination_base_url_query="div.jeg_navigation.jeg_pagination a.page_number",
        posts_query_xpath=(
            "/html/body/div[3]/div[4]/div/div[1]/div/div/div[2]/div/div/div[2]/div/div[1]/div/div/div/article/div/div/a"
        ),
    ),
    "nudecosplay.biz": PaginationXPath(
        pagination_query="div.jeg_navigation.jeg_pagination",
        pages_count_query="span.page_info",
        pagination_base_url_query="div.jeg_navigation.jeg_pagination a.page_number",
        posts_query_xpath="/html/body/div[2]/div[5]/div/div[1]/div/div/div[2]/div/div/div[2]/div/div/div/div/div/article/div/a",
    ),
    "buondua.com": PaginationXPath(
        pagination_query="div.pagination-list",
        pages_count_query="span a.pagination-link",
        pagination_base_url_query="div.pagination-list span a.pagination-link.is-current",
        posts_query_xpath="/html/body/div[2]/div/div[2]/nav[1]/div/span/a",
    ),
    "www.v2ph.com": PaginationXPath(
        pagination_query="div.py-2",
        pages_count_query="a.page-link",
        pagination_base_url_query="div.py-2 ul li.active a",
        posts_query_xpath="/html/body/div/div[2]/div/img",
    ),
}

HEADERS_MAPPING = {
    "nudebird.biz": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    },
    "nudecosplay.biz": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    },
    "www.v2ph.com": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    },
    "cgcosplay.org": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    },
    "mitaku.net": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    },
    "www.xasiat.com": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    },
    "www.4khd.com": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    },
    "buondua.com": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    },
    "bunkr": {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    },
    "bestgirlsexy.com": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    },
    "new.pixibb.com": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    },
    "spacemiss.com": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    },
    "www.hentaiclub.net": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    },
    "ugirls.pics": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    },
    "xlust.org": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    },
    "common": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    },
}

PAGE_TITLE_SPLIT_MAPPING = {
    "xlust.org": ["- XLUST.ORG"],
    "xiuren.biz": ["- Xiuren.biz"],
    "ugirls.pics": ["|", "Page"],
    "spacemiss.com": ["-"],
    "new.pixibb.com": ["-"],
    "nudebird.biz": ["- Nude Bird"],
    "nudecosplay.biz": ["/nudecosplay.biz/"],
    "hotgirl.biz": ["- Hotgirl.biz"],
    "mitaku.net": ["- Beautiful", "- Mitaku.net"],
    "hotgirl.asia": ["- Hotgirl.asia", "- Share"],
    "hentaiclub.net": ["-"],
    "everia.club": ["Everia.club", "-"],
    "common": ["-"],
}
