from __future__ import annotations

import asyncio
import base64
import logging
import random
import shutil
import time
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from sqlite3 import Connection
from typing import cast
from weakref import WeakValueDictionary

from aiohttp import hdrs
from aiohttp.web import FileResponse
from typing_extensions import override

from raphson_mp.common import const, process
from raphson_mp.common.image import ImageFormat, ImageQuality
from raphson_mp.common.track import AudioFormat
from raphson_mp.server import bing, cache, db, ffmpeg, musicbrainz, settings, wikipedia
from raphson_mp.server.features import FEATURES, Feature
from raphson_mp.server.track import FileTrack

_LOGGER = logging.getLogger(__name__)
LOCKS: WeakValueDictionary[str, asyncio.Lock] = WeakValueDictionary()


def _new_blob_id() -> str:
    return base64.urlsafe_b64encode(random.randbytes(16)).decode().rstrip("=")


def _blob_path(blob_id: str) -> Path:
    blob_dir = settings.blob_dir or Path(settings.data_dir, "blob")
    return Path(blob_dir, blob_id[:2], blob_id[2:])


class RefType(Enum):
    TRACK = "track"
    ARTIST = "artist"


_CLEANUP_FIND_QUERIES: dict[RefType, str] = {
    RefType.TRACK: "SELECT id FROM blob LEFT JOIN track ON ref = path WHERE reftype = 'track' AND track.path IS NULL",
    RefType.ARTIST: "SELECT id FROM blob LEFT JOIN track_artist ON ref = artist COLLATE NOCASE WHERE reftype = 'artist' AND artist IS NULL",
}
_CASE_SENSITIVE: dict[RefType, bool] = {
    RefType.TRACK: True,
    RefType.ARTIST: False,
}


class Blob(ABC):
    ref: str
    reftype: RefType
    blobtype: str
    content_type: str | None

    def __init__(self, ref: str, reftype: RefType, blobtype: str, content_type: str | None):
        self.ref = ref
        self.reftype = reftype
        self.blobtype = blobtype
        self.content_type = content_type

    async def get(self) -> Path:
        lock_key = self.reftype.value + self.ref + self.blobtype
        lock = LOCKS.get(lock_key)
        if not lock:
            LOCKS[lock_key] = lock = asyncio.Lock()

        async with lock:
            with db.MUSIC.connect() as conn:
                ref_collate = "" if _CASE_SENSITIVE[self.reftype] else "COLLATE NOCASE"
                row = conn.execute(
                    f"""
                    SELECT id FROM blob
                    WHERE reftype = ? AND ref = ? {ref_collate} AND blobtype = ?
                    """,
                    (self.reftype.value, self.ref, self.blobtype),
                ).fetchone()
                if row:
                    (blob_id,) = cast(tuple[str], row)
                    _LOGGER.debug("returning existing blob: %s", blob_id)
                    path = _blob_path(blob_id)
                    if await asyncio.to_thread(path.is_file):
                        return path
                    else:
                        _LOGGER.warning("blob exists in database but not on disk: %s", blob_id)
                        conn.execute("DELETE FROM blob WHERE id = ?", (blob_id))

            # blob is not stored on disk and needs to be generated

            async def shielded():
                blob_id = _new_blob_id()
                _LOGGER.debug("storing new blob: %s", blob_id)
                path = _blob_path(blob_id)
                await asyncio.to_thread(path.parent.mkdir, parents=True, exist_ok=True)
                await asyncio.to_thread(path.touch)  # file must exist to be able to bind mount it into the sandbox
                await self.produce(path)
                now = int(time.time())

                with db.MUSIC.connect() as conn:
                    conn.execute(
                        "INSERT INTO blob (id, blobtype, ref, reftype, timestamp) VALUES (?, ?, ?, ?, ?)",
                        (blob_id, self.blobtype, self.ref, self.reftype.value, now),
                    )
                return path

            return await asyncio.shield(shielded())

    async def response(self, cache: bool = True):
        assert self.content_type, "Content-Type is not known, this blob is likely not meant to be served directly"
        response = FileResponse(await self.get())
        response.headers[hdrs.CONTENT_TYPE] = self.content_type
        if cache:
            response.headers[hdrs.CACHE_CONTROL] = f"immutable, max-age={84600*30}"
        return response

    @abstractmethod
    async def produce(self, output_path: Path) -> None: ...

    @classmethod
    @abstractmethod
    def missing(cls, conn: Connection) -> Blob | None:
        """Return one missing blob, or None if no blobs are missing"""


class AudioBlob(Blob):
    track: FileTrack
    audio_format: AudioFormat

    def __init__(self, track: FileTrack, audio_format: AudioFormat):
        super().__init__(track.path, RefType.TRACK, "audio_" + audio_format.value, audio_format.content_type)
        self.track = track
        self.audio_format = audio_format

    @override
    async def produce(self, output_path: Path):
        with db.MUSIC.connect() as conn:
            loudness = await self.track.get_loudness(conn)
        await ffmpeg.transcode_audio(self.track.filepath, loudness, self.audio_format, output_path, self.track)

    @override
    @classmethod
    def missing(cls, conn: Connection) -> Blob | None:
        for audio_format in AudioFormat:
            row = conn.execute(
                """
                SELECT path
                FROM track LEFT JOIN blob ON ref = path AND reftype = ? AND blobtype = ?
                WHERE blob.id IS NULL;
                """,
                (RefType.TRACK.value, "audio_" + audio_format.value),
            ).fetchone()
            if row is None:
                continue
            track = FileTrack(conn, row[0])
            return cls(track, audio_format)
        return None


class VideoBlob(Blob):
    track: FileTrack
    ffmpeg_output_format: str

    def __init__(self, track: FileTrack):
        self.track = track
        if track.video == "vp9":
            self.ffmpeg_output_format = "webm"
            output_content_type = "video/webm"
        elif track.video == "h264":
            self.ffmpeg_output_format = "mp4"
            output_content_type = "video/mp4"
        else:
            raise ValueError("file has no suitable video stream")
        super().__init__(track.path, RefType.TRACK, "video", output_content_type)

    @override
    async def produce(self, output_path: Path):
        input_path = self.track.filepath
        await process.run(
            [
                *ffmpeg.common_opts(),
                "-y",
                "-i",
                input_path.as_posix(),
                "-c:v",
                "copy",
                "-map",
                "0:v",
                "-f",
                self.ffmpeg_output_format,
                output_path.as_posix(),
            ],
            ro_mounts=[input_path.as_posix()],
            rw_mounts=[output_path.as_posix()],
        )

    @override
    @classmethod
    def missing(cls, conn: Connection) -> Blob | None:
        row = conn.execute(
            """
            SELECT path
            FROM track LEFT JOIN blob ON ref = path AND reftype = ? AND blobtype = 'video'
            WHERE track.video IS NOT NULL AND blob.id IS NULL;
            """,
            (RefType.TRACK.value,),
        ).fetchone()
        if row is None:
            return None
        return cls(FileTrack(conn, row[0]))


class ArtistImageBlob(Blob):

    def __init__(self, artist: str):
        super().__init__(artist, RefType.ARTIST, "img", None)

    @override
    async def produce(self, output_path: Path):
        img_bytes = await cache.retrieve(f"artistimg{self.ref}")

        # Try Spotify
        if Feature.SPOTIFY in FEATURES:
            if img_bytes is None:
                from raphson_mp.server import spotify

                img_bytes = await spotify.CLIENT.get_artist_image(self.ref)

        # Try Bing
        if img_bytes is None:
            img_bytes = await bing.image_search(self.ref + " artist")

        # Fallback image
        if img_bytes is None:
            img_bytes = await asyncio.to_thread(const.RAPHSON_PNG_PATH.read_bytes)

        output_path.write_bytes(img_bytes)

    @override
    @classmethod
    def missing(cls, conn: Connection) -> Blob | None:
        row = conn.execute(
            """
            SELECT artist
            FROM track_artist LEFT JOIN blob ON ref = artist COLLATE NOCASE AND reftype = ? AND blobtype = ?
            WHERE blob.id IS NULL
            GROUP BY artist
            LIMIT 1
            """,
            (RefType.ARTIST.value, "img"),
        ).fetchone()
        if row is None:
            return None
        return cls(row[0])


class ArtistImageThumbBlob(Blob):
    img_format: ImageFormat
    img_quality: ImageQuality

    def __init__(self, artist: str, img_format: ImageFormat, img_quality: ImageQuality):
        super().__init__(
            artist, RefType.ARTIST, f"imgthumb_{img_format.value}_{img_quality.value}", img_format.content_type
        )
        self.img_format = img_format
        self.img_quality = img_quality

    @override
    async def produce(self, output_path: Path):
        original_path = await ArtistImageBlob(self.ref).get()
        await ffmpeg.image_thumbnail_paths(original_path, output_path, self.img_format, self.img_quality, True)

    @override
    @classmethod
    def missing(cls, conn: Connection) -> Blob | None:
        for img_format in [ImageFormat.JPEG, ImageFormat.WEBP]:
            for img_quality in ImageQuality:
                row = conn.execute(
                    """
                    SELECT artist
                    FROM track_artist LEFT JOIN blob ON ref = artist COLLATE NOCASE AND reftype = ? AND blobtype = ?
                    WHERE blob.id IS NULL
                    GROUP BY artist
                    LIMIT 1
                    """,
                    (RefType.ARTIST.value, f"imgthumb_{img_format.value}_{img_quality.value}"),
                ).fetchone()
                if row is None:
                    return None
                return cls(row[0], img_format, img_quality)


class ArtistWikiBlob(Blob):
    def __init__(self, artist: str):
        super().__init__(artist, RefType.ARTIST, "wiki", "text/plain")

    @override
    async def produce(self, output_path: Path):
        if cached := await cache.retrieve(f"wiki{self.ref}"):
            output_path.write_bytes(cached)
            return

        mb_artist = await musicbrainz.get_artist(self.ref)
        if mb_artist is None or mb_artist.wikidata is None:
            return
        wikipedia_url = await wikipedia.get_url_from_wikidata(mb_artist.wikidata)
        if wikipedia_url is None:
            return
        extract = await wikipedia.get_wikipedia_extract(wikipedia_url)
        output_path.write_text(extract)

    @override
    @classmethod
    def missing(cls, conn: Connection) -> Blob | None:
        row = conn.execute(
            """
            SELECT artist
            FROM track_artist LEFT JOIN blob ON ref = artist COLLATE NOCASE AND reftype = ? AND blobtype = ?
            WHERE blob.id IS NULL
            GROUP BY artist
            LIMIT 1
            """,
            (RefType.ARTIST.value, "wiki"),
        ).fetchone()
        if row is None:
            return None
        return cls(row[0])


BLOB_TYPES: list[type[Blob]] = [AudioBlob, VideoBlob, ArtistImageBlob, ArtistImageThumbBlob, ArtistWikiBlob]


async def cleanup():
    """
    Delete stale blobs on disk: blobs connected with references that no longer
    hold. For example deleted tracks.
    """
    with db.MUSIC.connect() as conn:
        delete_count = 0
        for reftype in RefType:
            to_delete = [cast(str, row[0]) for row in conn.execute(_CLEANUP_FIND_QUERIES[reftype])]
            for blob_id in to_delete:
                try:
                    _LOGGER.debug("delete blob: %s", blob_id)
                    await asyncio.to_thread(_blob_path(blob_id).unlink)
                except FileNotFoundError:
                    _LOGGER.warning("blob was already missing from disk: %s", blob_id)
                conn.execute("DELETE FROM blob WHERE id = ?", (blob_id,))
            delete_count += len(to_delete)
        _LOGGER.info("deleted %s blobs", delete_count)


async def generate_missing():
    """Generate blobs for as long as there are missing blobs"""
    for blob_type in BLOB_TYPES:
        while True:
            # select one missing blob
            with db.MUSIC.connect() as conn:
                blob = blob_type.missing(conn)
            if blob is None:
                break

            _total, _used, free = shutil.disk_usage(_blob_path(""))

            if free < 5 * 1024**3:
                _LOGGER.info("not generating missing blobs, free disk space is low")
                return

            _LOGGER.info("generating missing blob: %s %s %s", blob.reftype, blob.ref, blob.blobtype)
            await blob.get()
