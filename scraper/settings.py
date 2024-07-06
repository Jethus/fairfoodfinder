# Scrapy settings for scraper project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "fairfoodfinder"

# Spiders
SPIDER_MODULES = ['scraper.spiders']
NEWSPIDER_MODULE = 'scraper.spiders'

# Respect robots.txt rules
ROBOTSTXT_OBEY = True

# Playwright settings
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

# Update ITEM_PIPELINES
# ITEM_PIPELINES = {
#    "scraper.pipelines.GeneralPipeline": 300,
# }

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"


# # Set a custom user agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
# # uses default browser user agent when set to none
# PLAYWRIGHT_BROWSER_TYPE = "chromium"
# USER_AGENT = None

# # PostgreSQL settings
import os
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_HOST = os.getenv('POSTGRES_HOST')
POSTGRES_URI = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:5432/{POSTGRES_DB}'

PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": False,
}

# # Concurrent requests
DEPTH_PRIORITY = 1
CONCURRENT_REQUESTS = 2

# # Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS_PER_DOMAIN = 8

# # Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# # Enable and configure HTTP caching (disabled by default)
# HTTPCACHE_ENABLED = False
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

