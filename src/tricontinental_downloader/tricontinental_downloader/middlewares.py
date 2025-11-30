"""Spider and downloader middleware for the tricontinental downloader.

This module contains lightweight middleware hooks required by Scrapy. The
implementations are intentionally minimal and mainly present to allow
project-specific extensions later.
"""

from scrapy import signals


class TricontinentalDownloaderSpiderMiddleware:
    """Spider middleware hooks (minimal defaults).

    This class supplies no-op implementations of the common middleware
    hooks so projects can opt-in to overriding behaviours as needed.
    """

    @classmethod
    def from_crawler(cls, crawler):
        """Create middleware instance from a crawler object.

        This hook connects the spider_opened signal so middleware can
        perform initialization when the spider starts.
        """
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, _response, _spider):
        """Process each incoming response before the spider parses it.

        Returning ``None`` continues normal processing. Implementations may
        raise to signal errors.
        """
        return None

    def process_spider_output(self, _response, result, _spider):
        """Yield the results returned from the Spider.

        Use ``yield from`` to forward the iterable without materializing it.
        """
        yield from result

    def process_spider_exception(self, _response, _exception, _spider):
        """Handle exceptions raised during spider input processing.

        Returning ``None`` continues the exception propagation. Implementors
        may return an iterable of Requests or items to recover.
        """
        return None

    async def process_start(self, start):
        """Pass through items/requests from an async start iterator.

        This is a thin passthrough that yields each item or request
        produced by the spider start coroutine.
        """
        async for item_or_request in start:
            yield item_or_request

    def spider_opened(self, spider):
        """Log spider opened event."""
        spider.logger.info(f"Spider opened: {spider.name}")


class TricontinentalDownloaderDownloaderMiddleware:
    """Downloader middleware hooks (default no-op implementations)."""

    @classmethod
    def from_crawler(cls, crawler):
        """Create downloader middleware from the crawler and connect signals."""
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, _request, _spider):
        """Inspect or modify a downloader request before it is sent.

        Returning ``None`` continues normal processing.
        """
        return None

    def process_response(self, _request, response, _spider):
        """Return or replace the downloader response.

        Typical implementations would inspect the response and optionally
        return a different Request/Response. This default just passes it
        through.
        """
        return response

    def process_exception(self, _request, _exception, _spider):
        """Handle exceptions raised during downloader request processing.

        Return ``None`` to continue exception handling; return a Response or
        Request to short-circuit the chain.
        """
        return None

    def spider_opened(self, spider):
        """Log spider opened event."""
        spider.logger.info(f"Spider opened: {spider.name}")
