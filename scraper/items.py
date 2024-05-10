# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class ProductItem(scrapy.Item):
    name = scrapy.Field()
    price = scrapy.Field()
    unit_price = scrapy.Field()
    sale_price = scrapy.Field()
    previous_price = scrapy.Field()
    image_url = scrapy.Field()
    link = scrapy.Field()
    brand = scrapy.Field()
    package_size = scrapy.Field()
    points = scrapy.Field()