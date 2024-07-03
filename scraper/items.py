# Define here the models for your scraped items
#
# See documentation in:
# https://docs.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class ProductItem(Item):
    store = Field()
    category = Field()
    name = Field()
    price = Field()
    unit_price = Field()
    sale_price = Field()
    previous_price = Field()
    image_url = Field()
    link = Field()
    brand = Field()
    package_size = Field()
    stock = Field()
    points = Field()
    date_scraped = Field()
    product_id = Field()
    # ingredients = Field()
    # nutritional_info = Field()
    # origin = Field()
    organic = Field()