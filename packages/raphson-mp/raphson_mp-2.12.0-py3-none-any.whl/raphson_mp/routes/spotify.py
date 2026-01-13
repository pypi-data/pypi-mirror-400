import asyncio
import logging
from sqlite3 import Connection
from typing import cast

from aiohttp import web
from yarl import URL

from raphson_mp.common import metadata, util
from raphson_mp.server import auth, playlist, scanner, spotify
from raphson_mp.server.decorators import route
from raphson_mp.server.playlist import Playlist, get_playlists
from raphson_mp.server.response import template
from raphson_mp.server.track import from_relpath

_LOGGER = logging.getLogger(__name__)
# this is a random string, the playlist does not exist
SPOTIFY_PLAYLIST_PLACEHOLDER = "https://open.spotify.com/playlist/7EeOs8aXrjP67xNCnz1zLp"


def _get_redirect_uri(request: web.Request):
    return str(request.url.with_path("/spotify/callback"))


@route("")
async def root(request: web.Request, conn: Connection, user: auth.User):
    oauth_url = spotify.CLIENT.get_oauth_url(_get_redirect_uri(request))
    has_token = await spotify.CLIENT.get_personal_access_token() is not None

    all_playlists = get_playlists(conn, user)
    synced_playlists = [p for p in all_playlists if p.sync_type == "spotify"]
    can_sync_playlists = [p for p in all_playlists if p.writable and p.track_count == 0 or p.sync_type == "spotify"]

    sync_errors = [
        (playlist, spotify.PlaylistSyncError(reason), display)
        for playlist, reason, display in conn.execute(
            """
            SELECT playlist, type, display
            FROM playlist_sync_errors JOIN playlist ON playlist.name = playlist_sync_errors.playlist
            WHERE playlist.sync_type = 'spotify'
            """
        )
    ]

    return await template(
        "spotify.jinja2",
        oauth_url=oauth_url,
        has_token=has_token,
        synced_playlists=synced_playlists,
        can_sync_playlists=can_sync_playlists,
        all_playlists=all_playlists,
        spotify_playlist_placeholder=SPOTIFY_PLAYLIST_PLACEHOLDER,
        sync_errors=sync_errors,
    )


@route("/callback")
async def callback(request: web.Request, _conn: Connection, _user: auth.User):
    await spotify.CLIENT.receive_oauth_callback(
        request.query["code"], request.query["state"], _get_redirect_uri(request)
    )
    raise web.HTTPSeeOther(location="/spotify")


@route("/new", method="POST")
async def new(request: web.Request, conn: Connection, user: auth.User):
    data = await request.post()

    playlist = Playlist(conn, cast(str, data["playlist"]), user)

    if not playlist.writable:
        raise web.HTTPForbidden(reason="no write permission for this playlist")

    spotify_url = cast(str, data["spotify"])
    spotify_id = URL(spotify_url).path.removeprefix("/playlist/")

    playlist.set_sync(conn, "spotify", spotify_id)
    raise web.HTTPSeeOther("/spotify")


@route("/download", method="POST")
async def download(request: web.Request, conn: Connection, user: auth.User):
    data = await request.json()
    track_id = str(data["id"])
    dir = str(data["dir"])

    profile = await spotify.CLIENT.get_user_profile()
    if profile is None:
        raise web.HTTPServiceUnavailable()
    market = profile["country"]

    track = await spotify.CLIENT.get_track(track_id, market)
    assert not track["is_local"] and track["is_playable"]

    filename = track["artists"][0]["name"] + " - " + track["name"] + ".ogg"
    path = from_relpath(dir + "/" + filename)
    playlist.check_path_writable(conn, user, path)

    await spotify.CLIENT.download_track(track, path)
    await scanner.scan_track(user, path)
    raise web.HTTPNoContent()


def _fuzzy_match_track(
    spotify_normalized_title: str, local_track_key: tuple[str, tuple[str, ...]], spotify_track: spotify.TrackObject
) -> bool:
    (local_track_normalized_title, local_track_artists) = local_track_key
    if not util.str_match_approx(spotify_normalized_title, local_track_normalized_title):
        return False

    # Title matches, now check if artist matches (more expensive)
    for artist_a in spotify_track["artists"]:
        for artist_b in local_track_artists:
            if util.str_match_approx(artist_a["name"], artist_b):
                return True

    return False


@route("/compare")
async def compare(request: web.Request, conn: Connection, _user: auth.User):
    playlist_name = request.query["playlist"]
    spotify_playlist = request.query["spotify_playlist"]

    local_tracks: dict[tuple[str, tuple[str, ...]], tuple[str, list[str]]] = {}

    for title, artists in conn.execute(
        """
        SELECT title, GROUP_CONCAT(artist, ';') AS artists
        FROM track JOIN track_artist ON track.path = track_artist.track
        WHERE track.playlist = ?
        GROUP BY track.path
        """,
        (playlist_name,),
    ):
        local_track = (title, artists.split(";"))
        key = (metadata.normalize_title(title), tuple(local_track[1]))
        local_tracks[key] = local_track

    duplicate_check: set[tuple[str, str]] = set()  # normalized title, primary artist (lowercase)
    duplicates: list[spotify.TrackObject] = []
    both: list[tuple[tuple[str, list[str]], spotify.TrackObject]] = []
    only_spotify: list[spotify.TrackObject] = []
    only_local: list[tuple[str, list[str]]] = []

    profile = await spotify.CLIENT.get_user_profile()
    # fallback market: it is not relevant anyway if we are not streaming any music
    market = profile["country"] if profile is not None else "NL"

    i = 0
    async for spotify_track in spotify.CLIENT.list_playlist(spotify_playlist, market):
        i += 1
        if i % 10 == 0:
            await asyncio.sleep(0)  # yield to event loop

        normalized_title = metadata.normalize_title(spotify_track["name"])
        artists = [artist["name"] for artist in spotify_track["artists"]]

        # Spotify duplicates
        duplicate_check_key = normalized_title, artists[0]
        if duplicate_check_key in duplicate_check:
            duplicates.append(spotify_track)
        duplicate_check.add(duplicate_check_key)

        # Try to find fast exact match
        local_track_key = (normalized_title, tuple(artists))
        if local_track_key in local_tracks:
            local_track = local_tracks[local_track_key]
        else:
            # Cannot find exact match, look for partial match
            for local_track_key in local_tracks.keys():
                if _fuzzy_match_track(normalized_title, local_track_key, spotify_track):
                    break
            else:
                # no match found
                only_spotify.append(spotify_track)
                continue

        # match found, present in both
        both.append((local_tracks[local_track_key], spotify_track))
        del local_tracks[local_track_key]

    # any local tracks still left in the dict must have no matching spotify track
    only_local.extend(local_tracks.values())

    return await template(
        "spotify_compare.jinja2",
        duplicates=duplicates,
        both=both,
        only_local=only_local,
        only_spotify=only_spotify,
        playlist=playlist_name,
        has_token=profile is not None,
    )
