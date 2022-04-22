import scrapy
from scrapy.http import HtmlResponse
from avitoparser.items import AvitoparserItem
from scrapy.loader import ItemLoader

from leroymerlin.leroymerlin.items import CastaramaItem


class CastaramaSpider(scrapy.Spider):
    name = 'castarama'
    allowed_domains = ['www.castorama.ru']

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.start_urls = [f"https://www.castorama.ru/{kwargs.get('query')}"]

    def parse(self, response: HtmlResponse):
        links = response.xpath("//a[@class='product-card__img-link']")
        for link in links:
            yield response.follow(link, callback=self.parse_ads)

    def parse_ads(self, response: HtmlResponse):
        loader = ItemLoader(item=CastaramaItem(), response=response)
        loader.add_xpath('name', "//title/text()")
        loader.add_xpath('price', "//span[@class='price']/span/span[1]/text()")
        loader.add_xpath('photos', "//img/@data-src")
        loader.add_value('url', response.url)
        yield loader.load_item()
