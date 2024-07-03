import scrapy
import hashlib
from scrapy_playwright.page import PageMethod
from scraper.items import ProductItem
from datetime import datetime


class LoblawsSpider(scrapy.Spider):
    name = "loblaws"
    allowed_domains = ["loblaws.ca"]
    start_urls = [
        "https://www.loblaws.ca/food/fruits-vegetables/fresh-vegetables/c/28195",
        "https://www.loblaws.ca/food/fruits-vegetables/fresh-fruits/c/28194",
        "https://www.loblaws.ca/food/meat/deli-meat/c/59319",
        ]

    def start_requests(self):
        for url in self.start_urls:
            yield self.scrapy_request(url)

    def scrapy_request(self, url, callback=None):
        if callback is None:
            callback = self.parse
        return scrapy.Request(
            url,
            callback=callback,
            errback=self.errback,
            meta=dict(
                playwright=True,
                playwright_include_page=True,
                playwright_page_methods=[
                    PageMethod('wait_for_selector', 'div[data-testid="product-grid"] > *'), # wait for products
                    PageMethod('wait_for_selector', 'a[aria-label="Next Page"]',), # wait for pagination
                ],
            )
        )

    def parse(self, response):
        page = response.meta["playwright_page"]
        try:
            products = response.css('div[data-testid="product-grid"] > *')
            self.logger.info(f"Found {len(products)} products on {response.url}")
            for product in products:
                yield self.create_product_item(product, response)
            yield from self.get_next_page_request(response)
        finally:
            yield page.close()

    def create_product_item(self, product, response):
        item = ProductItem()
        item['store'] = 'loblaws'
        item['category'] = response.css('[data-testid="heading"]::text').get(default='Unknown')
        item['name'] = product.css('[data-testid="product-title"]::text').get(default='No name available')
        item['price'], item['sale_price'], item['previous_price'] = self.extract_price(product)
        item['image_url'] = product.css('[data-testid="product-image"] img::attr(src)').get(default='')
        item['link'] = response.urljoin(product.css('a::attr(href)').get(default=''))
        item['brand'] = product.css('[data-testid="product-brand"]::text').get(default='')
        item['package_size'], item['unit_price'] = self.extract_size(product)
        item['stock'] = product.css('[data-testid="inventory-badge-text"]::text').get(default='In stock')
        item['points'] = product.css('[data-testid="product-pco-badge"]::text').get(default='')
        item['date_scraped'] = datetime.now().isoformat()
        item['product_id'] = self.generate_product_id(item['name'], item['brand'], item['package_size'])
        item['organic'] = 'organic' in item['name'].lower()
        return item
            
    def generate_product_id(self, name, brand, package_size):
        unique_string = f"{name}_{brand}_{package_size}".lower()
        return hashlib.md5(unique_string.encode()).hexdigest()
    
    def extract_size(self, product):
        # $1.32/100g -> error data
        product_size_text = product.css('[data-testid="product-package-size"]::text').get(default='')
        if ',' in product_size_text:
            return [text.strip() for text in product_size_text.split(',', 1)]
        elif ' ' in product_size_text:
            return [text.strip() for text in product_size_text.split(' ', 1)]
        else:
            return '', product_size_text

    def extract_price(self, product):
        price_info = product.css('[data-testid="price-product-tile"]')
        regular_price = price_info.css('[data-testid="regular-price"] span::text').get(default='')
        sale_price = price_info.css('[data-testid="sale-price"] span::text').get(default='')
        previous_price = price_info.css('[data-testid="was-price"] span::text').get(default='')
        return regular_price, sale_price, previous_price
    
    def get_next_page_request(self, response):        
        next_page = response.css('a[aria-label="Next Page"]::attr(href)').get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            self.logger.info(f"Next page URL: {next_page}")
            yield self.scrapy_request(next_page_url)
        else:
            self.logger.info("No next page found. Ending pagination.")
    
    def errback(self, failure):
        page = failure.request.meta["playwright_page"]
        self.logger.error(f"Playwright page error: {failure}")
        page.close()