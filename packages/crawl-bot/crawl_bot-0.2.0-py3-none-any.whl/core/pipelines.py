"""
Define item pipelines for normalization and validation.

See documentation in: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
"""

from typing import Any, Optional, Sequence
from urllib.parse import urlparse

from itemadapter import ItemAdapter
from scrapy import Spider
from scrapy.crawler import Crawler
from scrapy.exceptions import DropItem


def _strip_or_none(value: Optional[str]) -> Optional[str]:
    """Strip a string, returning None when empty."""
    if value is None:
        return None
    value = str(value).strip()
    return value if value else None


def _normalize_url_for_compare(url: Optional[str]) -> Optional[str]:
    """Normalize a URL for canonical comparisons."""
    if not url:
        return None
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        return None
    path = parsed.path or "/"
    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")
    return f"{parsed.scheme.lower()}://{parsed.netloc.lower()}{path}"


def _derive_indexable(directives: Sequence[str]) -> Optional[bool]:
    """Derive indexable state from robots directives."""
    if "noindex" in directives:
        return False
    if "index" in directives:
        return True
    return None


def _derive_follow(directives: Sequence[str]) -> Optional[bool]:
    """Derive follow state from robots directives."""
    if "nofollow" in directives:
        return False
    if "follow" in directives:
        return True
    return None


class SeoItemPipeline:
    """Normalize and validate SEO crawl items."""

    def __init__(
        self,
        required_fields: Sequence[str],
        min_word_count: int,
        drop_noindex: bool,
        drop_non_html: bool,
        strip_fields: Sequence[str],
    ) -> None:
        """
        Configure validation and normalization behavior.

        Returns:
            None
        """
        self.required_fields = list(required_fields)
        self.min_word_count = min_word_count
        self.drop_noindex = drop_noindex
        self.drop_non_html = drop_non_html
        self.strip_fields = list(strip_fields)

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> "SeoItemPipeline":
        """
        Create the pipeline using crawler settings.

        Returns:
            Configured pipeline instance.
        """
        settings = crawler.settings
        return cls(
            required_fields=settings.getlist(
                "SEO_REQUIRED_FIELDS",
                ["url", "status_code"],
            ),
            min_word_count=settings.getint("SEO_MIN_WORD_COUNT", 0),
            drop_noindex=settings.getbool("SEO_DROP_NOINDEX", False),
            drop_non_html=settings.getbool("SEO_DROP_NON_HTML", False),
            strip_fields=settings.getlist(
                "SEO_STRIP_FIELDS",
                ["title", "meta_description"],
            ),
        )

    def process_item(self, item: Any, spider: Spider) -> Any:
        """
        Validate and normalize a scraped item.

        Returns:
            The normalized item, or raises DropItem.
        """
        adapter = ItemAdapter(item)
        self._validate_required_fields(adapter)
        self._normalize_strings(adapter)
        self._normalize_lengths(adapter)
        self._normalize_links(adapter)
        self._normalize_images(adapter)
        self._normalize_canonical(adapter)
        self._normalize_robots(adapter)
        self._normalize_url_fields(adapter)
        return item

    def _validate_required_fields(self, adapter: ItemAdapter) -> None:
        """Ensure required fields are present and non-empty."""
        for field in self.required_fields:
            value = adapter.get(field)
            if value in (None, "", [], {}):
                raise DropItem(f"Missing required field: {field}")

        word_count = adapter.get("word_count")
        if self.min_word_count and isinstance(word_count, int):
            if word_count < self.min_word_count:
                raise DropItem("Word count below minimum threshold")

        if self.drop_noindex and adapter.get("is_indexable") is False:
            raise DropItem("Item marked as noindex")

        if self.drop_non_html:
            content_type = adapter.get("content_type") or ""
            if isinstance(content_type, str) and "html" not in content_type.lower():
                raise DropItem("Non-HTML content")

    def _normalize_strings(self, adapter: ItemAdapter) -> None:
        """Strip selected string fields."""
        for field in self.strip_fields:
            value = adapter.get(field)
            if isinstance(value, str):
                adapter[field] = _strip_or_none(value)

    def _normalize_lengths(self, adapter: ItemAdapter) -> None:
        """Populate missing length metrics for text fields."""
        title = adapter.get("title")
        if title and adapter.get("title_length") is None:
            adapter["title_length"] = len(title)

        description = adapter.get("meta_description")
        if description and adapter.get("meta_description_length") is None:
            adapter["meta_description_length"] = len(description)

    def _normalize_links(self, adapter: ItemAdapter) -> None:
        """Populate link count fields when missing."""
        links = adapter.get("links")
        if not isinstance(links, list):
            return

        if adapter.get("link_count_total") is None:
            adapter["link_count_total"] = len(links)

        if adapter.get("link_count_unique") is None:
            unique_urls = {
                link.get("url")
                for link in links
                if isinstance(link, dict) and link.get("url")
            }
            adapter["link_count_unique"] = len(unique_urls)

        if adapter.get("link_count_internal") is None:
            adapter["link_count_internal"] = sum(
                1
                for link in links
                if isinstance(link, dict) and link.get("is_internal") is True
            )

        if adapter.get("link_count_external") is None:
            adapter["link_count_external"] = sum(
                1
                for link in links
                if isinstance(link, dict) and link.get("is_internal") is False
            )

        if adapter.get("link_count_nofollow") is None:
            adapter["link_count_nofollow"] = sum(
                1
                for link in links
                if isinstance(link, dict) and link.get("is_nofollow") is True
            )

    def _normalize_images(self, adapter: ItemAdapter) -> None:
        """Populate image count fields when missing."""
        images = adapter.get("images")
        if not isinstance(images, list):
            return

        if adapter.get("image_count") is None:
            adapter["image_count"] = len(images)

        if adapter.get("image_missing_alt_count") is None:
            adapter["image_missing_alt_count"] = sum(
                1
                for image in images
                if isinstance(image, dict) and not image.get("alt")
            )

        if adapter.get("image_alt_coverage") is None:
            image_count = adapter.get("image_count")
            missing_count = adapter.get("image_missing_alt_count")
            if isinstance(image_count, int) and image_count > 0:
                if isinstance(missing_count, int):
                    adapter["image_alt_coverage"] = (
                        image_count - missing_count
                    ) / image_count

    def _normalize_canonical(self, adapter: ItemAdapter) -> None:
        """Populate canonical comparison flags when missing."""
        canonical_link = adapter.get("canonical_link")
        url_without_query = adapter.get("url_without_query")
        if canonical_link and adapter.get("canonical_is_self") is None:
            canonical_normalized = _normalize_url_for_compare(canonical_link)
            url_normalized = _normalize_url_for_compare(url_without_query)
            if canonical_normalized and url_normalized:
                adapter["canonical_is_self"] = canonical_normalized == url_normalized

    def _normalize_robots(self, adapter: ItemAdapter) -> None:
        """Populate index/follow flags when directives are present."""
        directives = adapter.get("robots_directives")
        if not isinstance(directives, list):
            return

        if adapter.get("is_indexable") is None:
            adapter["is_indexable"] = _derive_indexable(directives)

        if adapter.get("is_follow") is None:
            adapter["is_follow"] = _derive_follow(directives)

    def _normalize_url_fields(self, adapter: ItemAdapter) -> None:
        """Ensure url_without_query exists if url is present."""
        if adapter.get("url_without_query") is None and adapter.get("url"):
            parsed = urlparse(adapter.get("url"))
            adapter["url_without_query"] = parsed._replace(
                query="",
                fragment="",
            ).geturl()


class CrawlBotPipeline(SeoItemPipeline):
    """Backward compatible alias for SeoItemPipeline."""
