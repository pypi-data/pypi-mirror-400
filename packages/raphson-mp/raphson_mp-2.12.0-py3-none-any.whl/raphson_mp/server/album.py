import asyncio
import logging
import random

from raphson_mp.common import const, image, process
from raphson_mp.server import bing, cache, ffmpeg, musicbrainz, reddit
from raphson_mp.server.features import FEATURES, Feature

_LOGGER = logging.getLogger(__name__)


async def _get_cover_data(artist: str | None, album: str, meme: bool):
    _LOGGER.debug("find cover for artist=%s album=%s", artist, album)

    if meme:
        if random.random() > 0.5:
            if image_bytes := await reddit.get_image(album):
                _LOGGER.debug("returning reddit meme for artist=%s album=%s", artist, album)
                return cache.CacheData(image_bytes, cache.MONTH)

        if image_bytes := await bing.image_search(album + " meme"):
            _LOGGER.debug("returning bing meme for artist=%s album=%s", artist, album)
            return cache.CacheData(image_bytes, cache.MONTH)

        _LOGGER.debug("no meme found for artist=%s album=%s, try finding regular cover", artist, album)

    # Try MusicBrainz first (high resolution, likely a good album cover)
    if artist:
        if image_bytes := await musicbrainz.get_cover(artist, album):
            _LOGGER.debug("returning musicbrainz cover for artist=%s album=%s", artist, album)
            return cache.CacheData(image_bytes, cache.HALFYEAR)

    if artist:
        query = artist + " - " + album
    else:
        query = album + " album cover art"

    # If available, try Spotify (lower resolution but very likely good album cover)
    if Feature.SPOTIFY in FEATURES:
        from raphson_mp.server import spotify

        if image_bytes := await spotify.CLIENT.get_album_image(album, artist):
            _LOGGER.debug("returning spotify cover for artist=%s album=%s", artist, album)
            return cache.CacheData(image_bytes, cache.HALFYEAR)

    # Otherwise try Bing (terrible, but it's something)
    if image_bytes := await bing.image_search(query):
        _LOGGER.debug("returning bing cover for artist=%s album=%s query=%s", artist, album, query)
        return cache.CacheData(image_bytes, cache.MONTH)

    _LOGGER.debug("returning fallback raphson cover for artist=%s album=%s", artist, album)
    return cache.CacheData(const.RAPHSON_PNG_PATH.read_bytes(), cache.WEEK)


async def _get_cover(artist: str | None, album: str, meme: bool) -> bytes:
    """Fetch (or return from cache) a full size album cover"""
    cache_key = f"cover{artist}{album}{meme}"
    return await cache.retrieve_or_store(cache_key, _get_cover_data, artist, album, meme)


async def _get_cover_thumbnail(
    artist: str | None,
    album: str,
    meme: bool,
    img_quality: image.ImageQuality,
    img_format: image.ImageFormat,
) -> cache.CacheData:
    """Get a cover image and transcode it to a smaller size"""
    original_bytes = await _get_cover(artist, album, meme)

    _LOGGER.debug(
        "transcoding cover to a thumbnail for artist=%s album=%s meme=%s img_quality=%s img_format=%s",
        artist,
        album,
        meme,
        img_quality,
        img_format,
    )

    thumbnail = await ffmpeg.image_thumbnail(
        original_bytes,
        img_format,
        img_quality,
        square=not meme,
    )

    return cache.CacheData(thumbnail, cache.MONTH)


async def get_cover_thumbnail(
    artist: str | None, album: str, meme: bool, img_quality: image.ImageQuality, img_format: image.ImageFormat
):
    """Generate (or retrieve from cache) a thumbnail album cover"""
    cache_key = f"coverthumb{artist}{album}{meme}{img_quality.value}{img_format.value}"
    try:
        return await cache.retrieve_or_store(
            cache_key, _get_cover_thumbnail, artist, album, meme, img_quality, img_format
        )
    except process.ProcessReturnCodeError:
        _LOGGER.warning("failed to generate thumbnail, is the image corrupt? artist=%s album=%s", artist, album)
        png_data = await asyncio.to_thread(const.RAPHSON_PNG_PATH.read_bytes)
        return await ffmpeg.image_thumbnail(png_data, img_format, img_quality, True)


async def remove_cached_cover(artist: str | None, album: str, meme: bool):
    await cache.delete(f"cover{artist}{album}{meme}")
    for img_format in image.ImageFormat:
        for img_quality in image.ImageQuality:
            await cache.delete(f"coverthumb{artist}{album}{meme}{img_quality.value}{img_format.value}")
