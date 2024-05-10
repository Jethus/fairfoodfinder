# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter
import json


class CategoryStoragePipeline:
    def open_spider(self, spider):
        self.data_by_category = {}

    def process_item(self, spider, item):
        category = item.get('category')
        if category not in self.data_by_category:
            self.data_by_category[category] = []

        self.data_by_category[category].append(dict(item))
        return item
    
    def close_spider(self, spider):
        # Write to database or file
        with open('output.json', 'w') as f:
            json.dump(self.data_by_category, f)
