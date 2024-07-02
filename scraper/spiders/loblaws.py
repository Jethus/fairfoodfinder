import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from scrapy.http import HtmlResponse
from scraper.items import ProductItem

class LoblawsSpider(scrapy.Spider):
    name = "loblaws"
    allowed_domains = ["loblaws.ca"]
    start_urls = [
        "https://www.loblaws.ca/food/fruits-vegetables/fresh-vegetables/c/28195",
        "https://www.loblaws.ca/food/fruits-vegetables/fresh-fruits/c/28194",
        "https://www.loblaws.ca/food/meat/deli-meat/c/59319",
        ]

    def __init__(self):
        # intialize the webdriver
        options = Options()
        options.headless = True
        self.driver = webdriver.Firefox(options=options)

    def closed(self, reason):
        # ensure driver exits when the program does
        self.driver.quit()

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, self.parse_initial)

    def parse_initial(self, response):
        self.driver.get(response.url)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,'[data-testid="pagination"]')))
            
            last_page_number = self.get_last_page_number()
            
            html = self.driver.page_source
            resp = HtmlResponse(url=self.driver.current_url, body=html, encoding='utf-8')
            
            if resp.css('div[data-testid="product-grid"]>*'):
                self.products = resp.css('div[data-testid="product-grid"]>*')
                yield from self.parse(resp)
                if last_page_number is not None:
                    next_page_url = self.get_next_page_url(resp.url, last_page_number)
            
                if next_page_url:
                    yield scrapy.Request(next_page_url, self.parse_initial)
                else: return

        except TimeoutException:
            self.log("Timeout while waiting for product grid on " + response.url)

    def parse(self, response):
        products = response.css('div[data-testid="product-grid"]>*')
        for product in products:
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
            yield item
                
    def extract_size(self, product):
        # $1.32/100g -> error data
        product_size_text = product.css('[data-testid="product-package-size"]::text').get(default='')
        print("OVER HERE BRO", product_size_text)
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
    
    def get_next_page_url(self, current_url, last_page_number):
        # Extract the base URL and the current page number if present
        if 'page=' in current_url:
            base_url, current_page_number = current_url.split("?page=")
            current_page_number = int(current_page_number)  # Convert page number to an integer
        else:
            base_url = current_url
            current_page_number = 1  # Assume the current page is 1 if 'page=' is not in URL

        next_page_number = current_page_number + 1  # Calculate the next page number

        # Only generate the next page URL if it does not exceed the last known page number
        if next_page_number > last_page_number:
            return None  # There are no more pages to fetch

        # Construct the next page URL
        next_page_url = f"{base_url}?page={next_page_number}"
        return next_page_url

    def get_last_page_number(self):
        try:
            last_page_element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="pagination"] > :nth-last-child(2)'))
            )
            return int(last_page_element.text.strip())
        except TimeoutException: return None
        

        # TODO
        # separation of code
        # extract and abtract away everything you can