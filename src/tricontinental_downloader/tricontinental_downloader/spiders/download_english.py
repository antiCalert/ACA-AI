"""Spider to discover and download English PDF documents from thetricontinental.org.

This spider crawls internal pages, filters out non-English sections and
yields download requests for PDFs. The implementation is conservative and
follows only internal links to avoid leaking to external domains.
"""

import scrapy


class EnglishPDFDownloaderSpider(scrapy.Spider):
    """Crawl the site and yield file download items for English PDFs."""

    name = "download_english"
    allowed_domains = ["thetricontinental.org"]
    start_urls = ["https://thetricontinental.org/"]

    custom_settings = {
        "DOWNLOAD_DELAY": 2.0,
        "ROBOTSTXT_OBEY": True,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 2,
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_START_DELAY": 1.0,
        "AUTOTHROTTLE_TARGET_CONCURRENCY": 1.5,
        "FILES_STORE": "pdf_raw",
        "ITEM_PIPELINES": {"tricontinental_downloader.pipelines.EnglishPDFPipeline": 1},
        "LOG_LEVEL": "INFO",
    }

    def parse(self, response):
        """Parse a page, yield file items and follow internal links.

        The parser filters out non-English sections and avoids a set of
        known blocking URL patterns.
        """
        # Skip non-English language sections
        if any(lang in response.url for lang in ["/es/", "/pt/", "/fr/", "/zh/"]):
            return

        # Extract PDF links
        for href in response.css('a[href$=".pdf"]::attr(href)').getall():
            pdf_url = response.urljoin(href)

            # Skip non-English PDFs (filename-based detection)
            lower = pdf_url.lower()
            if any(
                code in lower
                for code in [
                    "/es/",
                    "/pt/",
                    "/fr/",
                    "/zh/",
                    "-es.",
                    "-pt.",
                    "-fr.",
                    "-zh.",
                    "_es",
                    "_pt",
                    "_fr",
                    "_zh",
                    "-spanish",
                    "-portuguese",
                    "-french",
                    "-chinese",
                ]
            ):
                continue

            yield {
                "file_urls": [pdf_url],
                "referring_page": response.url,
            }

        # Follow only internal English pages
        for a in response.css("a::attr(href)").getall():
            next_page = response.urljoin(a)
            if not next_page.startswith("https://thetricontinental.org/"):
                continue

            blocked = [
                "/es/",
                "/pt/",
                "/fr/",
                "/zh/",
                "/donate/",
                "/search",
                "/author",
                "/tag",
                "/category",
            ]
            if any(b in next_page for b in blocked):
                continue

            yield response.follow(next_page, callback=self.parse)
