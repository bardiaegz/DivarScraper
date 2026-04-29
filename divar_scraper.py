import time
import argparse
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
)


class DivarScraper:
    CARD_CLASS = "kt-post-card__action"
    LOAD_MORE_SELECTOR = (
        "#post-list-container-id > div.post-list__bottom-container-cac2f "
        "> div > button"
    )

    
    def __init__(self, url, max_ads=100, max_scrolls=60, max_pages=3,
                 scroll_pause=3, click_pause=2, output_file="divar_ads.csv"):
        """
        Args:
            url (str): Divar search results URL to scrape.
            max_ads (int): Stop after collecting this many unique ads.
            max_scrolls (int): Max consecutive scrolls in the page.
            max_pages (int): Max number of "load more" pages to traverse.
            scroll_pause (float): Seconds to wait after each scroll.
            click_pause (float): Seconds to wait after clicking "load more".
            output_file (str): CSV file path for results.
        """
        self.url = url
        self.max_ads = max_ads
        self.max_scrolls = max_scrolls
        self.max_pages = max_pages
        self.scroll_pause = scroll_pause
        self.click_pause = click_pause
        self.output_file = output_file

        self.ads = {}
        self.page = 1
        self.driver = None

    def _start_driver(self):
        self.driver = webdriver.Chrome()
        self.driver.get(self.url)

    def _stop_driver(self):
        if self.driver is not None:
            self.driver.quit()
            self.driver = None

    def _fetch_partial_ads(self):
        cards = self.driver.find_elements(By.CLASS_NAME, self.CARD_CLASS)
        for card in cards:
            if len(self.ads) >= self.max_ads:
                break
            try:
                href = card.get_attribute("href")
                if not href or href in self.ads:
                    continue
                title = card.find_element(By.CSS_SELECTOR, "h2").text
                self.ads[href] = title
                print(f"AD #{len(self.ads)} ADDED!")
            except (NoSuchElementException, StaleElementReferenceException):
                print("ERROR ON ADDING POST TO THE DICT")

    def _click_load_more(self):
        """Click the 'آگهی‌های بیشتر' button. Returns True if clicked, False if absent."""
        try:
            btn = self.driver.find_element(By.CSS_SELECTOR, self.LOAD_MORE_SELECTOR)
            btn.click()
            print(f"PAGE {self.page} DONE. {self.max_pages - self.page} pages remain.")
            self.page += 1
            time.sleep(self.click_pause)
            return True
        except NoSuchElementException:
            return False

    def _save_results(self):
        df = pd.DataFrame(self.ads.items(), columns=["URL", "Title"])
        df.to_csv(self.output_file, index=False)
        return df

    def scrape(self):
        """Run the full scrape and return results as a pandas DataFrame."""
        self._start_driver()
        try:
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            scroll_attempt = 0
            self._fetch_partial_ads()

            while (
                scroll_attempt < self.max_scrolls
                and len(self.ads) < self.max_ads
                and self.page <= self.max_pages
            ):
                self.driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);"
                )
                time.sleep(self.scroll_pause)
                new_height = self.driver.execute_script(
                    "return document.body.scrollHeight"
                )
                self._fetch_partial_ads()

                if new_height == last_height:
                    if not self._click_load_more():
                        break
                    scroll_attempt = 0 # cause now we are on the new page. reset the scroll attempt counter.
                else:
                    scroll_attempt += 1 # we have scrolled but still didn't reach 'آگهی‌های بیشتر' button. so increase the scroll attempt counter.

                last_height = new_height

            df = self._save_results()
            print(
                f"Successfully scraped {len(self.ads)} ads from Divar.\n"
                f"Saved to {self.output_file}"
            )
            return df
        finally:
            self._stop_driver()


def main():
    parser = argparse.ArgumentParser(description="Scrape ads from a Divar search URL.")
    parser.add_argument(
        "url",
        nargs="?",
        default="https://divar.ir/s/tehran",
        help="Divar URL (default: tehran).",
    )
    parser.add_argument("--max-ads", type=int, default=100, help="Max ads to collect.")
    parser.add_argument("--max-scrolls", type=int, default=60,
                        help="Max consecutive scrolls in the page.")
    parser.add_argument("--max-pages", type=int, default=3,
                        help="Max pages to traverse.")
    parser.add_argument("--output", default="divar_ads.csv", help="Output CSV path.")
    args = parser.parse_args()

    scraper = DivarScraper(
        url=args.url,
        max_ads=args.max_ads,
        max_scrolls=args.max_scrolls,
        max_pages=args.max_pages,
        output_file=args.output,
    )
    scraper.scrape()


if __name__ == "__main__":
    main()
