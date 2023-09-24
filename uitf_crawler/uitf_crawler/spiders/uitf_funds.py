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


class UitfFundSpider(scrapy.Spider):
    name = 'uitf_fund'
    urls = ['https://www.uitf.com.ph/fund-matrix.php']

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument('--headless')
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
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        class_value = "1"
        currency_value = "PHP"
        self.driver.get(response.url)
        self.wait.until(lambda driver: driver.find_element(By.ID, 'class-id').is_displayed())

        class_dropdown = self.driver.find_element(By.ID, 'class-id')
        select_class = Select(class_dropdown)
        select_class.select_by_value(class_value)

        select_currency = Select(self.driver.find_element(By.ID, 'currency'))
        select_currency.select_by_value(currency_value)

        filter_button = self.driver.find_element(By.ID, 'filter-funds-button')
        filter_button.click()

    def closed(self, reason: str) -> None:
        self.driver.quit()