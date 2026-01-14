"""Tests for SEO pipeline normalization."""

import unittest

from scrapy.exceptions import DropItem

from core.pipelines import SeoItemPipeline


class TestSeoItemPipeline(unittest.TestCase):
    """Validate pipeline normalization and validation."""

    def test_pipeline_normalization(self) -> None:
        """Fill counts and lengths when missing."""
        pipeline = SeoItemPipeline(
            required_fields=["url", "status_code"],
            min_word_count=0,
            drop_noindex=False,
            drop_non_html=False,
            strip_fields=["title", "meta_description"],
        )
        item = {
            "url": "https://example.com/page",
            "status_code": 200,
            "title": " Example ",
            "meta_description": " Description ",
            "links": [
                {
                    "url": "https://example.com",
                    "is_internal": True,
                    "is_nofollow": False,
                },
                {
                    "url": "https://external.com",
                    "is_internal": False,
                    "is_nofollow": True,
                },
            ],
            "images": [
                {"src": "https://example.com/img.jpg", "alt": "Alt text"},
                {"src": "https://example.com/img2.jpg"},
            ],
            "canonical_link": "https://example.com/page",
            "url_without_query": "https://example.com/page",
            "robots_directives": ["index", "follow"],
        }

        processed = pipeline.process_item(item, spider=None)
        self.assertEqual(processed["title"], "Example")
        self.assertEqual(processed["meta_description"], "Description")
        self.assertEqual(processed["title_length"], len("Example"))
        self.assertEqual(processed["meta_description_length"], len("Description"))
        self.assertEqual(processed["link_count_total"], 2)
        self.assertEqual(processed["link_count_unique"], 2)
        self.assertEqual(processed["link_count_internal"], 1)
        self.assertEqual(processed["link_count_external"], 1)
        self.assertEqual(processed["link_count_nofollow"], 1)
        self.assertEqual(processed["image_count"], 2)
        self.assertEqual(processed["image_missing_alt_count"], 1)
        self.assertEqual(processed["image_alt_coverage"], 0.5)
        self.assertTrue(processed["canonical_is_self"])
        self.assertTrue(processed["is_indexable"])
        self.assertTrue(processed["is_follow"])

    def test_pipeline_required_fields(self) -> None:
        """Raise DropItem when required fields are missing."""
        pipeline = SeoItemPipeline(
            required_fields=["url", "status_code"],
            min_word_count=0,
            drop_noindex=False,
            drop_non_html=False,
            strip_fields=["title"],
        )
        with self.assertRaises(DropItem):
            pipeline.process_item({"status_code": 200}, spider=None)
