from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from collections.abc import Iterator
from pathlib import Path
from sqlite3 import Connection
from typing import cast

from typing_extensions import override

from raphson_mp.common import metadata
from raphson_mp.common.image import ImageFormat, ImageQuality
from raphson_mp.common.track import (
    MUSIC_EXTENSIONS,
    TRASH_PREFIX,
    VIRTUAL_PLAYLIST,
    NoSuchTrackError,
    TrackBase,
    VirtualTrackUnavailableError,
    relpath_playlist,
)
from raphson_mp.server import album, cache, ffmpeg, settings

log = logging.getLogger(__name__)


def to_relpath(path: Path) -> str:
    """
    Returns: Relative path as string, excluding base music directory
    """
    assert settings.music_dir is not None, "cannot use to_relpath in offline mode"

    relpath = path.as_posix()[len(settings.music_dir.as_posix()) + 1 :]
    return relpath if len(relpath) > 0 else ""


def from_relpath(relpath: str) -> Path:
    """
    Creates Path object from string path relative to music base directory, with directory
    traversal protection.
    """
    assert settings.music_dir is not None, "cannot use from_relpath in offline mode"

    if relpath and (relpath[0] == "/" or relpath[-1] == "/"):
        raise ValueError("relpath must not start or end with slash: " + relpath)

    # resolve() is important for is_relative_to to work properly!
    path = Path(settings.music_dir, relpath).resolve()

    if not path.is_relative_to(settings.music_dir):
        raise ValueError(f"path {path.as_posix()} is not inside music base directory {settings.music_dir.as_posix()}")

    return path


def is_trashed(path: Path) -> bool:
    """
    Returns: Whether this file or directory is trashed, by checking for the
    trash prefix in all path parts.
    """
    for part in path.parts:
        if part.startswith(TRASH_PREFIX):
            return True
    return False


def is_music_file(path: Path) -> bool:
    """
    Returns: Whether the provided path is a music file, by checking its extension
    """
    if not path.is_file():
        return False
    if is_trashed(path):
        return False
    for ext in MUSIC_EXTENSIONS:
        if path.name.endswith(ext):
            return True
    return False


def list_tracks_recursively(path: Path, trashed: bool = False) -> Iterator[Path]:
    """
    Scan directory for tracks, recursively
    Args:
        path: Directory Path
    Returns: Paths iterator
    """
    for ext in MUSIC_EXTENSIONS:
        for track_path in path.glob("**/*." + ext):
            if is_trashed(track_path) is trashed:
                yield track_path


class Track(TrackBase, ABC):
    @abstractmethod
    async def get_cover(self, meme: bool, img_quality: ImageQuality, img_format: ImageFormat) -> bytes: ...


class FileTrack(Track):
    def __init__(self, conn: Connection, relpath: str):
        query = "SELECT mtime, ctime, duration, title, album, album_artist, track_number, year, video, lyrics FROM track WHERE path=?"
        row = conn.execute(query, (relpath,)).fetchone()
        if row is None:
            raise NoSuchTrackError("Missing track from database: " + relpath)

        mtime, ctime, duration, title, album, album_artist, track_number, year, video, lyrics = row

        rows = conn.execute("SELECT artist FROM track_artist WHERE track=?", (relpath,)).fetchall()
        artists = metadata.sort_artists([row[0] for row in rows], album_artist)

        rows = conn.execute("SELECT tag FROM track_tag WHERE track=?", (relpath,)).fetchall()
        tags = [row[0] for row in rows]

        super().__init__(
            path=relpath,
            mtime=mtime,
            ctime=ctime,
            duration=duration,
            title=title,
            album=album,
            album_artist=album_artist,
            year=year,
            track_number=track_number,
            video=video,
            lyrics=lyrics,
            artists=artists,
            tags=tags,
        )

    @property
    def filepath(self) -> Path:
        assert self.playlist != VIRTUAL_PLAYLIST
        return from_relpath(self.path)

    @property
    def metadata(self) -> ffmpeg.Metadata:
        return ffmpeg.Metadata(
            duration=self.duration,
            artists=self.artists,
            album=self.album,
            title=self.title,
            year=self.year,
            album_artist=self.album_artist,
            track_number=self.track_number,
            tags=self.tags,
            lyrics=self.lyrics,
            video=self.video,
        )

    async def get_loudness(self, conn: Connection) -> ffmpeg.LoudnessParams:
        # look for loudness in database
        row = conn.execute(
            "SELECT input_i, input_tp, input_lra, input_thresh, target_offset FROM track_loudness WHERE track = ?",
            (self.path,),
        ).fetchone()
        if row is not None:
            return {
                "input_i": row[0],
                "input_tp": row[1],
                "input_lra": row[2],
                "input_thresh": row[3],
                "target_offset": row[4],
                "normalization_type": "",
            }

        # look for loudness in legacy cache
        data = await cache.retrieve(f"loud4{self.path}{self.mtime}")
        if data is not None:
            loudness = cast(ffmpeg.LoudnessParams, json.loads(data))
        else:
            # measure loudness
            loudness = await ffmpeg.measure_loudness(self.filepath)

        # store in database for next time
        conn.execute(
            "INSERT INTO track_loudness VALUES (?, ?, ?, ?, ?, ?)",
            (
                self.path,
                loudness["input_i"],
                loudness["input_tp"],
                loudness["input_lra"],
                loudness["input_thresh"],
                loudness["target_offset"],
            ),
        )

        return loudness

    @property
    def _album_search_name(self) -> str:
        if self.album and not metadata.album_is_compilation(self.album):
            return self.album
        elif self.title:
            return self.title
        else:
            return self.display_title(show_album=False, show_year=False)

    @property
    def _album_search_artist(self) -> str | None:
        return self.album_artist if self.album_artist else self.primary_artist

    @override
    async def get_cover(self, meme: bool, img_quality: ImageQuality, img_format: ImageFormat) -> bytes:
        return await album.get_cover_thumbnail(
            self._album_search_artist, self._album_search_name, meme, img_quality, img_format
        )

    async def delete_cached_cover(self, meme: bool) -> None:
        await album.remove_cached_cover(self._album_search_artist, self._album_search_name, meme)

    async def save(self) -> None:
        await ffmpeg.save_metadata(self.filepath, self.metadata)


async def get_track(conn: Connection, relpath: str) -> Track:
    if relpath_playlist(relpath) == VIRTUAL_PLAYLIST:
        if settings.offline_mode:
            raise VirtualTrackUnavailableError()

        from raphson_mp.server.virtual_track import VIRTUAL_TRACK_TYPES

        parts = relpath.split("/")
        assert parts[0] == VIRTUAL_PLAYLIST
        track = VIRTUAL_TRACK_TYPES[parts[1]]
        return await track.get_instance(parts[2:])
    else:
        return FileTrack(conn, relpath)


def filter_tracks(
    conn: Connection,
    limit: int,
    offset: int,
    *,
    playlist: str | None = None,
    artist: str | None = None,
    tag: str | None = None,
    album_artist: str | None = None,
    album: str | None = None,
    year: int | None = None,
    title: str | None = None,
    has_metadata: bool | None = None,
    order: str | None = None,
) -> list[FileTrack]:
    select_query = "SELECT path FROM track INDEXED BY idx_track_filter"
    where_query = "WHERE true"
    params: list[str | int] = []
    if playlist:
        where_query += " AND playlist = ?"
        params.append(playlist)

    if artist:
        select_query += " JOIN track_artist ON path = track"
        where_query += " AND artist = ?"
        params.append(artist)

    if tag:
        select_query += " JOIN track_tag ON path = track"
        where_query += " AND tag = ?"
        params.append(tag)

    if album_artist:
        where_query += " AND album_artist = ?"
        params.append(album_artist)

    if album:
        where_query += " AND album = ?"
        params.append(album)

    if year:
        where_query += " AND year = ?"
        params.append(year)

    if title:
        where_query += " AND title = ?"
        params.append(title)

    if has_metadata:
        # Has at least metadata for: title, album, album artist, artists
        where_query += """
            AND title NOT NULL
            AND album NOT NULL
            AND album_artist NOT NULL
            AND EXISTS(SELECT artist FROM track_artist WHERE track = path)
            """

    if has_metadata is False:
        where_query += """ AND (
            title IS NULL
            OR album IS NULL
            OR album_artist IS NULL
            OR NOT EXISTS(SELECT artist FROM track_artist WHERE track = path)
            OR year IS NULL
            )"""

    if order:
        order_query_parts: list[str] = []
        for order_item in order.split(","):
            if order_item == "title":
                order_query_parts.append("title ASC")
            elif order_item == "ctime_asc":
                order_query_parts.append("ctime ASC")
            elif order_item == "ctime_desc":
                order_query_parts.append("ctime DESC")
            elif order_item == "year_asc":
                order_query_parts.append("year ASC")
            elif order_item == "year_desc":
                order_query_parts.append("year DESC")
            elif order_item == "random":
                order_query_parts.append("RANDOM()")
            elif order_item == "number":
                order_query_parts.append("track_number ASC")
            else:
                log.warning("ignoring invalid order: %s", order_item)
        order_query = "ORDER BY " + ", ".join(order_query_parts)
    else:
        order_query = ""

    query = f"{select_query} {where_query} {order_query} LIMIT {limit} OFFSET {offset}"

    log.debug("filter: %s", query)

    result = conn.execute(query, params)
    return [FileTrack(conn, relpath) for relpath, in result]
