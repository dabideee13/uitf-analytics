from typing import Iterable, Any

import scrapy
from scrapy.http import Request
from scrapy.selector import Selector
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from ..items import UitfFundItem
from ..utils import wait_element, clean_string


class UitfFundSpider(scrapy.Spider):
    name = 'uitf_fund'
    urls = ['https://www.uitf.com.ph/fund-matrix.php']
    class_values = ['1', '21', '42', '22', '41', '50', '5', '7', '6', '23', '45', '40', '44', '4', '2']
    currencies = ['PHP', 'USD', 'JPY']

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--ignore-certificate-errors')

        self.driver = webdriver.Chrome(
            service=Service(executable_path=ChromeDriverManager().install()),
            options=chrome_options
        )

        self.wait = WebDriverWait(self.driver, 10)

    def start_requests(self) -> Iterable[Request]:
        for url in self.urls:
            self.logger.info(f"Getting requests for {url}")
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        item = UitfFundItem()
        self.driver.get(response.url)
        self.wait.until(lambda driver: driver.find_element(By.ID, 'class-id').is_displayed())

        class_dropdown = self.driver.find_element(By.ID, 'class-id')
        select_class = Select(class_dropdown)

        for class_value in self.class_values:
            select_class.select_by_value(class_value)
            wait_element()

            for currency_value in self.currencies:
                select_currency = Select(self.driver.find_element(By.ID, 'currency'))
                select_currency.select_by_value(currency_value)
                wait_element()

                filter_button = self.driver.find_element(By.ID, 'filter-funds-button')
                filter_button.click()
                wait_element()
                self.wait.until(lambda driver: driver.find_element(By.ID, 'generated-report_info').is_displayed())

                driver_response = Selector(text=self.driver.page_source)
                selectors = driver_response.xpath('//table[@id="generated-report"]/tbody//tr')

                for selector in selectors:
                    bank = selector.xpath('./td[1]/text()').get()
                    fund_name = selector.xpath('./td[2]/text()').get()
                    classification = selector.xpath('./td[3]/text()').get()
                    inception_date = selector.xpath('./td[4]/text()').get()
                    risk_classification = selector.xpath('./td[5]/text()').get()
                    currency = selector.xpath('./td[6]/text()').get()
                    min_initial_participation = selector.xpath('./td[7]/text()').get()
                    min_additional_participation = selector.xpath('./td[9]/text()').get()
                    min_maintaining_balance = selector.xpath('./td[11]/text()').get()
                    min_holding_period = selector.xpath('./td[13]/text()').get()
                    settlement_date = selector.xpath('./td[15]/text()').get()
                    trust_fee_structure = selector.xpath('./td[16]/text()').get()
                    early_redemption_fee = selector.xpath('./td[17]/text()').get()
                    navpu = selector.xpath('./td[20]/text()').get()
                    self.logger.info(f"Extracting details for {fund_name}")

                    item['bank'] = clean_string(bank)
                    item['fund_name'] = clean_string(fund_name)
                    item['classification'] = clean_string(classification)
                    item['inception_date'] = clean_string(inception_date)
                    item['risk_classification'] = clean_string(risk_classification)
                    item['currency'] = clean_string(currency)
                    item['min_initial_participation'] = clean_string(min_initial_participation)
                    item['min_additional_participation'] = clean_string(min_additional_participation)
                    item['min_maintaining_balance'] = clean_string(min_maintaining_balance)
                    item['min_holding_period'] = clean_string(min_holding_period)
                    item['settlement_date'] = clean_string(settlement_date)
                    item['trust_fee_structure'] = clean_string(trust_fee_structure)
                    item['early_redemption_fee'] = clean_string(early_redemption_fee)
                    item['navpu'] = clean_string(navpu)
                    yield item

    def closed(self, reason: str) -> None:
        self.driver.quit()