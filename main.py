from dataclasses import asdict
from datetime import datetime, timezone
from GCP import Data, GCP_Credentials, database
from EmbedBuilder import AuthorObject, Embed, FieldObject, ImageObject
from scraper import get_epic_free_games
import requests
import os


BASE_URL = "https://store.epicgames.com"
FREE_GAMES: list[dict] = []
GCP_DATA = []


def main():
    DB = database('webhooks')  # * Google Cloud Feature
    DATAS = DB.read()
    for data in DATAS:
        for key, value in data.items():
            update = value.get("updateAt")
            if not update or update <= datetime.now(timezone.utc):
                GCP_DATA.append(data)

    if len(GCP_DATA) == 0:
        print("Nothing to update.")
        exit()

    games_list = get_epic_free_games()
    for discounted_game in games_list:
        print(f"Name : {discounted_game.get("name")}")
        if discounted_game.get("discount_price") == 0:
            FREE_GAMES.append(discounted_game)

    for data in GCP_DATA:
        for key, value in data.items():
            sent_webhook(value.get("url"), FREE_GAMES)
            DB.update(
                asdict(Data(value.get("url"), FREE_GAMES[0].get("end_date"))),
                key
            )


def sent_webhook(url, data) -> bool:
    webhook_username = "Epic Free Games"

    embeds_list = []
    for dat in data:
        embed = embed = Embed(
            title=dat['name'],
            description=f"""*End Date : {dat.get("end_date").strftime("%d %B %Y")}*
            **Original Price : {dat.get("original_price")}**""",
            url=dat['url'],
            color="1752220",  # ! see https://gist.github.com/thomasbnt/b6f455e2c7d743b796917fa3c205f812
            author=AuthorObject('Epic Free Games', BASE_URL),
            image=ImageObject(dat['image_url']),
            fields=[
                FieldObject(
                    "Details",
                    f"```{dat['description']}```",
                    False
                ),
            ]
        )

        embeds_list.append(embed.to_dict())

    data = {
        "username": webhook_username,
        "embeds": embeds_list,
    }

    result = requests.post(url, json=data)

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
        return False
    else:
        print(f"{f" code {result.status_code}. ":=^40}")
        print(f"Payload delivered successfully.")
        return True


# Load variable on .env file
def load_env():
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


if __name__ == "__main__":
    load_env()
    if not GCP_Credentials():
        exit(1)
    main()
