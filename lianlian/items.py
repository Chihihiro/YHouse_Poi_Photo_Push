# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CrawlLianlianItem(scrapy.Item):
    city = scrapy.Field()
    id = scrapy.Field()
    address = scrapy.Field()
    # stores_name = scrapy.Field()
    title = scrapy.Field()
    original_price = scrapy.Field()#原价
    price = scrapy.Field()#价格
    sales = scrapy.Field()# 销量
    title_name = scrapy.Field()# 销量

    pass