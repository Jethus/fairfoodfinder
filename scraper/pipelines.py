# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter
import json

class CategoryStoragePipeline:
    def open_spider(self, spider):
        self.data = {}

    def process_item(self, spider, item):
        store = item['store']
        category = item['category']
        if store not in self.data:
            self.data[store] = {}
        if category not in self.data[store]:
            self.data[store][category] = []
        self.data[store][category].append(dict(item))
        return item
    
    def close_spider(self, spider):
        # Write to database or file
        with open('output.json', 'w') as f:
            json.dump(self.data, f, indent=4)
