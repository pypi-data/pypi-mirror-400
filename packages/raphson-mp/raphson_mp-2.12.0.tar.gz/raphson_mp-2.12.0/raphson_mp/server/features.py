from enum import Enum


class Feature(Enum):
    DOWNLOADER = "downloader"
    GAMES = "games"
    WEBDAV = "webdav"
    SUBSONIC = "subsonic"
    RADIO = "radio"
    SPOTIFY = "spotify"
    NEWS = "news"
    WEBAUTHN = "webauthn"


# Enable features that don't require configuration by default
FEATURES: set[Feature] = {
    Feature.DOWNLOADER,
    Feature.GAMES,
    Feature.WEBDAV,
    Feature.SUBSONIC,
    Feature.RADIO,
}
