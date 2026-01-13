from dataclasses import dataclass


@dataclass(kw_only=True)
class PaginationXPath:
    pagination_query: str
    pages_count_query: str
    pagination_base_url_query: str
    posts_query_xpath: str

    def __post_init__(self) -> None:
        self.pages_count_query = f"{self.pagination_query} {self.pages_count_query}"


query_pagination_mapping = {
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
