from sqlite3 import Connection

from aiohttp import web

from raphson_mp.server.auth import User
from raphson_mp.server.decorators import route
from raphson_mp.server.playlist import get_playlists
from raphson_mp.server.response import template


@route("")
async def route_playlists(_request: web.Request, conn: Connection, user: User):
    """
    Playlist management page
    """
    return await template(
        "playlist_management.jinja2",
        user_is_admin=user.admin,
        playlists=get_playlists(conn, user),
    )


@route("/set_favorites", method="POST")
async def set_favorites(request: web.Request, conn: Connection, user: User):
    form = await request.post()
    playlists = [playlist for playlist in form.keys() if playlist != "csrf"]
    with conn:
        conn.execute("DELETE FROM user_playlist_favorite WHERE user = ?", (user.user_id,))
        conn.executemany(
            "INSERT INTO user_playlist_favorite VALUES (?, ?)", [(user.user_id, playlist) for playlist in playlists]
        )

    raise web.HTTPSeeOther("/playlist_management")


@route("/set_primary", method="POST")
async def set_primary(request: web.Request, conn: Connection, user: User):
    form = await request.post()
    playlist = form["playlist"]
    assert isinstance(playlist, str)
    if playlist == "":
        playlist = None
    conn.execute("UPDATE user SET primary_playlist = ? WHERE id = ?", (playlist, user.user_id))
    raise web.HTTPSeeOther("/playlist_management")
