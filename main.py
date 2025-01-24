from dataclasses import asdict, dataclass, field
from playwright.sync_api import sync_playwright
from GameDetail import get_games_detail
from playwright_scrape import Scraper
from GCP import database
from datetime import datetime, timezone
from EmbedBuilder import AuthorObject, Embed, FieldObject, ImageObject
import requests
import os

# Load variable on .env file
if os.path.exists(".env"):
    print(f"{"_"*40}\n")
    print(f"{" Loading Environment Variable ":=^40}")
    with open(".env", 'r') as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith("#"):
                key, value = line.split("=")
                os.environ[key] = value.strip()
                print(f"{key}")
    print(f"{" Loaded Environment Variable ":=^40}")
    print(f"{"_"*40}\n")


@dataclass
class GameData:
    url: str
    name: str
    date: str
    image: str
    description: str = field(
        default_factory=lambda: f"Failed to fetch game details.\nPlease check the store directly.")


@dataclass
class Updated_data:
    update_on: datetime
    last_sent: datetime = datetime.now(timezone.utc)

    def to_dict(self):
        return asdict(self)


BASE_URL = "https://store.epicgames.com"
FREE_GAMES: list[GameData] = []


def main():
    with sync_playwright() as p:
        print(f"{f' Starting web scraper ':=^40}")
        scraper = Scraper(p)
        scraper.set_header({
            "User-Agent": "Chrome/131.0.0.0"
        })
        scraper.url = f"{BASE_URL}/en-US/"
        scrape = scraper.scrape()

        query_data = scrape.query_selector_all('section')
        for data in query_data:
            a_tags = data.query_selector_all("a")

        for data in a_tags:
            name = data.query_selector("h6").text_content()
            date = data.query_selector('p').text_content().replace("Free ", "")
            link = f"{BASE_URL}{data.get_attribute('href')}"
            image_url = data.query_selector(
                "img").get_attribute('data-image').split("?")
            image = image_url[0]
            FREE_GAMES.append(asdict(GameData(link, name, date, image)))

        scraper.close(f"{" Browser Closed ":=^40}")

    FREE_GAMES[0] = get_games_detail(FREE_GAMES[0])


def sent_FREE_GAMES(webhook, FREE_GAMES_data=FREE_GAMES):
    print(f"{" Sending Data ":=^40}")

    embed = Embed(
        title=FREE_GAMES_data[0]['name'],
        description=f"*{FREE_GAMES_data[0]['date']}*",
        url=FREE_GAMES_data[0]['url'],
        color="1752220",  # ! see https://gist.github.com/thomasbnt/b6f455e2c7d743b796917fa3c205f812
        author=AuthorObject('Epic Free Games', BASE_URL),
        image=ImageObject(FREE_GAMES_data[0]['image']),
        fields=[
            FieldObject(
                "Details",
                f"```{FREE_GAMES_data[0]['description']}```", False
            ),
            FieldObject(
                f"Upcoming Free Games [ {FREE_GAMES_data[1]['name']} ]",
                f"*{FREE_GAMES_data[1]['date']}*",
                False
            )
        ]
    )

    data = {
        "username": "Epic Free Games",
        "embeds": [
            embed.to_dict()
        ]
    }

    result = requests.post(webhook, json=data)

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
    else:
        print(f"Payload delivered successfully.")
        print(f"{f" code {result.status_code}. ":=^40}")


if __name__ == "__main__":
    DB = database('webhooks')  # * Google Cloud Feature
    GCP_DATA = DB.fetch_webhook()  # * Google Cloud Feature

    if len(GCP_DATA) > 0:  # ! Main program
        main()
    else:
        print(f"{" Up-to-date ":=^40}")
        exit()

    for webhook_detail in GCP_DATA:  # * Google Cloud Feature & Discord Webhook
        sent_FREE_GAMES(webhook_detail.get('url'))
        # * Cleaned data from Epic Store
        clean_day = FREE_GAMES[0]['date'].split(' ')
        parsed_date = datetime.strptime(
            f"{clean_day[2]} {clean_day[3]} {datetime.now().year}",
            f'%b %d %Y'
        )
        DB.update(
            Updated_data(parsed_date).to_dict(),
            webhook_detail.get('id')
        )
