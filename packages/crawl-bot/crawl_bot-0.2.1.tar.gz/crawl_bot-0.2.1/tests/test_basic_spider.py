"""Tests for BasicSpider SEO extraction."""

import unittest

from scrapy.http import HtmlResponse, Request
from scrapy.item import Item

from core.spiders.basic_spider import BasicSpider


class TestBasicSpider(unittest.TestCase):
    """Validate SEO extraction for the basic spider."""

    def test_seo_extraction(self) -> None:
        """Extract key SEO fields from a sample HTML response."""
        html = """
        <html lang="en">
          <head>
            <title>Example Title</title>
            <meta name="description" content="Example description.">
            <meta name="robots" content="index,follow">
            <meta property="og:title" content="OG Title">
            <meta name="twitter:card" content="summary">
            <link rel="canonical" href="https://example.com/page">
            <link rel="alternate" hreflang="en" href="https://example.com/en">
            <script type="application/ld+json">
              {"@context":"https://schema.org","@type":"Article"}
            </script>
          </head>
          <body>
            <h1>Heading</h1>
            <p>Some text for word count.</p>
            <a href="/internal">Internal</a>
            <a href="https://external.com" rel="nofollow">External</a>
            <img src="/img.jpg" alt="Alt text">
            <img src="/img2.jpg">
          </body>
        </html>
        """
        spider = BasicSpider(start_urls="https://example.com")
        request = Request(url="https://example.com/page?ref=1")
        response = HtmlResponse(
            url=request.url,
            request=request,
            body=html,
            encoding="utf-8",
        )
        response.headers["Content-Type"] = "text/html; charset=utf-8"

        results = list(spider.parse(response))
        item = next(result for result in results if isinstance(result, Item))

        self.assertEqual(item["title"], "Example Title")
        self.assertEqual(item["meta_description_length"], len("Example description."))
        self.assertTrue(item["canonical_is_self"])
        self.assertIn("index", item["robots_directives"])
        self.assertIn("follow", item["robots_directives"])
        self.assertEqual(item["open_graph"]["title"], "OG Title")
        self.assertEqual(item["twitter"]["card"], "summary")
        self.assertIn("Article", item["structured_data_types"])
        self.assertEqual(item["link_count_internal"], 1)
        self.assertEqual(item["link_count_external"], 1)
        self.assertEqual(item["link_count_nofollow"], 1)
        self.assertEqual(item["image_missing_alt_count"], 1)
