from __future__ import annotations

import asyncio
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from sqlite3 import Connection

from raphson_mp.common import eventbus
from raphson_mp.common.control import FileAction
from raphson_mp.common.track import VIRTUAL_PLAYLIST, relpath_playlist
from raphson_mp.server import auth, db, events, ffmpeg, settings, track
from raphson_mp.server.playlist import Playlist

log = logging.getLogger(__name__)

SCANNER_LOCK = asyncio.Lock()


class Counter:
    count: int = 0


DUMMY_COUNTER = Counter()


async def scan_playlists(conn: Connection) -> set[str]:
    """
    Scan playlist directories, add or remove playlists from the database
    where necessary.
    """
    assert settings.music_dir is not None

    async with SCANNER_LOCK:
        names_db = {row[0] for row in conn.execute("SELECT name FROM playlist")}
        paths_disk = [path for path in settings.music_dir.iterdir() if path.is_dir() and not track.is_trashed(path)]
        names_disk = {path.name for path in paths_disk}

        add_to_db: list[tuple[str]] = []
        remove_from_db: list[tuple[str]] = []

        for name in names_db:
            if name not in names_disk:
                log.info("going to delete playlist: %s", name)
                remove_from_db.append((name,))

        for name in names_disk:
            if name not in names_db:
                log.info("new playlist: %s", name)
                add_to_db.append((name,))

        if add_to_db:
            conn.executemany("INSERT INTO playlist (name) VALUES (?)", add_to_db)
        if remove_from_db:
            conn.executemany("DELETE FROM playlist WHERE name=?", remove_from_db)

    return names_disk


async def _update_db(
    user: auth.User | None,
    path: Path,
    relpath: str,
    mtime: int,
    update: bool,
) -> bool:
    meta = await ffmpeg.probe_metadata(path)
    if meta is None:
        if update:
            with db.MUSIC.connect() as conn:
                log.warning("Metadata error, delete track from database")
                conn.execute("DELETE FROM track WHERE path=?", (relpath,))
                await _log(conn, events.FileChangeEvent(FileAction.DELETE, relpath, user))
        return False

    playlist = relpath_playlist(relpath)
    assert playlist != VIRTUAL_PLAYLIST
    ctime = int(time.time())

    with db.MUSIC.connect() as conn:
        if update:
            conn.execute(
                """
                UPDATE track
                SET duration=?, title=?, album=?, album_artist=?, track_number=?, year=?, lyrics=?, video=?, mtime=?
                WHERE path=?
                """,
                (
                    meta.duration,
                    meta.title,
                    meta.album,
                    meta.album_artist,
                    meta.track_number,
                    meta.year,
                    meta.lyrics,
                    meta.video,
                    mtime,
                    relpath,
                ),
            )

            conn.execute("DELETE FROM track_artist WHERE track=?", (relpath,))
            conn.execute("DELETE FROM track_tag WHERE track=?", (relpath,))
        else:
            conn.execute(
                """
                INSERT INTO track (path, playlist, duration, title, album, album_artist, track_number, year, lyrics, video, mtime, ctime)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    relpath,
                    playlist,
                    meta.duration,
                    meta.title,
                    meta.album,
                    meta.album_artist,
                    meta.track_number,
                    meta.year,
                    meta.lyrics,
                    meta.video,
                    mtime,
                    ctime,
                ),
            )

        conn.executemany(
            "INSERT INTO track_artist (track, artist) VALUES (?, ?)",
            [(relpath, artist) for artist in meta.artists],
        )
        conn.executemany("INSERT INTO track_tag (track, tag) VALUES (?, ?)", [(relpath, tag) for tag in meta.tags])

        await _log(conn, events.FileChangeEvent(FileAction.UPDATE if update else FileAction.INSERT, relpath, user))
    return True


async def scan_playlist(
    user: auth.User | None,
    playlist: str | Playlist,
    counter: Counter = DUMMY_COUNTER,
) -> None:
    """
    Scan for added, removed or changed tracks in a playlist.
    """
    if isinstance(playlist, Playlist):
        playlist = playlist.name
    assert playlist  # ensure playlist name is not empty

    async with SCANNER_LOCK:
        log.info("scanning playlist: %s", playlist)

        with db.MUSIC.connect() as conn:
            tracks: dict[str, int] = {
                path: mtime
                for path, mtime in conn.execute("SELECT path, mtime FROM track WHERE playlist=?", (playlist,))
            }

        for relpath, db_mtime in tracks.items():
            path = track.from_relpath(relpath)

            if not track.is_music_file(path):
                with db.MUSIC.connect() as conn:
                    log.info("deleted: %s", relpath)
                    conn.execute("DELETE FROM track WHERE path=?", (relpath,))
                    await _log(conn, events.FileChangeEvent(FileAction.DELETE, relpath, user))
                    counter.count += 1
                return

            file_mtime = int(path.stat().st_mtime)
            if file_mtime != db_mtime:
                # Update existing track in database
                log.info(
                    "changed, update: %s (%s to %s)",
                    relpath,
                    datetime.fromtimestamp(db_mtime, tz=timezone.utc),
                    datetime.fromtimestamp(file_mtime, tz=timezone.utc),
                )
                await _update_db(user, path, relpath, file_mtime, True)
                counter.count += 1

        for path in track.list_tracks_recursively(track.from_relpath(playlist)):
            relpath = track.to_relpath(path)
            if relpath not in tracks:
                # Track does not yet exist in database
                log.info("new track, insert: %s", relpath)
                file_mtime = int(path.stat().st_mtime)
                await _update_db(user, path, relpath, file_mtime, False)
                counter.count += 1


async def scan_track(user: auth.User | None, path: Path) -> None:
    """
    Scan single track for changes
    """
    relpath = track.to_relpath(path)

    # Scanning a single track is not supported anymore, maybe I will add it back in the future
    # Scan the entire playlist
    # await scan_playlist(user, relpath_playlist(track.to_relpath(path)))

    async with SCANNER_LOCK:
        with db.MUSIC.connect() as conn:
            if not track.is_music_file(path):
                if conn.execute("SELECT 1 FROM track WHERE path=?", (relpath,)).fetchone() is None:
                    # already not in the database
                    return

                log.info("deleted: %s", relpath)
                conn.execute("DELETE FROM track WHERE path=?", (relpath,))
                await _log(conn, events.FileChangeEvent(FileAction.DELETE, relpath, user))
                return

            file_mtime = int(path.stat().st_mtime)
            mtime_row = conn.execute("SELECT mtime FROM track WHERE path = ?", (relpath,)).fetchone()

            if mtime_row is None:
                log.info("new track, insert: %s", relpath)
                await _update_db(user, path, relpath, file_mtime, False)
            elif (db_mtime := mtime_row[0]) != file_mtime:
                log.info(
                    "changed, update: %s (%s to %s)",
                    relpath,
                    datetime.fromtimestamp(db_mtime, tz=timezone.utc),
                    datetime.fromtimestamp(file_mtime, tz=timezone.utc),
                )
                await _update_db(user, path, relpath, file_mtime, True)


async def move(user: auth.User | None, from_path: Path, to_path: Path):
    from_relpath = track.to_relpath(from_path)
    to_relpath = track.to_relpath(to_path)
    to_playlist = relpath_playlist(to_relpath)
    was_music_file = track.is_music_file(from_path)
    from_path.rename(to_path)
    now_music_file = track.is_music_file(to_path)

    if not was_music_file or not now_music_file:

        if was_music_file:  # music -> trash: remove old file from database
            await scan_track(user, from_path)

        if now_music_file:  # trash -> music: add new file
            await scan_track(user, to_path)

        # If the file was trashed and still is, nothing needs to happen
        return

    # Complicated logic to move track without deleting it from and re-adding it to the database
    async with SCANNER_LOCK:
        with db.MUSIC.connect() as conn:
            try:
                if to_path.is_dir():
                    # need to update all children of this directory
                    conn.execute("BEGIN")
                    for (change_relpath,) in conn.execute(
                        "SELECT path FROM track WHERE path LIKE ?", (from_relpath + "/%",)
                    ).fetchall():
                        new_relpath = to_relpath + change_relpath[len(from_relpath) :]
                        log.debug("track in directory has moved from %s to %s", change_relpath, new_relpath)
                        conn.execute(
                            "UPDATE track SET path = ?, playlist = ? WHERE path = ?",
                            (new_relpath, to_playlist, change_relpath),
                        )
                        await _log(conn, events.FileChangeEvent(FileAction.MOVE, new_relpath, user))
                    conn.execute("COMMIT")
                    return

                # the file might not be in the db, if it's not a music file or if it hasn't been scanned yet
                in_db = conn.execute("SELECT 1 FROM track WHERE path = ?", (from_relpath,)).fetchone() is not None
                if in_db:
                    conn.execute(
                        "UPDATE track SET path = ?, playlist = ? WHERE path = ?",
                        (to_relpath, to_playlist, from_relpath),
                    )
                    await _log(conn, events.FileChangeEvent(FileAction.MOVE, to_relpath, user))
            except Exception as ex:
                # if this somehow went wrong, attempt to rename the track back before raising the exception again
                to_path.rename(from_path)
                raise ex


def last_change(conn: Connection, playlist: str | None) -> datetime:
    if settings.offline_mode:
        return datetime.now(tz=timezone.utc)

    if playlist is not None:
        query = "SELECT MAX(timestamp) FROM scanner_log WHERE playlist = ?"
        params = (playlist,)
    else:
        query = "SELECT MAX(timestamp) FROM scanner_log"
        params = ()
    (mtime,) = conn.execute(query, params).fetchone()
    if mtime is None:
        mtime = 0

    return datetime.fromtimestamp(mtime, timezone.utc)


async def scan(user: auth.User | None, counter: Counter = DUMMY_COUNTER) -> None:
    """
    Main function for scanning music directory structure
    """
    if settings.offline_mode:
        log.info("skip scanner in offline mode")
        return

    with db.MUSIC.connect() as conn:
        playlists = await scan_playlists(conn)

    for playlist in playlists:
        await scan_playlist(user, playlist, counter)


async def _log(conn: Connection, event: events.FileChangeEvent):
    await eventbus.fire(event)
    playlist_name = event.track[: event.track.index("/")]
    user_id = event.user.user_id if event.user else None

    conn.execute(
        """
        INSERT INTO scanner_log (timestamp, action, playlist, track, user)
        VALUES (?, ?, ?, ?, ?)
        """,
        (int(time.time()), event.action.value, playlist_name, event.track, user_id),
    )
