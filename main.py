from dataclasses import dataclass, field
from playwright.sync_api import sync_playwright
from playwright_scrape import Scraper
from firestore import database
from datetime import datetime, timezone
import requests
import os
import re
import html

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
    description: str = field(default_factory="Failed to fetch game details.")


@dataclass
class webhook:
    url: str
    update_on: datetime
    last_updated: datetime = field(default_factory=datetime.now(timezone.utc))


base_url = "https://store.epicgames.com"
free_games = []
temp_data = None
current_date = datetime.now(timezone.utc)
webhooks = []
update_required = []


def main():
    with sync_playwright() as p:
        print(f"{f' Starting web scraper ':=^40}")
        scraper = Scraper(p)
        scraper.set_header({
            "User-Agent": "Chrome/131.0.0.0"
        })
        scraper.url = f"{base_url}/en-US/"
        scrape = scraper.scrape()

        query_data = scrape.query_selector_all('section')
        for data in query_data:
            a_tags = data.query_selector_all("a")

        for data in a_tags:
            name = data.query_selector("h6").text_content()
            date = data.query_selector(
                'p').text_content().replace("Free ", "")
            link = f"{base_url}{data.get_attribute('href')}"
            image_url = data.query_selector(
                "img").get_attribute('data-image').split("?")
            image = image_url[0]
            free_games.append(GameData(link, name, date, image))

        scraper.close(f"{" Browser Closed ":=^40}")

    get_games_detail()
    # for url in webhooks:
    #     sent_free_games(url)

    # for id in update_required:
    #     clean_day = free_games[0]['date'].split(' ')
    #     end_of_sale = f"{clean_day[2]} {
    #         clean_day[3]} {datetime.now().year}"
    #     parsed_date = datetime.strptime(end_of_sale, f'%b %d %Y')

    #     print(f'{f" Updating database ":=^40}')
    #     db.update({
    #         "last_sent": current_date,
    #         "update_on": parsed_date,
    #     }, id)


def get_games_detail(games=None) -> dict:
    if not games:
        games = free_games
    rawg_api_url = f"https://api.rawg.io/api/games/{
        games[0]['name'].replace(" ", "-")}?key={os.getenv("RAWG_API")}"

    result = requests.get(rawg_api_url)
    if result.status_code != 200:
        status_code = result.status_code
        print(f"{f" {status_code} ":=^40}")
        match status_code:
            case 404:
                print(f"Game not found!")
        return games
    print(f"Game found [ {games[0]['name']} ]")
    data = result.json()
    description: str = ""
    for desc in data['description'].split("."):
        desc = html.unescape(desc)
        desc = re.sub(r"<.*?>", "", desc)
        desc = desc.replace("\n", " ")
        if (len(description) + len(desc)) < 400:
            description = description + desc + "."
            continue
        break
    games[0]['description'] = description
    games[0]['released'] = data['released']
    return games


def sent_free_games(webhook, free_games_data=free_games):
    print(f"{" Sending Data ":=^40}")

    # see https://discord.com/developers/docs/resources/message#embed-object
    embed = {
        "title": free_games_data[0]['name'],
        "type": "rich",  # see https://discord.com/developers/docs/resources/message#embed-object-embed-types
        "description": f"*{free_games_data[0]['date']}*",
        "url": free_games_data[0]['link'],
        # see https://gist.github.com/thomasbnt/b6f455e2c7d743b796917fa3c205f812
        "color": "1752220",
        "author": {
            "name": 'Epic Free Games',
            'url': base_url
        },
        "thumbnail": {
            "url": free_games_data[0]['image'],
        },
        "fields": [
            {
                "name": 'Details',
                "value": f"```{free_games_data[0]['description'] if 'description' in free_games_data[0] else "Cannot find game details. Please check the store directly."}```",
                "inline": False
            },
            {
                "name": f"Upcoming Free Games [ {free_games_data[1]['name']} ]",
                "value": f"*{free_games_data[1]['date']}*",
                "inline": False
            }
        ]
    }

    data = {
        "username": "Epic Free Games",
        "embeds": [
            embed
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
    # Start of the program
    db = database('webhooks')
    webhook_url = db.read()
    print(f"{f" Found {len(webhook_url)} webhook ":=^40}")
    print(f"Checking update...")
    for webhook in webhook_url:
        for key, value in webhook.items():
            print(f'{f'ID':10} = {key}')
            update_date = value.get('update_on')
            if not update_date or update_date < current_date:
                print(f"Update require.")
                need_update = webhook(url=value.get(
                    'url'), update_on=value.get("update_on"))
                update_required.append(key)
                # webhooks.append(value.get('url'))
                webhooks.append(need_update)
                continue
            print(f"Update not needed.")

    main() if len(webhooks) > 0 else exit()
