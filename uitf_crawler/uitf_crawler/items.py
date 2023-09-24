import scrapy


class UitfPerformanceItem(scrapy.Item):
    bank = scrapy.Field()
    fund_name = scrapy.Field()
    ytd = scrapy.Field()


class UitfFundItem(scrapy.Item):
    bank = scrapy.Field()
    fund_name = scrapy.Field()
    classification = scrapy.Field()
    currency = scrapy.Field()
    min_initial_participation = scrapy.Field()
    min_additional_participation = scrapy.Field()
    min_holding_period = scrapy.Field()
    inception_date = scrapy.Field()
    min_maintaining_balance = scrapy.Field()
    settlement_date = scrapy.Field()
    trust_fee_structure = scrapy.Field()
    early_redemption_fee = scrapy.Field()
    benchmark = scrapy.Field()