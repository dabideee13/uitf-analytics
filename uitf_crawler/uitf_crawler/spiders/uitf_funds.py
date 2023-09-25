from typing import Iterable, Any

import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.http import Request
from scrapy.selector import Selector
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from ..utils import wait_element, clean_string, clean_fund_name, clean_fund_details_key


class UitfFundSpider(CrawlSpider):
    name = 'uitf_fund'
    urls = ['https://www.uitf.com.ph/fund-matrix.php']
    class_values = ['1', '21', '42', '22', '41', '50', '5', '7', '6', '23', '45', '40', '44', '4', '2']
    currencies = ['PHP', 'USD']
    link_extractor = LinkExtractor(restrict_xpaths='//a[starts-with(@href, "daily_navpu_details.php")]')
    rules = (Rule(link_extractor, callback='parse_fund_details', follow=True),)

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
            yield scrapy.Request(url=url, callback=self.parse_fund_list)

    def parse_fund_list(self, response):
        self.logger.info(f'Starting selenium driver')
        self.driver.get(response.url)
        self.wait.until(lambda driver: driver.find_element(By.ID, 'class-id').is_displayed())

        self.logger.info(f'Selecting from dropdown menu')
        class_dropdown = self.driver.find_element(By.ID, 'class-id')
        select_class = Select(class_dropdown)

        for class_value in self.class_values:
            self.logger.info(f'Selecting from dropdown menu for class {class_value}')
            select_class.select_by_value(class_value)
            wait_element()

            for currency_value in self.currencies:
                self.logger.info(f'Selecting from dropdown menu for currency {currency_value}')
                select_currency = Select(self.driver.find_element(By.ID, 'currency'))
                select_currency.select_by_value(currency_value)
                wait_element()

                self.logger.info(f'Clicking on filter button')
                filter_button = self.driver.find_element(By.ID, 'filter-funds-button')
                filter_button.click()
                wait_element()
                self.wait.until(lambda driver: driver.find_element(By.ID, 'generated-report_info').is_displayed())

                driver_response = Selector(text=self.driver.page_source)
                selectors = driver_response.xpath('//table[@id="generated-report"]/tbody//tr')

                for selector in selectors:
                    bank = selector.xpath('./td[@class="sorting_1"]/text()').get()
                    fund_details_url = response.urljoin(selector.xpath('./td/a/@href').get())

                    try:
                        navpu_selector = selector.xpath('.//td')[-2]
                        navpu = navpu_selector.xpath('./text()').get()

                        if not navpu:
                            continue

                        self.logger.info(f'Parsing Bank: {bank} | Fund details url: {fund_details_url}')
                        yield scrapy.Request(
                            url=fund_details_url, 
                            callback=self.parse_fund_details, 
                            meta={'bank': bank, 'navpu': navpu}
                        )
                    
                    except IndexError:
                        self.logger.info(f'Skipping {fund_details_url}')

    def parse_fund_details(self, response):
        fund_name = response.xpath('//section[@class="page-content"]//h2/text()').get()
        classification = response.xpath('//h6[@id="tpg"]/text()').get()
        selectors = response.xpath('//table[@class="tbl-50=50"]/tbody//tr')

        fund_details = {
            clean_fund_details_key(selector.xpath('./td[1]/text()').get()): selector.xpath('./td[2]/text()').get()
            for selector in selectors
        }
        fund_details['fund_name'] = clean_fund_name(fund_name)
        fund_details['classification'] = clean_string(classification)
        fund_details['navpu'] = clean_string(response.meta['navpu'])
        fund_details['bank'] = clean_string(response.meta['bank'])
        fund_details['url'] = response.url
        yield fund_details

    def closed(self, reason: str) -> None:
        self.driver.quit()