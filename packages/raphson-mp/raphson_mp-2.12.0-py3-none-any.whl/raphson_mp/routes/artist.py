from sqlite3 import Connection

from aiohttp import web

from raphson_mp.common.image import ImageFormat, ImageQuality
from raphson_mp.server import auth, settings
from raphson_mp.server.blob import ArtistImageThumbBlob, ArtistWikiBlob
from raphson_mp.server.decorators import route


@route("/{artist}/image")
async def image(request: web.Request, _conn: Connection, _user: auth.User):
    artist_name = request.match_info["artist"]
    img_format = ImageFormat(request.query.get("format", settings.default_image_format))
    img_quality = ImageQuality(request.query.get("quality", ImageQuality.HIGH))
    return await ArtistImageThumbBlob(artist_name, img_format, img_quality).response()


@route("/{artist}/extract")
async def extract(request: web.Request, _conn: Connection, _user: auth.User):
    artist_name = request.match_info["artist"]
    return await ArtistWikiBlob(artist_name).response()
