import asyncio
import logging
import time
from pathlib import Path
from sqlite3 import Connection

from aiohttp import web
from typing_extensions import override

from raphson_mp.common.playlist import PlaylistBase
from raphson_mp.common.tag import TagMode
from raphson_mp.common.track import VIRTUAL_PLAYLIST, relpath_playlist
from raphson_mp.common.typing import PlaylistDict
from raphson_mp.server import auth, settings
from raphson_mp.server.track import FileTrack, Track, from_relpath, to_relpath

_LOGGER = logging.getLogger(__name__)
_TRACK_CHOOSE_LOCK = asyncio.Lock()


class PlaylistStats:
    name: str
    track_count: int
    total_duration: int
    mean_duration: int
    artist_count: int
    has_title_count: int
    has_album_count: int
    has_album_artist_count: int
    has_year_count: int
    has_artist_count: int
    has_tag_count: int
    most_recent_choice: int
    least_recent_choice: int
    most_recent_mtime: int

    def __init__(self, conn: Connection, name: str):
        self.name = name
        row = conn.execute(
            "SELECT COUNT(*), SUM(duration), AVG(duration) FROM track WHERE playlist=?",
            (name,),
        ).fetchone()
        self.track_count, self.total_duration, self.mean_duration = row

        row = conn.execute(
            """
            SELECT COUNT(DISTINCT artist)
            FROM track_artist JOIN track ON track.path=track
            WHERE playlist=?
            """,
            (name,),
        ).fetchone()
        (self.artist_count,) = row

        (
            self.has_title_count,
            self.has_album_count,
            self.has_album_artist_count,
            self.has_year_count,
            self.most_recent_choice,
            self.least_recent_choice,
            self.most_recent_mtime,
        ) = conn.execute(
            """
            SELECT SUM(title IS NOT NULL),
                    SUM(album IS NOT NULL),
                    SUM(album_artist IS NOT NULL),
                    SUM(year IS NOT NULL),
                    MAX(last_chosen),
                    MIN(last_chosen),
                    MAX(mtime)
            FROM track WHERE playlist=?
            """,
            (name,),
        ).fetchone()

        (self.has_artist_count,) = conn.execute(
            """
            SELECT COUNT(DISTINCT track)
            FROM track_artist JOIN track ON track.path = track
            WHERE playlist=?
            """,
            (name,),
        ).fetchone()

        (self.has_tag_count,) = conn.execute(
            """
            SELECT COUNT(DISTINCT track)
            FROM track_tag JOIN track ON track.path = track
            WHERE playlist=?
            """,
            (name,),
        ).fetchone()


class Playlist(PlaylistBase):
    primary: bool
    sync_type: str | None
    sync_ref: str | None

    def __init__(self, conn: Connection, name: str, user: auth.User | None = None):
        if name == VIRTUAL_PLAYLIST:
            raise ValueError("cannot create Playlist object for virtual playlist")

        self.sync_type, self.sync_ref = conn.execute(
            "SELECT sync_type, sync_ref FROM playlist WHERE name = ?", (name,)
        ).fetchone()

        track_count, duration = conn.execute(
            "SELECT COUNT(*), COALESCE(SUM(duration), 0) FROM track WHERE playlist=?", (name,)
        ).fetchone()

        # safe default: if user is forgotten but writability is checked, the playlist should not be writable
        writable = user is not None and (
            user.admin
            or conn.execute(
                "SELECT 1 FROM user_playlist_write WHERE playlist=? AND user=?",
                (name, user.user_id),
            ).fetchone()
            is not None
        )

        favorite = (
            user is not None
            and conn.execute(
                "SELECT 1 FROM user_playlist_favorite WHERE playlist=? AND user=?",
                (name, user.user_id),
            ).fetchone()
            is not None
        )

        super().__init__(
            name=name,
            track_count=track_count,
            duration=duration,
            writable=writable,
            favorite=favorite,
            synced=self.sync_type is not None,
        )

        self.primary = user is not None and name == user.primary_playlist

    @override
    def __eq__(self, other: object):
        return isinstance(other, Playlist) and self.name == other.name

    @property
    def path(self) -> Path:
        return from_relpath(self.name)

    async def choose_track(
        self,
        conn: Connection,
        user: auth.User | None,
        require_metadata: bool = False,
        tag_mode: TagMode | None = None,
        tags: list[str] | None = None,
        intersect_playlists: list[str] | None = None,
    ) -> Track | None:
        """
        Randomly choose a track from this playlist
        Args:
            user: optionally specify a user to exclude tracks that this user has disliked
            require_metadata: only return tracks with at least some metadata (title, album, artists)
            tag_mode Tag mode (optional, must provide tags)
            tags: List of tags (optional, must provide tag_mode)
        Returns: Track object
        """
        # Select least recently played tracks
        params: list[str | int] = []
        query = "SELECT track.path, last_chosen FROM track"

        if intersect_playlists is not None:
            query += " JOIN track_artist ON track.path = track_artist.track"

        query += " WHERE playlist = ?"
        params.append(self.name)

        # don't choose disliked track
        if user is not None:
            query += " AND NOT EXISTS (SELECT 1 FROM dislikes WHERE user=? AND track=path)"
            params.append(user.user_id)

        # don't choose a track with reported problem
        query += " AND NOT EXISTS (SELECT 1 FROM track_problem WHERE track=path)"

        # tags
        track_tags_query = "SELECT tag FROM track_tag WHERE track = track.path"
        if tag_mode is TagMode.ALLOW:
            assert tags is not None
            query += " AND (" + " OR ".join(len(tags) * [f"? IN ({track_tags_query})"]) + ")"
            params.extend(tags)
        elif tag_mode is TagMode.DENY:
            assert tags is not None
            query += " AND (" + " AND ".join(len(tags) * [f"? NOT IN ({track_tags_query})"]) + ")"
            params.extend(tags)

        # metadata is required for guessing game
        if require_metadata:
            # Has at least metadata for: title, album, artists
            query += (
                " AND title NOT NULL AND album NOT NULL AND EXISTS(SELECT artist FROM track_artist WHERE track = path)"
            )

        if intersect_playlists is not None:
            # The track chosen from this playlist must be from an artist that is at least in one other playlist
            artists: set[str] = set()
            for playlist in intersect_playlists:
                for (artist,) in conn.execute(
                    "SELECT DISTINCT artist FROM track JOIN track_artist ON path = track WHERE playlist = ?",
                    (playlist,),
                ):
                    artists.add(artist)

            query += " AND artist IN (" + ",".join(["?"] * len(artists)) + ")"
            params.extend(artists)

        query += f" ORDER BY last_chosen ASC LIMIT {self.track_count // 4  + 1}"

        # From selected least recently played tracks, choose a random one
        query = "SELECT * FROM (" + query + ") ORDER BY RANDOM() LIMIT 1"

        async with _TRACK_CHOOSE_LOCK:
            _LOGGER.debug("choose track query: %s", query)
            _LOGGER.debug("choose track params: %s", params)

            row = conn.execute(query, params).fetchone()
            if row is None:
                # No track found
                return None

            track, last_chosen = row
            current_timestamp = int(time.time())
            if last_chosen == 0:
                _LOGGER.info("chosen track: %s (never played)", track)
            else:
                hours_ago = (current_timestamp - last_chosen) / 3600
                _LOGGER.info("chosen track: %s (last played %.2f hours ago)", track, hours_ago)

            # it would be nice if this could be done in the background with create_task(), but that would cause
            # duplicate tracks to be chosen at times when the next track is chosen before last_chosen is updated
            conn.execute("UPDATE track SET last_chosen = ? WHERE path=?", (current_timestamp, track))

        return FileTrack(conn, track)

    def stats(self, conn: Connection) -> PlaylistStats:
        """Get playlist statistics"""
        return PlaylistStats(conn, self.name)

    def tracks(self, conn: Connection) -> list[Track]:
        """Get list of tracks in this playlist"""
        tracks: list[Track] = []
        for (relpath,) in conn.execute("SELECT path FROM track WHERE playlist = ?", (self.name,)):
            tracks.append(FileTrack(conn, relpath))
        return tracks

    def to_dict(self) -> PlaylistDict:
        return {
            "name": self.name,
            "track_count": self.track_count,
            "duration": self.duration,
            "favorite": self.favorite,
            "write": self.writable,
            "writable": self.writable,
            "synced": self.synced,
        }

    def set_sync(self, conn: Connection, sync_type: str, sync_ref: str):
        # Protect against accidental deletion of tracks in an existing playlist
        if sync_type != self.sync_type and self.track_count > 0:
            raise web.HTTPBadRequest(reason="can only set up sync for an empty playlist")

        conn.execute(
            "UPDATE playlist SET sync_type = ?, sync_ref = ? WHERE name = ?",
            (sync_type, sync_ref, self.name),
        )


def get_playlists(conn: Connection, user: auth.User | None = None) -> list[Playlist]:
    names = [row[0] for row in conn.execute("SELECT name FROM playlist ORDER BY name ASC")]
    return [Playlist(conn, name, user) for name in names]


def check_path_writable(conn: Connection, user: auth.User, path: Path) -> Playlist:
    if path == settings.music_dir or path.parent == settings.music_dir:
        raise web.HTTPForbidden(reason="cannot write in root directory")

    playlist = Playlist(conn, relpath_playlist(to_relpath(path)), user)
    if not playlist.writable:
        raise web.HTTPForbidden(reason="no write access to playlist: " + playlist.name)
    return playlist
