from dataclasses import asdict, dataclass
import requests
import html
import re
import os


@dataclass
class ErrorStatus:
    status_code: int
    message: str

    def to_dict(self):
        return asdict(self)


@dataclass
class Data:
    status_code: int
    data: dict

    def to_dict(self):
        return asdict(self)


@dataclass
class ReturnData:
    name: str
    description: str

    def to_dict(self):
        return asdict(self)


def GameSearch(name: str) -> dict:
    RAWG_API = os.getenv("RAWG_API")

    if name.find(":") != -1:
        name = name.split(":")[0]
    name = name.replace(" ", "-")
    url = f"https://api.rawg.io/api/games/{name}?key={RAWG_API}"

    result = requests.get(url)
    if result.status_code != 200:
        print(f"Status Code {result.status_code}")
        print(result.json())
        return ErrorStatus(result.status_code, result.json())

    return Data(result.status_code, result.json()).to_dict()


def get_games_detail(game) -> dict:
    print(f"Searching `{game['name']}` ...")
    data = GameSearch(game['name'])

    description: str = ""
    for desc in data['data']['description'].split("."):
        desc = html.unescape(desc)
        desc = re.sub(r"<.*?>", "", desc)
        desc = desc.replace("\n", " ")
        if len(description) + len(desc) < 400:
            description = description + desc + "."
            continue
        break

    game['description'] = description if len(
        description) >= 200 else game['description']
    return game
