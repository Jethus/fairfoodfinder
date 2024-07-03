import asyncio
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from twisted.internet import asyncioreactor
asyncioreactor.install()
from twisted.internet import reactor

from scraper.spiders.loblaws import LoblawsSpider

async def run_spider():
    settings = get_project_settings()
    runner = CrawlerRunner(settings)
    await runner.crawl(LoblawsSpider)

if __name__ == '__main__':
    asyncio.run(run_spider())