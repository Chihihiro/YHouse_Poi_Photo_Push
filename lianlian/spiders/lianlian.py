# -*- coding: utf-8 -*-
import scrapy
import re
import datetime
import pandas as pd
from scrapy import Selector
import json
import time
from lianlian.items import CrawlLianlianItem
from lianlian.engines import choise_engine as engine
from scrapy import Selector, Request
from lianlian.iosjk import to_sql
from copy import deepcopy

class LianlianSpider(scrapy.Spider):
    name = 'lianlian'
    # allowed_domains = ['http://hotel.elong.com/92494775/']
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
        # cc = [[x.get('id') for x in i] for i in bb]
        # dd = []
        # for i in cc:
        #     for x in i:
        #         dd.append(x)
        n = 0
        for b in bb:
            for id in b:
                city_id = id['id']
                print(city_id)
                n+=1
                print(n, id['city'])
                item['city'] = id['city']
                url = 'https://api.lianlianlvyou.com/v1/wx/list?i=&t=1&pageSize=10&pageIndex=1&locationid=' + str(city_id)
                yield Request(url, callback=self.Details_page, meta={"item": deepcopy(item)})



    def Details_page(self, response):
        info = json.loads(response.body)
        df = pd.DataFrame([info]).T
        df.columns = ['json']

        count = info['data']['list']['rowCount']
        cc = int(count/10)
        item = response.meta["item"]
        url = response.url
        # print(url)
        for i in range(1, cc+1):
            url2 = url.replace('pageIndex=1', 'pageIndex='+str(i))
            print(url2)
            yield Request(url2, callback=self.next_page, meta={"item": deepcopy(item)})



    def next_page(self, response):
        info = json.loads(response.body)
        df = pd.DataFrame([info]).T
        df.columns = ['json']
        data = info['data']['list']['data']
        item = response.meta["item"]

        for stores in data:
            print(stores)
            stores_id = stores['id']

            url = 'https://api.lianlianlvyou.com/v1/wx/product2?i=&id=' + str(stores_id)

            try:
                item['id'] = stores_id
                item['title'] = stores['title']
                item['sales'] = stores['saleAmount']
                item['original_price'] = stores['originPriceStr']
                item['price'] = stores['salePriceStr']
                yield Request(url, callback=self.address_page, meta={"item": deepcopy(item)})
            except KeyError:
                df = pd.DataFrame([url]).T
                df.columns = ['url']
                to_sql('wrong_url', engine, df, type='update')


    def address_page(self, response):
        info = json.loads(response.body)
        df = pd.DataFrame([info]).T
        df.columns = ['json']
        df['id'] = info['data']['bizProduct']['id']
        to_sql('json_lianlian_page2', engine, df, type='update')
        data = info['data']['bizProduct']
        item = response.meta["item"]
        try:
            address = data['address']
            item['sold_out'] = data['isSoldOut']
            item['address'] = address
            item['title_name'] = data['name']
        except KeyError:
            item['address'] = None
            item['title_name'] = None
        yield item






