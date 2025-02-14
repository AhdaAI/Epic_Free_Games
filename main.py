from dataclasses import asdict, dataclass
from GCP import Data, GCP_Credentials, database
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
        sent_webhook(data.get("url"), FREE_GAMES[0])
        DB.update(
            asdict(Data(data.get("url"), FREE_GAMES[0].get("end_date"))),
            data.get("id")
        )


def sent_webhook(url, data) -> bool:
    webhook_username = "Epic Free Games"

    embed = embed = Embed(
        title=data['name'],
        description=f"*End Date : {
            data.get("end_date").strftime("%d %B %Y")}*",
        url=data['url'],
        color="1752220",  # ! see https://gist.github.com/thomasbnt/b6f455e2c7d743b796917fa3c205f812
        author=AuthorObject('Epic Free Games', BASE_URL),
        image=ImageObject(data['image_url']),
        fields=[
            FieldObject(
                "Details",
                f"```{data['description']}```", False
            ),
        ]
    )

    data = {
        "username": webhook_username,
        "embeds": [
            embed.to_dict()
        ],
    }

    result = requests.post(url, json=data)

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
        return False
    else:
        print(f"Payload delivered successfully.")
        print(f"{f" code {result.status_code}. ":=^40}")
        return True


if __name__ == "__main__":
    if not GCP_Credentials():
        exit(1)
    main()
