"""
Item definitions for scraped pages.

See documentation in: https://docs.scrapy.org/en/latest/topics/items.html
"""

import scrapy


class PageItem(scrapy.Item):
    """Item describing a crawled page and SEO metadata."""

    url = scrapy.Field()
    url_without_query = scrapy.Field()
    url_path = scrapy.Field()
    url_params = scrapy.Field()
    url_query = scrapy.Field()
    url_fragment = scrapy.Field()
    status_code = scrapy.Field()
    response_time = scrapy.Field()
    content_type = scrapy.Field()
    content_length = scrapy.Field()
    response_size_bytes = scrapy.Field()
    title = scrapy.Field()
    title_length = scrapy.Field()
    meta_description = scrapy.Field()
    meta_description_length = scrapy.Field()
    meta_keywords = scrapy.Field()
    meta_charset = scrapy.Field()
    meta_viewport = scrapy.Field()
    meta_refresh = scrapy.Field()
    meta_refresh_url = scrapy.Field()
    canonical_link = scrapy.Field()
    canonical_is_self = scrapy.Field()
    amphtml_link = scrapy.Field()
    robots_meta = scrapy.Field()
    x_robots = scrapy.Field()
    robots_directives = scrapy.Field()
    is_indexable = scrapy.Field()
    is_follow = scrapy.Field()
    language = scrapy.Field()
    headings = scrapy.Field()
    heading_counts = scrapy.Field()
    word_count = scrapy.Field()
    text_length = scrapy.Field()
    links = scrapy.Field()
    link_count_total = scrapy.Field()
    link_count_unique = scrapy.Field()
    link_count_internal = scrapy.Field()
    link_count_external = scrapy.Field()
    link_count_nofollow = scrapy.Field()
    images = scrapy.Field()
    image_count = scrapy.Field()
    image_missing_alt_count = scrapy.Field()
    image_alt_coverage = scrapy.Field()
    open_graph = scrapy.Field()
    twitter = scrapy.Field()
    structured_data = scrapy.Field()
    structured_data_types = scrapy.Field()
    hreflang = scrapy.Field()
    depth = scrapy.Field()
    html = scrapy.Field()
