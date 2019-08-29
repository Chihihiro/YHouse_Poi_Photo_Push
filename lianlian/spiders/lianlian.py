# -*- coding: utf-8 -*-
import scrapy
import re
import pandas as pd
import json
from copy import deepcopy
from scrapy import Request
from lianlian.iosjk import to_sql
from lianlian.items import CrawlLianlianItem, LianlianItem, LianlianshopItem
from lianlian.engines import choise_engine as engine







class LianlianSpider(scrapy.Spider):
    name = 'lianlian'
    start_urls = ['https://api.lianlianlvyou.com/v1/wx/city/list?i=&locationid=0']

    custom_settings = {
        "DOWNLOADER_MIDDLEWARES": {
            'lianlian.middlewares.CrawlLianlianDownloaderMiddleware': 543,
        },
        "ITEM_PIPELINES": {
            'lianlian.pipelines.CrawlYhousePipeline': 300,
        }
    }

    def parse(self, response):
        info = json.loads(response.body)
        data = info['data']["allSiteList"]
        print(data)
        bb = [i['siteList'] for i in data]
        item = CrawlLianlianItem()
        n = 0
        for b in bb:
            for id in b:
                city_id = id['id']
                print(city_id)
                n += 1
                print(n, id['city'])
                item['city'] = id['city']
                url = 'https://api.lianlianlvyou.com/v1/wx/list?i=&t=1&pageSize=10&pageIndex=1&locationid=' + str(
                    city_id)
                yield Request(url, callback=self.Details_page, meta={"item": deepcopy(item)})

    def Details_page(self, response):
        info = json.loads(response.body)
        df = pd.DataFrame([info]).T
        df.columns = ['json']

        count = info['data']['list']['rowCount']
        cc = int(count / 10)
        item = response.meta["item"]
        url = response.url
        print(url)
        for i in range(1, cc + 1):
            url2 = url.replace('pageIndex=1', 'pageIndex=' + str(i))
            print(url2)
            yield Request(url2, callback=self.next_page, meta={"item": deepcopy(item)})

    def next_page(self, response):
        info = json.loads(response.body)
        df = pd.DataFrame([info]).T
        df.columns = ['json']
        data = info['data']['list']['data']
        item = response.meta["item"]
        print(item)

        for stores in data:
            print(stores)
            stores_id = stores['id']

            url = 'https://api.lianlianlvyou.com/v1/wx/product2?i=&id=' + str(stores_id)

            try:
                yield Request(url, callback=self.address_page, meta={"item": deepcopy(item)})
            except KeyError:
                df = pd.DataFrame([url]).T
                df.columns = ['url']
                to_sql('wrong_url', engine, df, type='update')

    def address_page(self, response):
        info = json.loads(response.body)
        data = info['data']['bizProduct']
        item = response.meta["item"]
        city = item.get('city')

        item['city'] = city
        item['product_id'] = data['id']
        item['product_name'] = data['name']
        item['product_title'] = data['title']
        item['address'] = re.sub('商家地址：','', data['address'])
        item['tel'] = re.sub('咨询电话：|配送范围：|商家电话：|电话：','', data['tel'])
        item['sale_price'] = re.search('\d+',data['salePriceStr']).group()
        item['original_price'] = re.search('\d+',data['originPriceStr']).group()
        item['sale_amount'] = data['saleAmount']
        item['stock_amount'] = data['stockAmount']
        item['single_min'] = data['singleMin']
        item['single_max'] = data['singleMax']
        item['sold_out'] = data['isSoldOut']
        item['valid_begin_date'] = data['validBeginDate']
        item['valid_end_date'] = data['validEndDate']

        try:
            shops = data['shops']
        except KeyError as e:
            print(e)
            shops = []

        if shops:
            item2 = LianlianshopItem()
            info2 = data['shops']
            # keys2 = list(info2.keys())
            # data2 = [info2.get(i) for i in keys2]
            for i2 in info2:
                item2['product_id'] = data['id']
                item2['shop_name'] = i2['name']
                item2['shop_address'] = i2['address']
                item2['phone_number'] = i2['phoneNumber']
                item2['latitude'] = i2['latitude']
                item2['longitude'] = i2['longitude']
                item2['memo'] = i2['memo']
                item2['scale'] = i2['scale']
                yield item2

        try:
            items_d = data['items']
        except KeyError as e:
            print(e)
            items_d = []
        if items_d:
            item3 = LianlianItem()
            info3 = data['items']
            for i3 in info3:
                item3['item_id'] = i3['id']
                item3['product_id'] = i3['bizProductId']
                item3['sub_title'] = i3['subTitle']
                item3['original_price'] = i3['originPrice']
                item3['sale_price'] = i3['salePrice']
                item3['sold_out'] = i3['isSoldOut']
                yield item3
        yield item


