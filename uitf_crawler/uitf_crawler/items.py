import scrapy


class UitfPerformanceItem(scrapy.Item):
    bank = scrapy.Field()
    fund_name = scrapy.Field()
    ytd = scrapy.Field()