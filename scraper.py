from dataclasses import dataclass
import requests
from datetime import datetime


@dataclass
class game_data:
    name: str
    description: str
    start_date: datetime
    end_date: datetime
    url_slug: str
    url: str
    active_promotion: bool


def get_epic_free_games():
    url = "https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions?locale=en-US&country=ID&allowCountries=ID"

    games = []

    data = requests.get(url)
    data = data.json()
    for game in data['Catalog']['searchStore']['elements']:
        promotions = game.get('promotions')
        if not promotions:
            continue

        slug = game.get("urlSlug")
        game_url = f"https://store.epicgames.com/en-US/p/{slug}"
        data_game = game_data(
            game.get("title"),
            game.get("description"),
            url_slug=slug,
            url=game_url
        )
        promotional_offer = promotions.get("promotionalOffers")[0]
        upcoming_promotional_offer = promotions.get(
            'upcomingPromotionalOffers')[0]

        if len(promotional_offer) > 0:
            data_game.end_date = datetime(promotional_offer.get("endDate"))
            data_game.start_date = datetime(promotional_offer.get("startDate"))
            data_game.active_promotion = True

        if len(upcoming_promotional_offer) > 0:
            data_game.end_date = datetime(promotional_offer.get("endDate"))
            data_game.start_date = datetime(promotional_offer.get("startDate"))
            data_game.active_promotion = False
