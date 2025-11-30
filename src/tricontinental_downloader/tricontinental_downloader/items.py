"""Item definitions for the tricontinental downloader spiders.

Keep items small and serializable; pipelines expect the default mapping
structure produced by Scrapy's Item objects.
"""

import scrapy


class TricontinentalDownloaderItem(scrapy.Item):
    """Placeholder item for scraper outputs.

    Extend with fields as needed by the scraping pipeline.
    """
    # define the fields for your item here like:
    # name = scrapy.Field()
