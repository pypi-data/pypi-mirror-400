import asyncio
import base64
import logging
import os
import time
from collections.abc import AsyncIterator
from contextlib import AbstractAsyncContextManager
from enum import Enum
from pathlib import Path
from typing import TypedDict, cast

import aiohttp
from typing_extensions import override
from yarl import URL

from raphson_mp.common import httpclient, process, util
from raphson_mp.server import challenge, db, ffmpeg, ratelimit, scanner, settings
from raphson_mp.server.i18n import gettext
from raphson_mp.server.track import from_relpath, to_relpath

if settings.offline_mode:
    # Module must not be imported to ensure no data is ever downloaded in offline mode.
    raise RuntimeError("Cannot use spotify in offline mode")


log = logging.getLogger(__name__)
TOKEN_EXPIRE_EARLY_TIME = 300
ARTIST_FIELDS = "name,images"
ALBUM_FIELDS = f"name,release_date,artists({ARTIST_FIELDS}),images"
TRACK_FIELDS = f"type,id,name,album({ALBUM_FIELDS}),artists({ARTIST_FIELDS}),is_local,is_playable"
PLAYLIST_LIST_FIELDS = f"next,items(track({TRACK_FIELDS}))"


class SpotifyToken(TypedDict):
    access_token: str
    expires_in: int
    refresh_token: str


class ImageObject(TypedDict):
    url: str


class ArtistObject(TypedDict):
    name: str
    images: list[ImageObject]


class AlbumObject(TypedDict):
    name: str
    release_date: str
    artists: list[ArtistObject]
    images: list[ImageObject]


class TrackObject(TypedDict):
    id: str
    name: str
    album: AlbumObject
    artists: list[ArtistObject]
    is_local: bool
    is_playable: bool


class UserProfile(TypedDict):
    country: str
    display_name: str | None
    product: str


class SpotifyPlaylist(TypedDict):
    snapshot_id: str


class AlbumList(TypedDict):
    items: list[AlbumObject]


class ArtistList(TypedDict):
    items: list[ArtistObject]


class TrackList(TypedDict):
    items: list[TrackObject]


class SpotifySearchResult(TypedDict):
    tracks: TrackList
    artists: ArtistList
    albums: AlbumList


class SpotifyClient:
    _OAUTH_STATE_KEY: bytes = os.urandom(16)
    _playlist_cache: dict[tuple[str, str], list[TrackObject]] = {}
    _profile_cache: tuple[str, UserProfile] | None = None
    _api_id: str
    _api_secret: str
    _access_token: str | None = None
    _access_token_expiry: int = 0

    def __init__(self, api_id: str, api_secret: str):
        self._api_id = api_id
        self._api_secret = api_secret

    @property
    def auth_header(self):
        return f"Basic " + base64.b64encode((self._api_id + ":" + self._api_secret).encode()).decode()

    async def get_access_token(self) -> str:
        """
        Obtain an access token using the "Client Credentials Flow". This token can only be used for public data.
        https://developer.spotify.com/documentation/web-api/tutorials/client-credentials-flow
        """
        if self._access_token_expiry > time.time():
            assert self._access_token
            return self._access_token

        async with httpclient.session() as session:
            async with ratelimit.SPOTIFY:
                async with session.post(
                    "https://accounts.spotify.com/api/token",
                    data={
                        "grant_type": "client_credentials",
                    },
                    headers={"Authorization": self.auth_header, "Content-Type": "application/x-www-form-urlencoded"},
                ) as response:
                    json = cast(SpotifyToken, await response.json())

        access_token: str = json["access_token"]
        self._access_token = access_token
        self._access_token_expiry = int(time.time()) + json["expires_in"] - TOKEN_EXPIRE_EARLY_TIME
        return access_token

    async def _session(self) -> AbstractAsyncContextManager[aiohttp.ClientSession]:
        return httpclient.session(
            headers={
                "Authorization": "Bearer " + await self.get_access_token(),
            },
        )

    async def get_playlist(self, playlist_id: str):
        async with await self._session() as session:
            async with ratelimit.SPOTIFY:
                async with session.get(
                    f"https://api.spotify.com/v1/playlists/{util.urlencode(playlist_id)}",
                    params={"fields": "snapshot_id"},
                ) as response:
                    return cast(SpotifyPlaylist, await response.json())

    async def list_playlist(self, playlist_id: str, market: str) -> AsyncIterator[TrackObject]:
        url = f"https://api.spotify.com/v1/playlists/{util.urlencode(playlist_id)}/tracks"
        playlist = await self.get_playlist(playlist_id)

        cache_key = (playlist_id, playlist["snapshot_id"])
        if cached_tracks := self._playlist_cache.get(cache_key):
            log.debug("yielding tracks from cache")
            for track in cached_tracks:
                yield track
            return

        to_be_cached: list[TrackObject] = []
        async with await self._session() as session:
            while url:
                log.debug("making request to: %s", url)

                async with ratelimit.SPOTIFY:
                    async with session.get(url, params={"fields": PLAYLIST_LIST_FIELDS, "market": market}) as response:
                        json = await response.json()

                for item in json["items"]:
                    track = item["track"]
                    if track["type"] == "track":
                        to_be_cached.append(track)
                        yield track

                url = json["next"]

        self._playlist_cache[cache_key] = to_be_cached

    async def get_track(self, track_id: str, market: str) -> TrackObject:
        async with ratelimit.SPOTIFY:
            async with await self._session() as session:
                async with session.get(
                    f"https://api.spotify.com/v1/tracks/{util.urlencode(track_id)}",
                    params={"fields": TRACK_FIELDS, "market": market},
                ) as response:
                    return cast(TrackObject, await response.json())

    async def _search(self, query: str, search_type: str) -> SpotifySearchResult:
        log.debug("searching spotify for %s: %s", search_type, query)
        async with await self._session() as session:
            async with ratelimit.SPOTIFY:
                async with session.get(
                    "https://api.spotify.com/v1/search",
                    params={"q": query, "type": search_type, "market": "NL", "limit": 1},
                ) as response:
                    return cast(SpotifySearchResult, await response.json())

    async def search_artist(self, name: str) -> ArtistObject | None:
        result = await self._search(name, "artist")
        return result["artists"]["items"][0] if result["artists"]["items"] else None

    async def search_album(self, name: str, artist: str | None) -> AlbumObject | None:
        query = name + " " + (artist or "")
        result = await self._search(query, "album")
        return result["albums"]["items"][0] if result["albums"]["items"] else None

    async def _get_image(self, obj: ArtistObject | AlbumObject) -> bytes | None:
        images = obj["images"]
        if not images:
            return None
        image_url = images[0]["url"]

        async with httpclient.session() as session:
            async with session.get(image_url) as response:
                return await response.content.read()

    async def get_artist_image(self, name: str):
        artist = await self.search_artist(name)
        return await self._get_image(artist) if artist is not None else None

    async def get_album_image(self, name: str, artist: str | None):
        album = await self.search_album(name, artist)
        return await self._get_image(album) if album is not None else None

    def get_oauth_url(self, redirect_uri: str):
        """
        Get oauth URL that can be used for obtaining a personal access token. A personal access token is
        required for actions on non-public data. For example, listing private playlists and streaming audio.
        https://developer.spotify.com/documentation/web-api/tutorials/code-flow
        """
        return URL("https://accounts.spotify.com/authorize").with_query(
            {
                "client_id": self._api_id,
                "response_type": "code",
                "redirect_uri": redirect_uri,
                "state": challenge.generate(),
                "scope": "user-read-private streaming",
            }
        )

    async def receive_oauth_callback(self, code: str, state: str, redirect_uri: str):
        challenge.verify(state)

        async with httpclient.session() as session:
            async with ratelimit.SPOTIFY:
                async with session.post(
                    "https://accounts.spotify.com/api/token",
                    data={
                        "grant_type": "authorization_code",
                        "redirect_uri": redirect_uri,
                        "code": code,
                    },
                    headers={"Authorization": self.auth_header, "Content-Type": "application/x-www-form-urlencoded"},
                ) as response:
                    json = cast(SpotifyToken, await response.json())

        with db.MUSIC.connect() as conn:
            expire_time = int(time.time()) + json["expires_in"] - TOKEN_EXPIRE_EARLY_TIME
            conn.execute(
                "INSERT INTO spotify_token (access_token, expire_time, refresh_token) VALUES (?, ?, ?)",
                (json["access_token"], expire_time, json["refresh_token"]),
            )

    async def get_personal_access_token(self) -> str | None:
        while True:
            with db.MUSIC.connect() as conn:
                row = conn.execute(
                    "SELECT rowid, access_token, expire_time, refresh_token FROM spotify_token LIMIT 1"
                ).fetchone()

            if row is None:
                log.debug("no personal access token found")
                return None

            rowid, access_token, expire_time, refresh_token = row

            if expire_time > int(time.time()):
                log.debug("found valid token")
                # token is valid
                return access_token

            # try to refresh the token
            # https://developer.spotify.com/documentation/web-api/tutorials/refreshing-tokens
            log.debug("token needs refresh")
            async with httpclient.session() as session:
                async with ratelimit.SPOTIFY:
                    async with session.post(
                        "https://accounts.spotify.com/api/token",
                        data={
                            "grant_type": "refresh_token",
                            "refresh_token": refresh_token,
                        },
                        headers={
                            "Authorization": self.auth_header,
                            "Content-Type": "application/x-www-form-urlencoded",
                        },
                        raise_for_status=False,
                    ) as response:
                        if response.status == 200:
                            # token refresh successful
                            json = await response.json()
                            log.info("refreshed spotify token")

                            # update in database
                            with db.MUSIC.connect() as conn:
                                expire_time = int(time.time()) + json["expires_in"] - TOKEN_EXPIRE_EARLY_TIME
                                conn.execute(
                                    "UPDATE spotify_token SET access_token = ?, expire_time = ?",
                                    (json["access_token"], expire_time),
                                )
                            return json["access_token"]
                        else:
                            log.warning("failed to refresh access token")
                            # remove from database
                            with db.MUSIC.connect() as conn:
                                conn.execute("DELETE FROM spotify_token WHERE rowid = ?", (rowid,))

    async def download_track(self, track: TrackObject, dest: Path):
        token = await self.get_personal_access_token()
        if token is None:
            raise ValueError("no Spotify token available")
        async with ratelimit.SPOTIFY:
            # if the track cannot be downloaded, the process may hang
            # temporary fix: set a timeout
            async with asyncio.timeout(30):
                await process.run(
                    ["raphson-spotify-sync", token, track["id"], dest.as_posix()],
                    rw_mounts=[dest.parent.as_posix()],
                    allow_networking=True,
                )
        size = dest.stat().st_size
        assert size > 10_000, "downloaded file is very small, the download likely failed"
        await ffmpeg.save_metadata(dest, track_metadata(track))

    async def get_user_profile(self):
        token = await self.get_personal_access_token()
        if token is None:
            return None

        if self._profile_cache is not None and self._profile_cache[0] == token:
            return self._profile_cache[1]

        async with httpclient.session() as session:
            async with ratelimit.SPOTIFY:
                async with session.get(
                    "https://api.spotify.com/v1/me",
                    params={"fields": "country,display_name,product"},
                    headers={"Authorization": "Bearer " + token},
                ) as response:
                    profile = cast(UserProfile, await response.json())
                    self._profile_cache = (token, profile)
                    return profile


if settings.spotify_api_id is None:
    raise ValueError("--spotify-api-id must be set")

if settings.spotify_api_secret is None:
    raise ValueError("--spotify-api-secret must be set")

CLIENT = SpotifyClient(settings.spotify_api_id, settings.spotify_api_secret)


def track_metadata(track: TrackObject) -> ffmpeg.Metadata:
    """Convert spotify TrackObject to Metadata"""
    return ffmpeg.Metadata(
        duration=0,
        artists=[artist["name"] for artist in track["artists"]],
        album=track["album"]["name"],
        title=track["name"],
        year=int(track["album"]["release_date"][:4]),
        album_artist=track["album"]["artists"][0]["name"],
    )


class PlaylistSyncError(Enum):
    DUPLICATE = "duplicate"
    UNAVAILABLE = "unavailable"

    @override
    def __str__(self):
        if self is PlaylistSyncError.DUPLICATE:
            return gettext("Duplicate")
        elif self is PlaylistSyncError.UNAVAILABLE:
            return gettext("Unavailable")
        raise ValueError()


async def _sync_playlist(playlist_name: str, spotify_id: str, market: str):
    log.info("sync playlist: %s -> %s", spotify_id, playlist_name)
    downloads = 0
    all_tracks: set[str] = set()

    sync_errors: list[tuple[str, str, str]] = []
    duplicate_check: set[tuple[str, str]] = set()

    async for track in CLIENT.list_playlist(spotify_id, market):
        track_relpath = f"{playlist_name}/{track['id']}.ogg"

        # Add track to set before checking if it's available
        # This way, if it becomes unavailable we don't delete it locally
        all_tracks.add(track_relpath)

        # Check if track can be downloaded
        if track["is_local"] or not track["is_playable"]:
            sync_errors.append(
                (
                    playlist_name,
                    PlaylistSyncError.UNAVAILABLE.value,
                    f"{track['artists'][0]['name']} - {track['name']}",
                )
            )
            continue

        # Check for and skip duplicates
        duplicate_check_key = (track["name"], track["artists"][0]["name"])
        if duplicate_check_key in duplicate_check:
            sync_errors.append(
                (
                    playlist_name,
                    PlaylistSyncError.DUPLICATE.value,
                    f"{track['artists'][0]['name']} - {track['name']}",
                )
            )
            continue
        duplicate_check.add(duplicate_check_key)

        # Do we already have the track locally?
        track_path = from_relpath(track_relpath)
        if track_path.exists():
            continue

        downloads += 1
        if downloads > 50:
            log.info("stopped after downloading 50 tracks, we will continue the next maintenance cycle")
            return

        log.debug("downloading: %s", track_relpath)
        await CLIENT.download_track(track, track_path)
        await scanner.scan_track(None, track_path)
        log.info("downloaded: %s", track_relpath)
        await asyncio.sleep(30)

    # Store sync errors in database
    with db.MUSIC.connect() as conn:
        conn.execute("DELETE FROM playlist_sync_errors WHERE playlist = ?", (playlist_name,))
        conn.executemany("INSERT INTO playlist_sync_errors VALUES (?, ?, ?)", sync_errors)

    local_paths = list(from_relpath(playlist_name).iterdir())

    if len(local_paths) > len(all_tracks) * 2:
        log.warning("playlist %s suspiciously more than halved in size, refusing to delete any tracks", playlist_name)
        return

    for track_path in local_paths:
        relpath = to_relpath(track_path)
        if relpath not in all_tracks:
            log.info("delete: %s", relpath)
            track_path.unlink()
            await scanner.scan_track(None, track_path)


async def sync():
    log.debug("starting Spotify sync")
    with db.MUSIC.connect() as conn:
        playlists = conn.execute("SELECT name, sync_ref FROM playlist WHERE sync_type = 'spotify'").fetchall()

    if len(playlists) == 0:
        # no need to look up profile if we don't have anything to sync
        return

    log.debug("look up user info")
    profile = await CLIENT.get_user_profile()
    if profile is None:
        log.warning("not authenticated with oauth, cannot sync playlists")
        return
    market = profile["country"]
    log.debug("market: %s", market)

    for playlist_name, spotify_id in playlists:
        await _sync_playlist(playlist_name, spotify_id, market)
