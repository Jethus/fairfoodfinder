# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter
import logging
import psycopg2
from scrapy.exceptions import NotConfigured

class GeneralPipeline:
    def __init__(self, postgres_uri):
        self.postgres_uri = postgres_uri
        self.conn = None
        self.cur = None

    @classmethod
    def from_crawler(cls, crawler):
        postgres_uri = crawler.settings.get('POSTGRES_URI')
        if not postgres_uri:
            raise NotConfigured("POSTGRES_URI is not set")
        return cls(postgres_uri)
    
    def spider_opened(self, spider):
        logging.info(f"Attempting to connect to PostgreSQL with URI: {self.postgres_uri}")
        try:
            self.conn = psycopg2.connect(self.postgres_uri)
            self.cur = self.conn.cursor()
            logging.info("Connected to PostgreSQL database")
        except psycopg2.Error as e:
            logging.error(f"Unable to connect to PostgreSQL: {e}")
            raise

    def spider_closed(self, spider):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
        logging.info("Closed PostgreSQL database connection")

    def process_item(self, item, spider):
        spider.logger.info(f"Processing item in pipeline: {item}")
        try:
            self.cur.execute("""
            INSERT INTO products (
                store, category, name, price, unit_price, sale_price, previous_price, 
                image_url, link, brand, package_size, stock, points, date_scraped,
                product_id, organic
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """, (
            item.get('store'), item.get('category'), item.get('name'), item.get('price'),
            item.get('unit_price'), item.get('sale_price'), item.get('previous_price'),
            item.get('image_url'), item.get('link'), item.get('brand'), item.get('package_size'),
            item.get('stock'), item.get('points'), item.get('date_scraped'), item.get('product_id'),
            item.get('organic')
        ))
            self.conn.commit()
            spider.logger.info(f"Item inserted into database: {item['name']}")
        except Exception as e:
            spider.logger.error(f"Error inserting item into database: {e}")
            self.conn.rollback()
        return item