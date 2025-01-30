from playwright.sync_api import Playwright
import requests


def log(func):
    def wrapper(*args, **kwargs):
        print(f"{"Running":20} = {func.__name__}")
        result = func(*args, **kwargs)
        print(f"{f"Done":20} = {func.__name__}")
        return result
    return wrapper


class Scraper:
    def __init__(self, playwright: Playwright):
        self._playwright = playwright
        self._browser = playwright.chromium.launch()
        self._context = None
        self._url = None

    def close(self, text: str = None):
        self._browser.close()
        if text:
            print(text)

    @property
    def url(self):
        print(f"{"URL":20} = {self._url}")
        return self._url

    @url.setter
    def url(self, url: str):
        self._url = url
        return self.url

    @property
    def header(self):
        return self._browser.contexts

    def set_header(self, extra_header):
        context = self._browser.new_context()
        context.set_extra_http_headers(extra_header)
        self._context = context
        return self._browser.contexts

    @log
    def scrape(self, url: str = None, selector: str = None):
        if self._context is None:
            self._context = self._browser

        if not url:
            url = self._url

        print(f"{"Scraping":20} = {url}")

        page = self._context.new_page()
        page.set_default_timeout(60000)

        page.goto(url)
        print(f"{"page.title()":20} = {page.title()}")

        if selector:
            print(f"{"Waiting for selector":20} = {selector}")
            page.wait_for_selector(selector)

        return page

    def get_epic_store_data(self, game_name: str):
        if game_name.find(":") > -1:
            game_name = game_name.replace(":", "")

        game_name = game_name.lower()
        game_name = game_name.replace(" ", "-")
        epic_api_url = f"https://store-content-ipv4.ak.epicgames.com/api/en-US/content/products/{
            game_name}"

        data = requests.get(epic_api_url)
        json_data = data.json()
        if json_data.get("error"):
            print(f"Failed to get details.")
            print(f"{json_data}")
            return None

        print("Details found.")
        return json_data
