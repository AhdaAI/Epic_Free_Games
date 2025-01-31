from dataclasses import asdict, dataclass
from GCP import database
from datetime import datetime, timezone
from EmbedBuilder import AuthorObject, Embed, FieldObject, ImageObject
from scraper import get_epic_free_games
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
class Updated_data:
    update_on: datetime
    last_sent: datetime = datetime.now(timezone.utc)

    def to_dict(self):
        return asdict(self)


BASE_URL = "https://store.epicgames.com"
FREE_GAMES: list[dict] = []


def main():
    DB = database('webhooks')  # * Google Cloud Feature
    GCP_DATA = DB.fetch_webhook()  # * Google Cloud Feature

    if len(GCP_DATA) == 0:
        print("Nothing to update.")
        exit()

    games_list = get_epic_free_games()
    for discounted_game in games_list:
        print(f"Name : {discounted_game.get("name")}")
        if discounted_game.get("discount_price") == 0:
            FREE_GAMES.append(discounted_game)

    for data in GCP_DATA:
        sent_FREE_GAMES(data.get("url"))
        DB.update(
            Updated_data(FREE_GAMES[0].get("end_date")).to_dict(),
            data.get("id")
        )


def sent_FREE_GAMES(webhook, FREE_GAMES_data=FREE_GAMES):
    print(f"{" Sending Data ":=^40}")

    embed = Embed(
        title=FREE_GAMES_data[0]['name'],
        description=f"*End Date : {
            FREE_GAMES_data[0].get("end_date").strftime("%d %B %Y")}*",
        url=FREE_GAMES_data[0]['url'],
        color="1752220",  # ! see https://gist.github.com/thomasbnt/b6f455e2c7d743b796917fa3c205f812
        author=AuthorObject('Epic Free Games', BASE_URL),
        image=ImageObject(FREE_GAMES_data[0]['image_url']),
        fields=[
            FieldObject(
                "Details",
                f"```{FREE_GAMES_data[0]['description']}```", False
            ),
        ]
    )

    data = {
        "username": "Epic Free Games",
        "embeds": [
            embed.to_dict()
        ],
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
    main()
