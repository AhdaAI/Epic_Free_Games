from dataclasses import asdict, dataclass
from typing import List
import requests
from datetime import datetime
from dateutil import parser

URL = "https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions?locale=en-US&country=ID&allowCountries=ID"


@dataclass
class game_data:
    name: str
    description: str
    url_slug: str
    url: str
    image_url: str
    discount_price: int
    original_price: int
    start_date: datetime = None
    end_date: datetime = None
    active_promotion: bool = False


def get_epic_free_games() -> List[game_data]:
    games = []

    data = requests.get(URL)
    data = data.json()
    for game in data['data']['Catalog']['searchStore']['elements']:
        rules = game['price']['lineOffers'][0]['appliedRules']
        if len(rules) == 0:
            continue

        slug = game.get("productSlug")
        if not slug: # * Check for null
            slug = game.get("offerMappings")[0].get("pageSlug")

        game_url = f"https://store.epicgames.com/en-US/p/{slug}"
        data_game = game_data(
            name=game.get("title"),
            description=game.get("description"),
            url_slug=slug,
            url=game_url,
            image_url=game.get("keyImages")[0].get("url"),
            discount_price=game['price']['totalPrice']['discountPrice'],
            original_price=game['price']['totalPrice']['fmtPrice']['originalPrice']
        )
        data_game.end_date = parser.isoparse(rules[0].get('endDate'))

        games.append(asdict(data_game))

    print(f"Found {len(games)} discounted games.")
    return games
