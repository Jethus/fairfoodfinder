import scrapy
import json
import hashlib
from datetime import datetime
from scraper.items import ProductItem  # Ensure this is correctly imported from your project structure
import logging

class LobLawsSpider(scrapy.Spider):
    name = "loblaws"
    allowed_domains = ["api.pcexpress.ca"]

    def start_requests(self):
        url = "https://api.pcexpress.ca/pcx-bff/api/v2/listingPage/27985"
        logging.info("HELLO THERE")
        yield scrapy.Request(
            url, 
            method='POST', 
            headers=self.get_headers(),
            body=json.dumps(self.get_payload()),
            callback=self.parse_primary
        )

    def get_headers(self):
        return {
            "Accept-Language": "en",
            "x-apikey": "C1xujSegT5j3ap3yexJjqhOfELwGKYvz",
            "x-application-type": "Web",
            "x-loblaw-tenant-id": "ONLINE_GROCERIES",
        }

    def get_payload(self):
        return {
            "banner": "loblaw",
            "cart": {"cartId": "00000000-0000-0000-0000-000000000000"},
            "fulfillmentInfo": {"storeId": "1001"}
        }

    def parse_primary(self, response):
        data = response.json()
        logging.info(response.text)
        primary_nav_nodes = self.get_navigation_nodes(data)
        primary_urls = self.get_navigation_urls(primary_nav_nodes)

        # Process each primary URL to fetch sub-navigation nodes
        for url_info in primary_urls:
            full_url = response.urljoin(url_info['categoryUrl'])
            yield scrapy.Request(full_url, callback=self.parse_subnavigation)

    def get_navigation_nodes(self, data):
        try:
            components = data['layout']['sections']['productListingSection']['components']
            for component in components:
                if 'data' in component and 'categoryNavigation' in component['data']:
                    return component['data']['categoryNavigation']['navigation']['childNodes']
        except KeyError as e:
            self.logger.error(f"Error navigating JSON: {e}")
        return []

    def parse_subnavigation(self, response):
        data = response.json()
        sub_nav_nodes = self.get_subnavigation_nodes(data)
        sub_urls = self.get_navigation_urls(sub_nav_nodes)
        
        # Print sub URLs
        for info in sub_urls:
            print(f"Sub Category: {info['categoryName']}, ID: {info['categoryNumber']}")

    def get_subnavigation_nodes(self, data):
        try:
            components = data['layout']['sections']['productListingSection']['components'][0]['data']['navigation']['childNodes']
            return components
        except KeyError as e:
            self.logger.error(f"Error navigating JSON: {e}")
        return []

    def get_navigation_urls(self, navigationNodes):
        urls_info = []
        for node in navigationNodes:
            if 'url' in node and 'displayName' in node:
                url_parts = node['url'].split('/')
                url_number = url_parts[-1] if url_parts[-1].isdigit() else url_parts[-2]  # Handle cases where the last part is not a digit
                urls_info.append({
                    'categoryName': node['displayName'],
                    'categoryNumber': url_number,
                    'categoryUrl': node['url']
                })
        return urls_info
