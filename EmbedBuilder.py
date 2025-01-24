from dataclasses import asdict, dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class EmbedType:
    RICH: str = "rich"
    IMAGE: str = "image"
    VIDEO: str = "video"
    GIFV: str = "gifv"  # * animated gif image embed rendered as a video embed
    ARTICLE: str = "article"
    LINK: str = "link"
    # ! see https://discord.com/developers/docs/resources/message#embed-fields-by-embed-type-poll-result-embed-fields
    POLL_RESULT: str = "poll_result"


@dataclass
class FooterObject:
    text: str = None
    icon_url: str = None
    proxy_icon_url: str = None


@dataclass
class ImageObject:
    url: str
    proxy_url: str = None
    height: int = None
    width: int = None


@dataclass
class ThumbnailObject:
    url: str
    proxy_url: str = None
    height: int = None
    width: int = None


@dataclass
class VideoObject:
    url: str
    proxy_url: str = None
    height: int = None
    width: int = None


@dataclass
class ProviderObject:
    name: str
    url: str


@dataclass
class AuthorObject:
    name: str
    url: str = None
    icon_url: str = None
    proxy_icon_url: str = None


@dataclass
class FieldObject:
    name: str
    value: str
    inline: bool = True


@dataclass
class Embed:
    title: str
    description: str = None
    url: str = None
    timestamp: datetime = None
    color: str = None  # ! see https://gist.github.com/thomasbnt/b6f455e2c7d743b796917fa3c205f812
    footer: FooterObject = None
    image: ImageObject = None
    thumbnail: ThumbnailObject = None
    video: VideoObject = None
    provider: ProviderObject = None
    author: AuthorObject = None
    fields: list[FieldObject] = None
    type: EmbedType = EmbedType.RICH

    def to_dict(self):
        return asdict(self)
