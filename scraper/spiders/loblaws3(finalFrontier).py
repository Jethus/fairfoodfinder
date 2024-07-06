import scrapy
import hashlib
from scraper.items import ProductItem
from datetime import datetime
import json

class LobLawsSpider(scrapy.Spider):
    name = "loblaws"
    allowed_domains = ["api.pcexpress.ca"]

    def start_requests(self):
        url = "https://api.pcexpress.ca/pcx-bff/api/v2/listingPage/27985"
        primaryUrls = self.get_navigation_nodes(self.parse_url(url))
        subUrls = []
        for url in primaryUrls:
            self.get_subnavigation_nodes(self.parse(url))

    def parse_url(self, url, callback=None):
        if callback is None:
            callback = self.parse

        headers = {
            "Accept-Language": "en",
            "x-apikey": "C1xujSegT5j3ap3yexJjqhOfELwGKYvz",
            "x-application-type": "Web",
            "x-loblaw-tenant-id": "ONLINE_GROCERIES",
        }
        payload = {
            "banner": "loblaw",
            "cart": {"cartId": "00000000-0000-0000-0000-000000000000"},
            "fulfillmentInfo": {"storeId": "1001"}
        }
        yield scrapy.Request(
            url, 
            method='POST', 
            headers=headers, 
            body=json.dumps(payload),
            callback=callback
        )

    def get_navigation_nodes(self, response):
        try:
            # Navigate to the relevant part of the JSON structure
            navChildren = response['layout']['sections']['productListingSection']['components']['data']['categoryNavigation']['navigation']['childNodes']
            return navChildren
        except KeyError as e:
            print(f"Error navigating JSON: {e}")
        return []
    
    def get_subnavigation_nodes(self, response):
        try:
            # Navigate to the relevant part of the JSON structure
            navChildren = response['layout']['sections']['productListingSection']['components'][0]['data']['navigation']['childNodes']
            return navChildren
        except KeyError as e:
            print(f"Error navigating JSON: {e}")
        return []
    
    def get_navigation_urls(self, navigationNodes):
        urls_info = []
        try:
            for node in navigationNodes:
                if 'url' in node and 'displayName' in node:
                    # Split the URL by '/' and get the last element
                    url_parts = node['url'].split('/')
                    url_name = node['displayName']
                    url_number = url_parts[-1] if url_parts[-1].isdigit() else url_parts[-2]  # Check if the last part is a digit, otherwise take the second last
                    urls_info.append({
                        'categoryName': url_name,
                        'categoryNumber': url_number
                    })
        except KeyError as e:
            print(f"Error accessing data in navigationNodes: {e}")
        return urls_info

    def parse(self, response):
        data = response.json()
        # get primary urls
        # api request urls
        # get sub urls
        # api request urls
        # parse those urls
        navigation_nodes = self.get_navigation_nodes(data)  # This should call a corrected function
        urls_info = self.get_navigation_urls(navigation_nodes)
        for info in urls_info:
            print(f"Category: {info['categoryName']}, ID: {info['categoryNumber']}")

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