from sqlite3 import Connection

from aiohttp import web

from raphson_mp.common.image import guess_content_type
from raphson_mp.server import auth, db
from raphson_mp.server.decorators import route


@route("/{artist}/image")
async def image(request: web.Request, _conn: Connection, _user: auth.User):
    artist = request.match_info["artist"]
    with db.OFFLINE.connect() as conn_offline:
        (artist_img,) = conn_offline.execute("SELECT img FROM artist_img WHERE artist = ?", (artist,)).fetchone()
    return web.Response(body=artist_img, content_type=guess_content_type(artist_img))


@route("/{artist}/extract")
async def extract(_request: web.Request, _conn: Connection, _user: auth.User):
    raise web.HTTPNoContent()
