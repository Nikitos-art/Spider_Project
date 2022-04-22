# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import Compose, MapCompose, TakeFirst
from w3lib.html import remove_tags


def convert_price(value):
    value = value.replace('\xa0', '')
    try:
        value = int(value)
    except:
        return value
    return value


class CastaramaItem(scrapy.Item):
    name = scrapy.Field(input_processor=MapCompose(remove_tags), output_processor=TakeFirst())
    price = scrapy.Field(input_processor=MapCompose(convert_price), output_processor=TakeFirst())
    photos = scrapy.Field()
    url = scrapy.Field(output_processor=TakeFirst())
    #_id = scrapy.Field()
    pass
