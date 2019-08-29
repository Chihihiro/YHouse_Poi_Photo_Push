# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CrawlLianlianItem(scrapy.Item):
    city = scrapy.Field()
    product_id = scrapy.Field()
    product_name = scrapy.Field()
    product_title = scrapy.Field()
    # title_name = scrapy.Field()  # 销量
    address = scrapy.Field()
    tel = scrapy.Field()
    original_price = scrapy.Field()#原价
    sale_price = scrapy.Field()#价格
    sale_amount = scrapy.Field()# 销量
    stock_amount = scrapy.Field()
    single_min = scrapy.Field()
    single_max = scrapy.Field()
    sold_out = scrapy.Field()# s售罄
    valid_begin_date = scrapy.Field()
    valid_end_date = scrapy.Field()
    pass

class LianlianItem(scrapy.Item):
    product_id = scrapy.Field()
    item_id = scrapy.Field()
    sub_title = scrapy.Field()
    original_price = scrapy.Field()
    sale_price = scrapy.Field()  # 销量
    sold_out = scrapy.Field()

class LianlianshopItem(scrapy.Item):
    product_id = scrapy.Field()
    shop_name = scrapy.Field()
    shop_address = scrapy.Field()
    phone_number = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()  # 销量
    memo = scrapy.Field()
    scale = scrapy.Field()