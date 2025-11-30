"""Scrapy settings for the tricontinental_downloader project.

This file contains a minimal set of settings used by the included spider
and pipelines. For full Scrapy configuration options, consult the
official Scrapy documentation.
"""

BOT_NAME = "tricontinental_downloader"

SPIDER_MODULES = ["tricontinental_downloader.spiders"]
NEWSPIDER_MODULE = "tricontinental_downloader.spiders"

ADDONS = {}


# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = "tricontinental_downloader (+http://www.yourdomain.com)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Concurrency and throttling settings
# CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_DELAY = 1

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
# }

# Enable or disable spider middlewares
# See Scrapy docs for spider middleware examples.
# SPIDER_MIDDLEWARES = {
#    "tricontinental_downloader.middlewares.TricontinentalDownloaderSpiderMiddleware": 543,
# }

# Enable or disable downloader middlewares
# See Scrapy docs for downloader middleware examples.
# DOWNLOADER_MIDDLEWARES = {
#    "tricontinental_downloader.middlewares.TricontinentalDownloaderDownloaderMiddleware": 543,
# }

# Enable or disable extensions
# See Scrapy extensions documentation for optional extensions.
# EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
# }

# Configure item pipelines
# See Scrapy item pipeline documentation for pipeline configuration.
# ITEM_PIPELINES = {
#    "tricontinental_downloader.pipelines.TricontinentalDownloaderPipeline": 300,
# }

# Enable and configure the AutoThrottle extension (disabled by default)
# See Scrapy autothrottle documentation for tuning options.
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See Scrapy HTTP cache settings documentation for cache options.
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = "httpcache"
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
FEED_EXPORT_ENCODING = "utf-8"

ITEM_PIPELINES = {
    "scrapy.pipelines.files.FilesPipeline": 1,
}

FILES_STORE = "english_pdfs_raw"
