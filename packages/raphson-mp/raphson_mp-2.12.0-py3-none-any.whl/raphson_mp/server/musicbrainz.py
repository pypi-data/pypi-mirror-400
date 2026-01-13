import logging
import re
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import cast

import aiohttp

from raphson_mp.common import httpclient
from raphson_mp.server import ratelimit, settings
from raphson_mp.server.decorators import retry

if settings.offline_mode:
    # Module must not be imported to ensure no data is ever downloaded in offline mode.
    raise RuntimeError("Cannot use musicbrainz in offline mode")


log = logging.getLogger(__name__)


# https://lucene.apache.org/core/4_3_0/queryparser/org/apache/lucene/queryparser/classic/package-summary.html#Escaping_Special_Characters
# https://github.com/alastair/python-musicbrainzngs/blob/1638c6271e0beb9560243c2123d354461ec9f842/musicbrainzngs/musicbrainz.py#L27
LUCENE_SPECIAL = re.compile(r'([+\-&|!(){}\[\]\^"~*?:\\\/])')

MUSICBRAINZ_BASE = "https://musicbrainz.org/ws/2/"


def lucene_escape(text: str) -> str:
    """Escape string for MB"""
    return re.sub(LUCENE_SPECIAL, r"\\\1", text)


@retry(log)
async def _get_release_group_cover(release_group: str) -> bytes | None:
    url = f"https://coverartarchive.org/release-group/{release_group}/front-1200"
    log.info("downloading: %s", url)
    async with httpclient.session() as session:
        async with session.get(url, allow_redirects=True, raise_for_status=False) as response:
            if response.status == 404:
                log.info("release group has no image")
                return None
            response.raise_for_status()
            return await response.content.read()


async def _search_release_group(artist: str, title: str) -> str | None:
    """
    Search for a release group id using the provided search query
    """

    @retry(log)
    async def search(session: aiohttp.ClientSession, query: str):
        async with ratelimit.MUSICBRAINZ:
            log.info("performing MB search for query: %s", query)
            async with session.get(
                "release-group",
                params={"query": query, "limit": "1", "fmt": "json"},
            ) as response:
                return await response.json()

    async with httpclient.session(MUSICBRAINZ_BASE) as session:
        for query in [
            f'artist:"{lucene_escape(artist)}" AND releasegroup:"{lucene_escape(title)}" AND (primarytype:Album OR primarytype:EP)',
            f'artist:"{lucene_escape(artist)}" AND releasegroup:"{lucene_escape(title)}"',
        ]:
            result = await search(session, query)
            groups = result["release-groups"]
            if groups:
                group = groups[0]
                log.info(
                    "Found release group: %s: %s (%s)",
                    group["id"],
                    group["title"],
                    group.get("primary-type"),
                )
                return group["id"]

        log.info("no release group found")
        return None


async def get_cover(artist: str, album: str) -> bytes | None:
    """
    Get album cover for the given artist and album
    Returns: Image bytes, or None of no album cover was found.
    """
    try:
        release_group = await _search_release_group(artist, album)
        if release_group is None:
            return None

        image_bytes = await _get_release_group_cover(release_group)
        if image_bytes is None:
            return None

        return image_bytes
    except Exception:
        log.info("error retrieving album art from musicbrainz", exc_info=True)
        return None


@dataclass
class MBMeta:
    id: str
    title: str
    album: str
    artists: list[str]
    album_artist: str
    year: int | None
    release_type: str
    packaging: str


async def get_recording_metadata(recording_id: str) -> AsyncIterator[MBMeta]:
    async with ratelimit.MUSICBRAINZ:
        async with httpclient.session(MUSICBRAINZ_BASE) as session:
            async with session.get(
                "recording/" + recording_id,
                params={"inc": "artists+releases+release-groups", "fmt": "json"},
                raise_for_status=False,
            ) as response:
                if response.status == 404:
                    log.warning("got 404 for recording %s", recording_id)
                    return
                response.raise_for_status()
                result = await response.json()

    title = result["title"]
    artists = [artist["name"] for artist in result["artist-credit"]]

    for release in result["releases"]:
        if "Compilation" in release["release-group"]["secondary-types"]:
            log.info("ignoring compilation release: %s", release["id"])
            continue

        release_type = release["release-group"]["primary-type"]

        album = release["title"]

        album_artist = release["release-group"]["artist-credit"][0]["name"]

        if "date" in release and len(release["date"]) >= 4:
            year = int(release["date"][:4])
        else:
            year = None

        packaging = release["packaging"]
        if packaging is None or packaging == "None":
            packaging = "Digital"

        yield MBMeta(
            release["id"],
            title,
            album,
            artists,
            album_artist,
            year,
            release_type,
            packaging,
        )


@dataclass
class MBArtist:
    name: str
    area: str | None
    begin_date: str | None
    wikidata: str | None


@retry(log)
async def get_artist(name: str):
    # http://musicbrainz.org/ws/2/artist?query=Green%20Day&fmt=json&limit=1
    async with httpclient.session(MUSICBRAINZ_BASE) as session:
        async with ratelimit.MUSICBRAINZ:
            async with session.get(
                "artist", params={"query": lucene_escape(name), "fmt": "json", "limit": 1}
            ) as response:
                search_json = await response.json()

        if len(search_json["artists"]) == 0:
            return None

        artist_id = search_json["artists"][0]["id"]

        async with ratelimit.MUSICBRAINZ:
            async with session.get("artist/" + artist_id, params={"fmt": "json", "inc": "url-rels"}) as response:
                artist_json = await response.json()

        name = cast(str, artist_json["name"])
        area = cast(str, artist_json["area"]["name"]) if artist_json["area"] is not None else None
        begin_date = cast(str, artist_json["life-span"]["begin"]) if artist_json["life-span"] is not None else None

        for relation in artist_json["relations"]:
            if relation["type"] == "wikidata":
                wikidata = cast(str, relation["url"]["resource"]).removeprefix("https://www.wikidata.org/wiki/")
                break
        else:
            wikidata = None

        return MBArtist(name, area, begin_date, wikidata)
