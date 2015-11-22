from scrapy.spiders import Spider
from scrapy.selector import Selector
from makemeup.items import BeautyProduct
from scrapy.http import Request
import json
import re

def remove_tags(text):
    return re.compile(r'<[^>]+>').sub('', text)

class MakeupSpider(Spider):
    name = 'makemeup'
    allowed_domains = ['sephora.com']
    start_urls = [
        'http://www.sephora.com/'
    ]

    def parse(self, response):
        extractor = Selector(response)
        # get moar links
        list_of_links = []
        link_xpath = '//script[contains(@seph-json-to-js,"skugroup")]/text()'
        links = extractor.xpath(link_xpath).extract()
        for link in links:
            link_data = json.loads(link)
            sku_list = link_data.get('sku_list',[])
            if len(sku_list) > 0:
                urls = [
                    sku.get('primary_product',{}).get('product_url',None)
                    for sku in sku_list
                ]
            for url in urls:
                if url is not None and url not in list_of_links:
                    list_of_links.append(url)
                    yield Request(response.urljoin(url),self.parse)

        link_xpath_2 = '//a[contains(@href,"/")]/@href'
        links_2 = extractor.xpath(link_xpath_2).extract()
        for link in links_2:
            if link not in list_of_links and 'http://' not in link:
                list_of_links.append(link)
                yield Request(response.urljoin(link),self.parse)

        # products
        product_xpath = '//script[@seph-json-to-js="sku"]/text()'
        products = extractor.xpath(product_xpath).extract()
        p_counter = 0

        description_xpath = '//div[@class="long-description"]'
        description = extractor.xpath(description_xpath).extract()

        for product in products:
            product_data = json.loads(product)

            item = BeautyProduct()
            primary_product = product_data.get('primary_product',{})
            item['product_name'] = primary_product.get('display_name','')
            item['product_type'] = primary_product.get('product_type','')
            item['average_rating'] = primary_product.get('rating','')
            item['variations_on'] = primary_product.get('variation_type','')
            item['sephora_url'] = primary_product.get('product_url','')
            item['sephora_product_id'] = primary_product.get('id','')
            item['brand_name'] = primary_product.get('brand_name','')

            item['ingredients'] = product_data.get('ingredients','')
            item['limited_edition'] = product_data.get('is_limited_edition','')
            item['new_offering'] = product_data.get('is_new','')
            item['sephora_exclusive'] = product_data.get('is_sephora_exclusive','')
            item['list_price'] = product_data.get('list_price','')
            item['value_price'] = product_data.get('value_price','')
            item['variation_value'] = product_data.get('variation_value','')
            item['beauty_insider_exclusive'] = product_data.get('bi_exclusivity_level','')
            item['ingredients'] = product_data.get('ingredients','')
            item['not_for_sale_in'] = product_data.get('restricted_countries','')
            item['sku_size'] = product_data.get('sku_size','')
            item['sku_number'] = product_data.get('sku_number','')
            if p_counter == 0:
                item['description'] = remove_tags(description[0])

            p_counter += 1
            yield item