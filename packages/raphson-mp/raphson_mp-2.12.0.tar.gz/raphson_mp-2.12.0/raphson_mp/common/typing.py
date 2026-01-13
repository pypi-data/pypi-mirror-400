from typing import NotRequired, TypedDict


class TrackDict(TypedDict):
    path: str
    mtime: int
    ctime: int
    duration: int
    title: NotRequired[str | None]
    album: NotRequired[str | None]
    album_artist: NotRequired[str | None]
    year: NotRequired[int | None]
    track_number: NotRequired[int | None]
    artists: NotRequired[list[str]]
    tags: NotRequired[list[str]]
    video: NotRequired[str | None]
    lyrics: NotRequired[str | None]


class AlbumDict(TypedDict):
    name: str
    artist: str | None
    track: str


class ArtistDict(TypedDict):
    name: str


class QueuedTrackDict(TypedDict):
    track: TrackDict
    manual: bool


class FilterResponseDict(TypedDict):
    tracks: list[TrackDict]


class DislikesResponseDict(TypedDict):
    tracks: list[TrackDict]


class GetCsrfResponseDict(TypedDict):
    token: str


class LoginResponseDict(TypedDict):
    token: str
    csrf: str


class SearchResponseDict(TypedDict):
    tracks: list[TrackDict]
    albums: list[AlbumDict]


class PlaylistDict(TypedDict):
    name: str
    track_count: int
    duration: NotRequired[int]  # since 2.11.0
    favorite: bool
    write: NotRequired[bool]  # deprecated in 2.11.0
    writable: NotRequired[bool]  # since 2.11.0
    synced: NotRequired[bool]  # since 2.11.0


class ChooseTrackRequestDict(TypedDict):
    require_metadata: NotRequired[bool]
    intersect_playlists: NotRequired[list[str]]
    tag_mode: NotRequired[str]
    tags: NotRequired[list[str]]
