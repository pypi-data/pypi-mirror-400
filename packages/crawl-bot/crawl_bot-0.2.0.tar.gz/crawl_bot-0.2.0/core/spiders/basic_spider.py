"""Basic spider module with SEO-focused extraction."""

import json
import re
from typing import (
    Any,
    Dict,
    Iterator,
    List,
    Optional,
    Sequence,
    Tuple,
    TypedDict,
    Union,
)
from urllib.parse import urlparse

import scrapy
from scrapy.crawler import Crawler
from scrapy.http import Response
from scrapy.linkextractors import LinkExtractor

from core.items import PageItem

TRUTHY_VALUES = {"1", "true", "yes", "y", "on"}
WORD_RE = re.compile(r"[A-Za-z0-9]+")
WHITESPACE_RE = re.compile(r"\s+")


class LinkItem(TypedDict):
    """Typed structure for link metadata."""

    url: str
    text: Optional[str]
    rel: Optional[str]
    is_internal: bool
    is_nofollow: bool


class ImageItem(TypedDict):
    """Typed structure for image metadata."""

    src: Optional[str]
    alt: Optional[str]
    title: Optional[str]
    srcset: Optional[str]
    data_src: Optional[str]
    loading: Optional[str]
    width: Optional[str]
    height: Optional[str]


class HreflangItem(TypedDict):
    """Typed structure for hreflang metadata."""

    href: str
    hreflang: Optional[str]


MetaMap = Dict[str, Union[str, List[str]]]


def _parse_list(value: Any) -> List[str]:
    """Return a list of cleaned string values from CLI input."""
    if value is None:
        return []

    if isinstance(value, (list, tuple, set)):
        raw_values = list(value)
    else:
        raw_values = [value]

    results: List[str] = []
    for raw in raw_values:
        if raw is None:
            continue
        if isinstance(raw, str):
            raw = raw.strip()
            if not raw:
                continue
            if raw.startswith("["):
                try:
                    parsed = json.loads(raw)
                except json.JSONDecodeError:
                    parsed = None
                if isinstance(parsed, list):
                    results.extend(
                        [str(entry) for entry in parsed if entry is not None]
                    )
                    continue
            if "," in raw:
                results.extend(
                    [part.strip() for part in raw.split(",") if part.strip()]
                )
                continue
            results.append(raw)
        else:
            results.append(str(raw))

    cleaned = []
    for entry in results:
        entry = str(entry).strip()
        if entry:
            cleaned.append(entry)
    return cleaned


def _unique_in_order(values: Sequence[str]) -> List[str]:
    """Return unique values in their first-seen order."""
    seen = set()
    unique = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        unique.append(value)
    return unique


def _normalize_start_urls(value: Any) -> List[str]:
    """Normalize start URLs by ensuring scheme and deduping."""
    urls = _parse_list(value)
    normalized = []
    for url in urls:
        if "://" not in url:
            url = f"https://{url}"
        normalized.append(url)
    return _unique_in_order(normalized)


def _normalize_allowed_domains(value: Any) -> List[str]:
    """Normalize allowed domains to hostnames only."""
    domains = _parse_list(value)
    normalized = []
    for domain in domains:
        if "://" in domain:
            parsed = urlparse(domain)
            domain = parsed.netloc or parsed.path
        normalized.append(domain)
    return _unique_in_order([domain for domain in normalized if domain])


def _is_truthy(value: Any) -> bool:
    """Return True for common truthy strings and booleans."""
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in TRUTHY_VALUES


def _parse_int(value: Any) -> Optional[int]:
    """Parse an integer value from a string or number."""
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _parse_float(value: Any) -> Optional[float]:
    """Parse a float value from a string or number."""
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _decode_header(value: Any) -> Optional[str]:
    """Decode a response header value to a string."""
    if not value:
        return None
    if isinstance(value, bytes):
        return value.decode("latin-1").strip()
    return str(value).strip()


def _strip_or_none(value: Optional[str]) -> Optional[str]:
    """Strip a string, returning None when empty."""
    if value is None:
        return None
    value = str(value).strip()
    return value if value else None


def _is_html_response(response: Response) -> bool:
    """Return True when the response is HTML or XHTML."""
    content_type = _decode_header(response.headers.get("Content-Type"))
    if not content_type:
        return True
    content_type = content_type.lower()
    return "text/html" in content_type or "application/xhtml+xml" in content_type


def _collapse_whitespace(text: str) -> str:
    """Collapse repeated whitespace into single spaces."""
    return WHITESPACE_RE.sub(" ", text).strip()


def _extract_visible_text(response: Response) -> str:
    """Extract visible text content from the response body."""
    texts = response.xpath(
        "//body//text()[normalize-space() and not(ancestor::script or ancestor::style "
        "or ancestor::noscript)]"
    ).getall()
    return _collapse_whitespace(" ".join(texts))


def _word_count(text: str) -> int:
    """Return a basic word count for the given text."""
    if not text:
        return 0
    return len(WORD_RE.findall(text))


def _split_meta_keywords(value: Optional[str]) -> Optional[List[str]]:
    """Split meta keywords into a list."""
    if not value:
        return None
    keywords = [token.strip() for token in value.split(",") if token.strip()]
    return _unique_in_order(keywords) if keywords else None


def _extract_charset(response: Response) -> Optional[str]:
    """Extract a charset declaration from meta tags."""
    charset = _strip_or_none(response.css("meta[charset]::attr(charset)").get())
    if charset:
        return charset
    content = _strip_or_none(
        response.css('meta[http-equiv="Content-Type"]::attr(content)').get()
    )
    if not content:
        return None
    match = re.search(r"charset=([\w-]+)", content, flags=re.IGNORECASE)
    return match.group(1) if match else None


def _parse_directives(*values: Optional[str]) -> List[str]:
    """Parse robots directives from meta and header values."""
    directives: List[str] = []
    for value in values:
        if not value:
            continue
        for token in re.split(r"[,\s]+", value.lower()):
            token = token.strip()
            if token:
                directives.append(token)
    return _unique_in_order(directives)


def _derive_indexable(directives: Sequence[str]) -> Optional[bool]:
    """Return indexable state derived from robots directives."""
    if "noindex" in directives:
        return False
    if "index" in directives:
        return True
    return None


def _derive_follow(directives: Sequence[str]) -> Optional[bool]:
    """Return follow state derived from robots directives."""
    if "nofollow" in directives:
        return False
    if "follow" in directives:
        return True
    return None


def _normalize_url_for_compare(url: Optional[str]) -> Optional[str]:
    """Normalize URL for canonical comparisons."""
    if not url:
        return None
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        return None
    path = parsed.path or "/"
    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")
    return f"{parsed.scheme.lower()}://{parsed.netloc.lower()}{path}"


def _extract_prefixed_meta(response: Response, prefix: str) -> Dict[str, List[str]]:
    """Collect prefixed meta tag content values."""
    results: Dict[str, List[str]] = {}
    selectors = [
        f'meta[property^="{prefix}"]',
        f'meta[name^="{prefix}"]',
    ]
    for selector in selectors:
        for meta in response.css(selector):
            key = meta.attrib.get("property") or meta.attrib.get("name")
            if not key or not key.startswith(prefix):
                continue
            content = _strip_or_none(meta.attrib.get("content"))
            if content is None:
                continue
            clean_key = key[len(prefix):]
            results.setdefault(clean_key, []).append(content)
    return results


def _flatten_meta_values(values: Dict[str, List[str]]) -> MetaMap:
    """Flatten single-item lists to strings for meta values."""
    flattened: MetaMap = {}
    for key, items in values.items():
        flattened[key] = items[0] if len(items) == 1 else items
    return flattened


def _extract_schema_types(data: Any) -> List[str]:
    """Recursively extract schema types from JSON-LD data."""
    types: List[str] = []
    if isinstance(data, dict):
        type_value = data.get("@type") or data.get("type")
        if isinstance(type_value, list):
            types.extend([str(value) for value in type_value if value])
        elif type_value:
            types.append(str(type_value))
        for value in data.values():
            types.extend(_extract_schema_types(value))
    elif isinstance(data, list):
        for item in data:
            types.extend(_extract_schema_types(item))
    return types


def _extract_structured_data(response: Response) -> Tuple[List[Any], List[str]]:
    """Extract JSON-LD structured data and derived schema types."""
    structured_items: List[Any] = []
    schema_types: List[str] = []
    for raw in response.css('script[type="application/ld+json"]::text').getall():
        raw = raw.strip()
        if not raw:
            continue
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            structured_items.append(raw)
            continue
        structured_items.append(parsed)
        schema_types.extend(_extract_schema_types(parsed))
    schema_types = _unique_in_order([value for value in schema_types if value])
    return structured_items, schema_types


def _extract_hreflang(response: Response) -> List[HreflangItem]:
    """Extract hreflang link tags."""
    hreflang_items: List[HreflangItem] = []
    for tag in response.css('link[rel~="alternate"][hreflang]'):
        href = _strip_or_none(tag.attrib.get("href"))
        if not href:
            continue
        hreflang_items.append(
            {
                "href": response.urljoin(href),
                "hreflang": _strip_or_none(tag.attrib.get("hreflang")),
            }
        )
    return hreflang_items


def _is_http_url(url: str) -> bool:
    """Return True for http/https URLs."""
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"}


def _is_internal_link(
    url: str,
    allowed_domains: Sequence[str],
    fallback_url: str,
) -> bool:
    """Return True when the URL matches allowed domains or fallback host."""
    parsed = urlparse(url)
    netloc = parsed.netloc.lower()
    if not netloc:
        return False
    domains = [domain.lower() for domain in allowed_domains if domain]
    if not domains:
        fallback_netloc = urlparse(fallback_url).netloc.lower()
        domains = [fallback_netloc] if fallback_netloc else []
    for domain in domains:
        if netloc == domain or netloc.endswith(f".{domain}"):
            return True
    return False


def _parse_rel_tokens(value: Optional[str]) -> List[str]:
    """Parse rel attribute into lower-case tokens."""
    if not value:
        return []
    tokens = [token.strip().lower() for token in value.replace(",", " ").split()]
    return _unique_in_order([token for token in tokens if token])


def _extract_meta_refresh(response: Response) -> Tuple[Optional[str], Optional[str]]:
    """Extract meta refresh content and URL if present."""
    content = _strip_or_none(
        response.css('meta[http-equiv="refresh"]::attr(content)').get()
    )
    if not content:
        return None, None
    match = re.search(r"url=(.+)", content, flags=re.IGNORECASE)
    if match:
        url = match.group(1).strip(" \"'")
        return content, response.urljoin(url)
    return content, None


class BasicSpider(scrapy.Spider):
    """Crawl pages and extract SEO metadata, links, images, and structure."""

    name = "basic_spider"

    @classmethod
    def from_crawler(
        cls,
        crawler: Crawler,
        *args: Any,
        **kwargs: Any,
    ) -> "BasicSpider":
        """
        Construct the spider and apply runtime settings.

        Returns:
            The initialized spider.
        """
        spider = super().from_crawler(crawler, *args, **kwargs)
        spider._apply_runtime_settings(crawler)
        return spider

    def __init__(
        self,
        start_urls: Optional[Union[str, Sequence[str]]] = None,
        start_url: Optional[str] = None,
        allowed_domains: Optional[Union[str, Sequence[str]]] = None,
        include_html: Union[bool, str] = False,
        download_delay: Optional[Union[str, float]] = None,
        concurrent_requests: Optional[Union[str, int]] = None,
        concurrent_requests_per_domain: Optional[Union[str, int]] = None,
        autothrottle: Optional[Union[str, bool]] = None,
        autothrottle_target_concurrency: Optional[Union[str, float]] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Initialize spider settings and link extractor.

        Returns:
            None
        """
        super().__init__(*args, **kwargs)
        if start_urls is None:
            start_urls = start_url
        self.start_urls: List[str] = _normalize_start_urls(start_urls)
        if not self.start_urls:
            raise ValueError(
                "start_urls is required. Pass -a start_urls=https://example.com"
            )

        if allowed_domains is None:
            derived_domains = [urlparse(url).netloc for url in self.start_urls if url]
            self.allowed_domains: List[str] = _unique_in_order(
                [domain for domain in derived_domains if domain]
            )
        else:
            self.allowed_domains = _normalize_allowed_domains(allowed_domains)

        allow_domains = self.allowed_domains or None
        self.link_extractor = LinkExtractor(allow_domains=allow_domains, unique=True)
        self.include_html = _is_truthy(include_html)
        self.download_delay = _parse_float(download_delay)
        self.concurrent_requests = _parse_int(concurrent_requests)
        self.concurrent_requests_per_domain = _parse_int(
            concurrent_requests_per_domain
        )
        self.autothrottle_enabled = (
            _is_truthy(autothrottle) if autothrottle is not None else None
        )
        self.autothrottle_target_concurrency = _parse_float(
            autothrottle_target_concurrency
        )

        self.logger.info("Initialized spider with start URLs: %s", self.start_urls)
        self.logger.info("Allowed domains: %s", self.allowed_domains or "any")

    def _apply_runtime_settings(self, crawler: Crawler) -> None:
        """
        Apply per-run crawl settings supplied via spider arguments.

        Returns:
            None
        """
        if self.download_delay is not None:
            crawler.settings.set(
                "DOWNLOAD_DELAY",
                self.download_delay,
                priority="spider",
            )
        if self.concurrent_requests is not None:
            crawler.settings.set(
                "CONCURRENT_REQUESTS",
                self.concurrent_requests,
                priority="spider",
            )
        if self.concurrent_requests_per_domain is not None:
            crawler.settings.set(
                "CONCURRENT_REQUESTS_PER_DOMAIN",
                self.concurrent_requests_per_domain,
                priority="spider",
            )
        if self.autothrottle_enabled is not None:
            crawler.settings.set(
                "AUTOTHROTTLE_ENABLED",
                self.autothrottle_enabled,
                priority="spider",
            )
        if self.autothrottle_target_concurrency is not None:
            crawler.settings.set(
                "AUTOTHROTTLE_TARGET_CONCURRENCY",
                self.autothrottle_target_concurrency,
                priority="spider",
            )
    def start_requests(self) -> Iterator[scrapy.Request]:
        """
        Yield initial requests for configured start URLs.

        Returns:
            An iterator of Scrapy requests.
        """
        for url in self.start_urls:
            self.logger.info("Generating request for %s", url)
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response: Response) -> Iterator[Union[PageItem, scrapy.Request]]:
        """
        Parse a response and yield SEO-enriched items and follow-up requests.

        Returns:
            An iterator of items and follow-up requests.
        """
        if not _is_html_response(response):
            return

        parsed_url = urlparse(response.url)
        url_without_query = parsed_url._replace(query="", fragment="").geturl()

        content_type = _decode_header(response.headers.get("Content-Type"))
        content_length = _decode_header(response.headers.get("Content-Length"))
        content_length_value = None
        if content_length and content_length.isdigit():
            content_length_value = int(content_length)
        response_size_bytes = len(response.body) if response.body else 0
        x_robots_tag = _decode_header(response.headers.get("X-Robots-Tag"))

        meta_refresh, meta_refresh_url = _extract_meta_refresh(response)
        meta_charset = _extract_charset(response)
        meta_viewport = _strip_or_none(
            response.css('meta[name="viewport"]::attr(content)').get()
        )
        meta_keywords = _split_meta_keywords(
            _strip_or_none(response.css('meta[name="keywords"]::attr(content)').get())
        )

        title = _strip_or_none(response.xpath("normalize-space(//title/text())").get())
        meta_description = _strip_or_none(
            response.css('meta[name="description"]::attr(content)').get()
        )
        if not meta_description:
            meta_description = _strip_or_none(
                response.css('meta[property="og:description"]::attr(content)').get()
            )

        title_length = len(title) if title else None
        meta_description_length = len(meta_description) if meta_description else None

        headings: Dict[str, List[str]] = {}
        heading_counts: Dict[str, int] = {}
        for level in range(1, 7):
            values = []
            for element in response.xpath(f"//h{level}"):
                text = _strip_or_none(element.xpath("normalize-space(string())").get())
                if text:
                    values.append(text)
            headings[f"h{level}"] = values
            heading_counts[f"h{level}"] = len(values)

        visible_text = _extract_visible_text(response)
        word_count = _word_count(visible_text)
        text_length = len(visible_text) if visible_text else 0

        images: List[ImageItem] = []
        for img in response.css("img"):
            src = _strip_or_none(img.attrib.get("src"))
            data_src = _strip_or_none(img.attrib.get("data-src"))
            if not src and data_src:
                src = data_src
            srcset = _strip_or_none(img.attrib.get("srcset"))
            if src:
                src = response.urljoin(src)
            images.append(
                {
                    "src": src,
                    "alt": _strip_or_none(img.attrib.get("alt")),
                    "title": _strip_or_none(img.attrib.get("title")),
                    "srcset": srcset,
                    "data_src": data_src,
                    "loading": _strip_or_none(img.attrib.get("loading")),
                    "width": _strip_or_none(img.attrib.get("width")),
                    "height": _strip_or_none(img.attrib.get("height")),
                }
            )

        image_count = len(images)
        image_missing_alt_count = sum(1 for image in images if not image.get("alt"))
        image_alt_coverage = None
        if image_count:
            image_alt_coverage = (image_count - image_missing_alt_count) / image_count

        links: List[LinkItem] = []
        unique_urls = set()
        link_count_internal = 0
        link_count_external = 0
        link_count_nofollow = 0
        for link in response.css("a[href]"):
            href = link.attrib.get("href")
            if not href:
                continue
            url = response.urljoin(href)
            rel = _strip_or_none(link.attrib.get("rel"))
            rel_tokens = _parse_rel_tokens(rel)
            is_nofollow = "nofollow" in rel_tokens
            is_internal = _is_internal_link(
                url,
                self.allowed_domains,
                response.url,
            )
            if is_nofollow:
                link_count_nofollow += 1
            if _is_http_url(url):
                if is_internal:
                    link_count_internal += 1
                else:
                    link_count_external += 1
            unique_urls.add(url)
            link_text = _strip_or_none(
                link.xpath("normalize-space(string())").get()
            )
            links.append(
                {
                    "url": url,
                    "text": link_text,
                    "rel": rel,
                    "is_internal": is_internal,
                    "is_nofollow": is_nofollow,
                }
            )

        canonical_link = _strip_or_none(
            response.css('link[rel~="canonical"]::attr(href)').get()
        )
        if canonical_link:
            canonical_link = response.urljoin(canonical_link)

        amphtml_link = _strip_or_none(
            response.css('link[rel~="amphtml"]::attr(href)').get()
        )
        if amphtml_link:
            amphtml_link = response.urljoin(amphtml_link)

        canonical_is_self = None
        if canonical_link:
            canonical_is_self = (
                _normalize_url_for_compare(canonical_link)
                == _normalize_url_for_compare(url_without_query)
            )

        robots_meta = _strip_or_none(
            response.css('meta[name="robots"]::attr(content)').get()
        )
        robots_directives = _parse_directives(robots_meta, x_robots_tag)
        is_indexable = _derive_indexable(robots_directives)
        is_follow = _derive_follow(robots_directives)

        language = _strip_or_none(
            response.xpath("//html/@lang").get()
            or response.xpath("//html/@xml:lang").get()
        )

        open_graph = _flatten_meta_values(
            _extract_prefixed_meta(response, "og:")
        )
        twitter = _flatten_meta_values(
            _extract_prefixed_meta(response, "twitter:")
        )
        structured_data, structured_data_types = _extract_structured_data(response)
        hreflang = _extract_hreflang(response)

        item = PageItem(
            url=response.url,
            url_without_query=url_without_query,
            url_path=parsed_url.path or None,
            url_params=parsed_url.params or None,
            url_query=parsed_url.query or None,
            url_fragment=parsed_url.fragment or None,
            status_code=response.status,
            response_time=response.meta.get("download_latency"),
            content_type=content_type,
            content_length=content_length_value,
            response_size_bytes=response_size_bytes,
            title=title,
            title_length=title_length,
            meta_description=meta_description,
            meta_description_length=meta_description_length,
            meta_keywords=meta_keywords,
            meta_charset=meta_charset,
            meta_viewport=meta_viewport,
            meta_refresh=meta_refresh,
            meta_refresh_url=meta_refresh_url,
            headings=headings,
            heading_counts=heading_counts,
            word_count=word_count,
            text_length=text_length,
            links=links,
            link_count_total=len(links),
            link_count_unique=len(unique_urls),
            link_count_internal=link_count_internal,
            link_count_external=link_count_external,
            link_count_nofollow=link_count_nofollow,
            images=images,
            image_count=image_count,
            image_missing_alt_count=image_missing_alt_count,
            image_alt_coverage=image_alt_coverage,
            canonical_link=canonical_link,
            canonical_is_self=canonical_is_self,
            amphtml_link=amphtml_link,
            robots_meta=robots_meta,
            x_robots=x_robots_tag,
            robots_directives=robots_directives,
            is_indexable=is_indexable,
            is_follow=is_follow,
            language=language,
            open_graph=open_graph,
            twitter=twitter,
            structured_data=structured_data,
            structured_data_types=structured_data_types,
            hreflang=hreflang,
            depth=response.meta.get("depth", 0),
        )

        if self.include_html:
            item["html"] = response.text

        yield item

        for link in self.link_extractor.extract_links(response):
            yield response.follow(link.url, self.parse)
