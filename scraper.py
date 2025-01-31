from dataclasses import asdict, dataclass
from typing import List
import requests
from datetime import datetime
from dateutil import parser


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


def get_epic_free_games() -> List[dict]:
    url = "https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions?locale=en-US&country=ID&allowCountries=ID"

    games = []

    data = requests.get(url)
    data = data.json()
    for game in data['data']['Catalog']['searchStore']['elements']:
        promotions = game.get('promotions')
        if not promotions:
            continue

        slug = game.get("urlSlug")
        game_url = f"https://store.epicgames.com/en-US/p/{slug}"
        data_game = game_data(
            name=game.get("title"),
            description=game.get("description"),
            url_slug=slug,
            url=game_url,
            image_url=game.get("keyImages")[0].get("url"),
            discount_price=game['price']['totalPrice']['discountPrice'],
            original_price=game['price']['totalPrice']['originalPrice']
        )
        promotional_offer = promotions.get("promotionalOffers")[
            0] if len(promotions.get("promotionalOffers")) > 0 else []
        upcoming_promotional_offer = promotions.get(
            'upcomingPromotionalOffers')[0] if len(promotions.get("upcomingPromotionalOffers")) > 0 else []

        # * Getting dates
        if len(promotional_offer) > 0:
            data_game.end_date = parser.isoparse(
                promotional_offer.get("promotionalOffers")[0].get("endDate"))
            data_game.start_date = parser.isoparse(
                promotional_offer.get("promotionalOffers")[0].get("startDate"))
            data_game.active_promotion = True

        # * Getting dates
        if len(upcoming_promotional_offer) > 0:
            data_game.end_date = parser.isoparse(
                upcoming_promotional_offer.get(
                    "promotionalOffers")[0].get("endDate")
            )
            data_game.start_date = parser.isoparse(
                upcoming_promotional_offer.get(
                    "promotionalOffers")[0].get("startDate")
            )
            data_game.active_promotion = False

        games.append(asdict(data_game))

    print(f"Found {len(games)} discounted games.")
    return games
