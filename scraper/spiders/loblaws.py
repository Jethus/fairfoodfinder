import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from scrapy.http import HtmlResponse
from items import ProductItem

import time

class LoblawsSpider(scrapy.Spider):
    name = "loblaws-vegetables"
    allowed_domains = ["loblaws.ca"]
    start_urls = ["https://www.loblaws.ca/food/fruits-vegetables/fresh-vegetables/c/28195"]

    def __init__(self):
        # intialize the webdriver and set the last page number
        options = Options()
        options.headless = True
        self.driver = webdriver.Firefox(options=options)
        self.last_page_number = None
        self.products = None

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
                lambda driver: len(driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="product-grid"]>*')) > 20
            )
            # Only fetch the last page number if it hasn't been set yet
            if self.last_page_number is None:
                self.last_page_number = self.get_last_page_number()
            
            html = self.driver.page_source
            resp = HtmlResponse(url=self.driver.current_url, body=html, encoding='utf-8')
            
            if resp.css('div[data-testid="product-grid"]>*'):
                self.products = resp.css('div[data-testid="product-grid"]>*')
                time.sleep(5)
                yield from self.parse(resp)
                if self.last_page_number is not None:
                    next_page_url = self.get_next_page_url(resp.url)
            
                if next_page_url:
                    yield scrapy.Request(next_page_url, self.parse_initial)
                else: return

        except TimeoutException:
            self.log("Timeout while waiting for product grid on " + response.url)

    def parse(self, response):
            for product in self.products:
                item = ProductItem()
                item['name'] = product.css('[data-testid="product-title"]::text').get(default='No name available')
                self.extract_price(product, item)
                item['image_url'] = product.css('[data-testid="product-image"] img::attr(src)').get(default='')
                item['link'] = response.urljoin(product.css('a::attr(href)').get(default=''))
                item['brand'] = product.css('[data-testid="product-brand"]::text').get(default='')
                item['package-size'] = product.css('[data-testid="product-package-size"]::text').get(default='')
                item['points'] = product.css('[data-testid="product-pco-badge"]::text').get(default='')
                

    def extract_price(self, product, item):
        price_info = product.css('div:has(>[data-testid="price-product-tile"]')
        regular_price = price_info.css('[data-testid="regular-price"] span::text').get()
        sale_price = price_info.css('[data-testid="sale-price"] span::text').get()
        was_price = price_info.css('[data-testid="was-price"] span::text').get()
        return {'regular_price': regular_price, 'sale_price': sale_price, 'was_price': was_price}
    
    def get_next_page_url(self, current_url):
        # Extract the base URL and the current page number if present
        if 'page=' in current_url:
            base_url, current_page_number = current_url.split("?page=")
            current_page_number = int(current_page_number)  # Convert page number to an integer
        else:
            base_url = current_url
            current_page_number = 1  # Assume the current page is 1 if 'page=' is not in URL

        next_page_number = current_page_number + 1  # Calculate the next page number

        # Only generate the next page URL if it does not exceed the last known page number
        if next_page_number > self.last_page_number:
            return None  # There are no more pages to fetch

        # Construct the next page URL
        next_page_url = f"{base_url}?page={next_page_number}"
        return next_page_url

    def get_last_page_number(self):
        try:
            last_page_element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'nav[data-testid="pagination"] > :nth-last-child(2)'))
            )
            return int(last_page_element.text.strip())
        except TimeoutException: return None
        

        # TODO
        # separation of code
        # LobLawsProductItem under items file
        # extract and abtract away everything you can