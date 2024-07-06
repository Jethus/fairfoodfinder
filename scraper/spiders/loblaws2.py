import scrapy
import hashlib
from scrapy_playwright.page import PageMethod
from scraper.items import ProductItem
from datetime import datetime

class LobLawsSpider(scrapy.Spider):
    name = "loblawsAgent"
    allowed_domains = ["loblaws.ca"]
    start_urls = ["https://www.loblaws.ca/food/c/27985"]
    category_urls = []
    subcategory_urls = []

    def start_requests(self):
        for url in self.start_urls:
            yield self.playwright_request(url, self.parse_categories)
    
    def playwright_request(self, url, callback):
        return scrapy.Request(
            url,
            callback=callback,
            meta=dict(
                playwright=True,
                playwright_include_page=True,
                playwright_page_methods=[
                    PageMethod('wait_for_selector', '[data-testid="accordion-item"]'),
                ],
                dont_filter=True
            )
        )
    
    def items_request(self, url, callback):
        return scrapy.Request(
            url,
            callback=callback,
            meta=dict(
                playwright=True,
                playwright_include_page=True,
                playwright_page_methods=[
                    PageMethod('wait_for_selector', '[data-testid="product-grid"] > *'),
                    PageMethod('evaluate', '''
                    async () => {
                        const grid = await page.waitForSelector('[data-testid="product-grid"] > *');
                        try {
                            await page.waitForSelector('[data-testid="pagination"]', {timeout: 5000});
                        } catch (e) {
                            if (e instanceof playwright.errors.TimeoutError) {
                                console.log('Less than 48 products, no pagination.');
                            } else {
                                throw e; // Re-throw the error if it is not a TimeoutError
                            }
                        }
                        return grid; // Proceed with parsing the grid
                    }
                ''')
                ],
                dont_filter=True
            )
        )
    
    def parse_categories(self, response):
        page = response.meta["playwright_page"]
        print("PARSING CATEGORIES")
        category_links = response.css('[data-testid="nav-list-link"]')
        for link in category_links:
            link_text = link.css('::text').get()
            link_url = link.css('::attr(href)').get()
            if "See All" not in link_text:
                full_url = response.urljoin(link_url)
                yield self.playwright_request(full_url, self.parse_subcategories)
                print("CATEGORY Number of URLS: ", len(self.category_urls))
        yield page.close()

    def parse_subcategories(self, response):
        page = response.meta["playwright_page"]
        print("PARSING SUBCATEGORIES")
        subcategory_links = response.css('[data-testid="nav-list-link"]')
        for link in subcategory_links:
            link_text = link.css('::text').get()
            link_url = link.css('::attr(href)').get()
            if "See All" in link_text:
                full_url = response.urljoin(link_url)
                yield self.items_request(full_url, self.parse_items)
                print("SUBCATEGORY Number of URLS: ", len(self.category_urls))
        yield page.close()

    def parse_items(self, response):
        page = response.meta["playwright_page"]
        products = response.css('div[data-testid="product-grid"] > *')
        for product in products:
            yield self.create_product_item(product, response)
        
        next_page = response.css('a[aria-label="Next Page"]::attr(href)').get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            yield self.items_request(next_page_url, self.parse_items)
        yield page.close()

    def create_product_item(self, product, response):
        item = ProductItem()
        item['store'] = 'loblaws'
        item['category'] = response.css('[data-testid="heading"]::text').get(default='Unknown')
        item['subcategory'] = response.css('[data-testid="back-link"]::text').get(default='Unknown')
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
    
    def errback(self, failure):
        page = failure.request.meta["playwright_page"]
        self.logger.error(f"Playwright page error: {failure}")
        yield page.close()