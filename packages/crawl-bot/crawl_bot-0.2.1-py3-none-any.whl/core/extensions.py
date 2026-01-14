"""Project extensions for crawl reporting."""

from typing import Any, Dict

from scrapy import signals
from scrapy.crawler import Crawler
from scrapy.spiders import Spider
from scrapy.statscollectors import StatsCollector


def _extract_status_counts(stats: Dict[str, Any]) -> Dict[str, int]:
    """Extract HTTP status counts from Scrapy stats."""
    prefix = "downloader/response_status_count/"
    counts: Dict[str, int] = {}
    for key, value in stats.items():
        if not key.startswith(prefix):
            continue
        status = key[len(prefix):]
        if isinstance(value, int):
            counts[status] = value
    return counts


class CrawlStatsExtension:
    """Log crawl summary stats when a spider closes."""

    def __init__(self, stats: StatsCollector) -> None:
        """
        Store the stats collector for later reporting.

        Returns:
            None
        """
        self.stats = stats

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> "CrawlStatsExtension":
        """
        Create the extension and connect signals.

        Returns:
            Configured extension instance.
        """
        extension = cls(crawler.stats)
        crawler.signals.connect(
            extension.spider_closed,
            signal=signals.spider_closed,
        )
        return extension

    def spider_closed(self, spider: Spider, reason: str) -> None:
        """
        Log crawl summary metrics on spider shutdown.

        Returns:
            None
        """
        stats = dict(self.stats.get_stats() or {})
        items = stats.get("item_scraped_count", 0)
        responses = stats.get("response_received_count", 0)
        filtered = stats.get("dupefilter/filtered", 0)
        elapsed = stats.get("elapsed_time_seconds", 0.0)
        spider.logger.info(
            "Crawl summary: items=%s responses=%s filtered=%s elapsed=%.1fs reason=%s",
            items,
            responses,
            filtered,
            elapsed,
            reason,
        )

        status_counts = _extract_status_counts(stats)
        if status_counts:
            spider.logger.info("HTTP status counts: %s", status_counts)
