from typing import Iterable

import scrapy
from scrapy.http import Request

from ..items import UitfPerformanceItem
from ..utils import clean_string


class UitfPerformanceYtdSpider(scrapy.Spider):
    name = 'uitf_performance_ytd'
    max_class_id = 46
    currencies = ['PHP', 'USD', 'JPY']

    def format_url(self, class_id: int, currency: str) -> str:
        return f"https://uitf.com.ph/top-funds.php?class_id={class_id}&currency={currency}&radio1=ytd&fromdate=&todate=&btn=FILTER"

    def clean_string(self, string: str) -> str:
        return string.strip().replace('\n', '').replace('\t', '').replace('%', '')

    def start_requests(self) -> Iterable[Request]:
        for currency in self.currencies:
            for class_id in range(1, self.max_class_id + 1):
                url = self.format_url(class_id, currency)
                self.logger.info(f"Getting requests for {url}")
                yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        item = UitfPerformanceItem()
        selectors = response.xpath('//table[@id="generated-report"]/tbody//tr')

        for selector in selectors:
            bank = selector.xpath('./td[2]/a/text()').get()
            fund_name = selector.xpath('./td[3]/a/text()').get()
            ytd = selector.xpath('./td[4]/text()').get()
            self.logger.info(f"Extracting details for {fund_name}")

            item['bank'] = clean_string(bank)
            item['fund_name'] = clean_string(fund_name)
            item['ytd'] = clean_string(ytd)
            yield item