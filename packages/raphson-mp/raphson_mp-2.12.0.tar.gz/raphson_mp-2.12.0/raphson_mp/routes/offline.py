import logging
from sqlite3 import Connection
from typing import cast

from aiohttp import web

from raphson_mp.common import metadata
from raphson_mp.server import auth, db, offline_sync
from raphson_mp.server.auth import User
from raphson_mp.server.background_task import (
    BackgroundTask,
    ProgressMonitor,
    WebProgressMonitor,
)
from raphson_mp.server.decorators import route
from raphson_mp.server.offline_sync import OfflineSync
from raphson_mp.server.response import template

_LOGGER = logging.getLogger(__name__)


@route("/sync")
async def route_sync(_request: web.Request, _conn: Connection, _user: User):
    with db.OFFLINE.connect() as offline:
        row = offline.execute("SELECT base_url, token FROM settings").fetchone()
        server, token = row if row else ("", "")

        rows = offline.execute("SELECT name FROM playlists")
        playlists = metadata.join_meta_list([row[0] for row in rows])

    return await template("offline_sync.jinja2", server=server, token=token, playlists=playlists)


@route("/settings", method="POST")
async def route_settings(request: web.Request, _conn: Connection, _user: User):
    form = await request.post()
    server = cast(str, form["server"])
    token = cast(str, form["token"])
    playlists = metadata.split_meta_list(cast(str, form["playlists"]))

    offline_sync.change_settings(server, token)
    await offline_sync.change_playlists(playlists)

    raise web.HTTPSeeOther("/offline/sync")


async def _sync(progress: ProgressMonitor):
    await OfflineSync(progress).run()


SYNC_TASK = BackgroundTask(_sync, _LOGGER)


@route("/start", method="POST")
async def sync_start(_request: web.Request, _conn: Connection, _user: auth.User):
    SYNC_TASK.start()
    raise web.HTTPNoContent()


@route("/stop", method="POST")
async def sync_stop(_request: web.Request, _conn: Connection, _user: auth.User):
    SYNC_TASK.stop()
    raise web.HTTPNoContent()


@route("/monitor")
async def monitor(request: web.Request, _conn: Connection, _user: auth.User):
    progress = WebProgressMonitor()
    SYNC_TASK.attach_monitor(progress)
    return progress.response(request)
