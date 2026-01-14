"""
Define here the models for your spider middleware

See documentation in: https://docs.scrapy.org/en/latest/topics/spider-middleware.html
"""

import itertools
import random
from typing import Any, Dict, Iterable, Iterator, Optional, Sequence, Union

from scrapy import signals
from scrapy.crawler import Crawler
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.http import Request, Response
from scrapy.spiders import Spider
from scrapy.utils.response import response_status_message
from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.internet.task import deferLater


class CrawlBotSpiderMiddleware:
    """
    Not all methods need to be defined. If a method is not defined,
    scrapy acts as if the spider middleware does not modify the
    passed objects.
    """
    @classmethod
    def from_crawler(cls, crawler: Crawler) -> "CrawlBotSpiderMiddleware":
        """Create the middleware from a crawler instance."""
        middleware = cls()
        crawler.signals.connect(
            middleware.spider_opened,
            signal=signals.spider_opened,
        )
        return middleware

    def process_spider_input(self, response: Response, spider: Spider) -> None:
        """
        Called for each response that goes through the spider
        middleware and into the spider.

        Should return None or raise an exception.
        """
        return None

    def process_spider_output(
        self,
        response: Response,
        result: Iterable[Any],
        spider: Spider,
    ) -> Iterator[Any]:
        """
        Called with the results returned from the Spider, after
        it has processed the response.

        Must return an iterable of Request, or item objects.
        """
        for output in result:
            yield output

    def process_spider_exception(
        self,
        response: Response,
        exception: Exception,
        spider: Spider,
    ) -> Optional[Iterable[Any]]:
        """
        Called when a spider or process_spider_input() method
        (from other spider middleware) raises an exception.

        Should return either None or an iterable of Request or item objects.
        """
        return None

    def process_start_requests(
        self,
        start_requests: Iterable[Request],
        spider: Spider,
    ) -> Iterator[Request]:
        """
        Called with the start requests of the spider, and works
        similarly to the process_spider_output() method, except
        that it doesn’t have a response associated.
        """
        # Must return only requests (not items).
        for request in start_requests:
            yield request

    def spider_opened(self, spider: Spider) -> None:
        """Log when the spider is opened."""
        spider.logger.info("Spider opened: %s" % spider.name)


class CrawlBotDownloaderMiddleware:
    """
    Not all methods need to be defined. If a method is not defined,
    scrapy acts as if the downloader middleware does not modify the
    passed objects.
    """

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> "CrawlBotDownloaderMiddleware":
        """Create the middleware from a crawler instance."""
        middleware = cls()
        crawler.signals.connect(
            middleware.spider_opened,
            signal=signals.spider_opened,
        )
        return middleware

    def process_request(
        self,
        request: Request,
        spider: Spider,
    ) -> Optional[Union[Response, Request]]:
        """
        Called for each request that goes through the downloader middleware.

        Must either:
        - return None: continue processing this request
        - or return a Response object
        - or return a Request object
        - or raise IgnoreRequest: process_exception() methods of
          installed downloader middleware will be called
        """
        return None

    def process_response(
        self,
        request: Request,
        response: Response,
        spider: Spider,
    ) -> Union[Response, Request]:
        """
        Called with the response returned from the downloader.

        Must either;
        - return a Response object
        - return a Request object
        - or raise IgnoreRequest
        """
        return response

    def process_exception(
        self,
        request: Request,
        exception: Exception,
        spider: Spider,
    ) -> Optional[Union[Response, Request]]:
        """
        Called when a download handler or a process_request()
        (from other downloader middleware) raises an exception.

        Must either:
        - return None: continue processing this exception
        - return a Response object: stops process_exception() chain
        - return a Request object: stops process_exception() chain
        """
        return None

    def spider_opened(self, spider: Spider) -> None:
        """Log when the spider is opened."""
        spider.logger.info("Spider opened: %s" % spider.name)


class PerRequestDelayMiddleware:
    """Apply per-request delays stored in request metadata."""

    def process_request(
        self,
        request: Request,
        spider: Spider,
    ) -> Optional[Union[Response, Request, Deferred]]:
        """
        Delay requests that include a download_delay meta value.

        Returns:
            None, Response, Request, or a Deferred to delay scheduling.
        """
        delay = request.meta.get("download_delay")
        if not delay:
            return None
        return deferLater(reactor, delay, lambda: None)


class RequestHeadersMiddleware:
    """Inject default headers for outbound requests."""

    def __init__(self, headers: Dict[str, str]) -> None:
        """
        Store headers to apply to outgoing requests.

        Returns:
            None
        """
        self.headers = headers

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> "RequestHeadersMiddleware":
        """
        Build middleware using crawler settings.

        Returns:
            Configured middleware instance.
        """
        headers = crawler.settings.getdict("SEO_REQUEST_HEADERS", {})
        return cls(headers=headers)

    def process_request(
        self,
        request: Request,
        spider: Spider,
    ) -> Optional[Union[Response, Request]]:
        """
        Apply headers to the request if not already present.

        Returns:
            None or a Response/Request to short-circuit processing.
        """
        for header, value in self.headers.items():
            if header not in request.headers:
                request.headers[header] = value
        return None


class ProxyRotationMiddleware:
    """Rotate proxies for outgoing requests."""

    def __init__(
        self,
        proxies: Sequence[str],
        mode: str,
        enabled: bool,
    ) -> None:
        """
        Initialize proxy rotation configuration.

        Returns:
            None
        """
        self.proxies = [proxy for proxy in proxies if proxy]
        self.enabled = enabled
        self.mode = mode.lower()
        self.proxy_cycle = itertools.cycle(self.proxies)

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> "ProxyRotationMiddleware":
        """
        Build middleware using crawler settings.

        Returns:
            Configured middleware instance.
        """
        proxies = crawler.settings.getlist("SEO_PROXY_LIST", [])
        mode = crawler.settings.get("SEO_PROXY_MODE", "round_robin")
        enabled = crawler.settings.getbool("SEO_PROXY_ENABLED", False)
        return cls(proxies=proxies, mode=mode, enabled=enabled)

    def process_request(
        self,
        request: Request,
        spider: Spider,
    ) -> Optional[Union[Response, Request]]:
        """
        Attach a proxy to the request when enabled.

        Returns:
            None or a Response/Request to short-circuit processing.
        """
        if not self.enabled or not self.proxies:
            return None
        if request.meta.get("proxy"):
            return None

        if self.mode == "random":
            proxy = random.choice(self.proxies)
        else:
            proxy = next(self.proxy_cycle)
        request.meta["proxy"] = proxy
        return None


class BackoffRetryMiddleware(RetryMiddleware):
    """Retry middleware with exponential backoff support."""

    def __init__(self, settings: Any) -> None:
        """
        Initialize retry backoff configuration.

        Returns:
            None
        """
        super().__init__(settings)
        self.base_delay = settings.getfloat("RETRY_BACKOFF_BASE", 1.0)
        self.max_delay = settings.getfloat("RETRY_BACKOFF_MAX", 60.0)

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> "BackoffRetryMiddleware":
        """
        Build middleware using crawler settings.

        Returns:
            Configured middleware instance.
        """
        return cls(crawler.settings)

    def _retry(
        self,
        request: Request,
        reason: Any,
        spider: Spider,
    ) -> Optional[Request]:
        """
        Schedule a retry request with exponential backoff delay.

        Returns:
            A new request or None if retries are exhausted.
        """
        retry_request = super()._retry(request, reason, spider)
        if retry_request is None:
            return None
        retries = retry_request.meta.get("retry_times", 0)
        delay = min(self.base_delay * (2 ** max(0, retries - 1)), self.max_delay)
        retry_request.meta["download_delay"] = delay
        return retry_request

    def process_response(
        self,
        request: Request,
        response: Response,
        spider: Spider,
    ) -> Union[Response, Request]:
        """
        Retry failed responses while capturing status messages.

        Returns:
            Response or retry request.
        """
        if request.meta.get("dont_retry"):
            return response
        if response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            retry_request = self._retry(request, reason, spider)
            if retry_request:
                return retry_request
        return response
