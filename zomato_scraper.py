import json
import logging
import os
import re
import time

from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class ZomatoScraper:
    def __init__(self, base_url="https://www.zomato.com", city="bangalore", output_file="captured_urls.json"):
        self.base_url = base_url.rstrip('/')
        self.city = city.lower()
        self.city_url = f"{self.base_url}/{self.city}"
        self.driver = None
        self.output_file = output_file
        self.next_id = 1

        # Set up a logger for debugging/info
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)

    def init_driver(self):
        """
        Initializes the Chrome WebDriver with the desired options.
        The browser will be visible.
        """
        options = Options()
        options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(options=options)

        # Set an implicit wait time so elements can load.
        self.driver.implicitly_wait(10)
        self.logger.info("WebDriver initialized.")

    def load_page(self, url, timeout=10):
        self.logger.info(f"Loading page: {url}")
        self.driver.get(url)
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "a"))
            )
        except Exception as e:
            self.logger.error(f"Error waiting for page load: {e}")

    def get_all_links(self):
        self.logger.debug("Extracting links from the page.")
        elements = self.driver.find_elements(By.XPATH, "//a[@href]")
        hrefs = []
        for el in elements:
            try:
                href = el.get_attribute("href")
                if href:
                    hrefs.append(href)
            except StaleElementReferenceException:
                self.logger.debug("Encountered a stale element. Skipping this element.")
        self.logger.debug(f"Extracted {len(hrefs)} links.")
        return hrefs

    def filter_restaurant_urls(self, urls):
        """
        Filters the provided URLs to extract only restaurant URLs.
        The expected pattern is:
          https://www.zomato.com/bangalore/<restaurant-name>/order...
        and the captured URL is trimmed to the base restaurant URL (i.e. without the /order part).
        :param urls: List of URL strings.
        :return: Set of unique restaurant URLs.
        """
        self.logger.debug("Filtering for restaurant URLs.")
        # This regex captures URLs like:
        # https://www.zomato.com/bangalore/some-restaurant/order...
        pattern = re.compile(
            rf'^(https://www\.zomato\.com/{self.city}/[^/]+)(/order.*)$',
            re.IGNORECASE
        )
        restaurant_urls = set()
        for url in urls:
            match = pattern.search(url)
            if match:
                restaurant_url = match.group(1)
                restaurant_urls.add(restaurant_url)
                self.logger.debug(f"Matched restaurant URL: {restaurant_url}")
        self.logger.debug(f"Total restaurant URLs after filtering: {len(restaurant_urls)}")
        return restaurant_urls

    def append_to_json_file(self, new_items):
        """
        Appends new items (a list of dictionaries) to the JSON file.
        If the file exists, the new items are appended to the stored list.
        Otherwise, a new file is created.
        :param new_items: List of dictionaries (each representing a captured URL with an id).
        """
        # Load existing data if the file exists.
        if os.path.exists(self.output_file):
            try:
                with open(self.output_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception as e:
                self.logger.error(f"Error reading {self.output_file}: {e}")
                data = []
        else:
            data = []

        data.extend(new_items)

        try:
            with open(self.output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            self.logger.info(f"Appended {len(new_items)} new items to {self.output_file}. Total items: {len(data)}")
        except Exception as e:
            self.logger.error(f"Error writing to {self.output_file}: {e}")

    def monitor_for_new_urls(self, poll_interval):
        """
        Continuously monitors the currently loaded page for new restaurant URLs.
        Prints any new URL as soon as it is found.
        :param poll_interval: Number of seconds between each check.
        """
        self.logger.info("Starting real-time URL monitoring.")
        captured_urls = set()

        try:
            while True:
                # Get all links from the current page.
                all_links = self.get_all_links()
                # Filter them to the restaurant URLs.
                filtered_urls = self.filter_restaurant_urls(all_links)
                # Determine which URLs are new.
                new_urls = filtered_urls - captured_urls

                if new_urls:
                    new_items = []
                    for url in new_urls:
                        # Assign a unique id to each new URL.
                        item = {"id": self.next_id, "url": url}
                        self.next_id += 1
                        print(f"New URL captured (ID {item['id']}): {url}")
                        new_items.append(item)
                    # Append the new items to the JSON file.
                    self.append_to_json_file(new_items)
                    captured_urls.update(new_urls)

                current_page_url = self.driver.current_url
                self.logger.debug(f"Current page: {current_page_url}")

                time.sleep(poll_interval)
        except KeyboardInterrupt:
            self.logger.info("Real-time monitoring stopped by user.")


def main():
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO
    )
    target_page = "https://www.zomato.com/bangalore/restaurants"
    scraper = ZomatoScraper(output_file="captured_urls.json")
    scraper.init_driver()
    scraper.load_page(target_page)
    scraper.monitor_for_new_urls(poll_interval=1)


if __name__ == "__main__":
    main()
