from scrapy.spider import BaseSpider
from scrapy.selector import Selector
from makemeup.items import MakemeupItem
from scrapy.http import Request

class MakeupSpider(BaseSpider):
    name = "makemeup"
    allowed_domains = ["sephora.com"]
    start_urls = ["http://sephora.com/"]

    def parse(self, response):
        extractor = Selector(response)
        products = extractor.select('//*[@id="main"]/div[7]/script/text()').extract()
        for product in products:
            item = MakemeupItem()
            item["title"] = product
            yield item

# required tag:
# <script type="text/json" data-entity="Sephora.Sku" seph-json-to-js="sku">
# X Path:
# //script[@data-entity="Sephora.Sku"]/text()


