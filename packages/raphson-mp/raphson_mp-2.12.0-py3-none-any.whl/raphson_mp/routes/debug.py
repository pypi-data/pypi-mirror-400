import asyncio
import logging
import random
from sqlite3 import Connection

from aiohttp import web

from raphson_mp.server import auth
from raphson_mp.server.background_task import (
    BackgroundTask,
    ProgressMonitor,
    WebProgressMonitor,
)
from raphson_mp.server.decorators import route
from raphson_mp.server.response import template

_LOGGER = logging.getLogger(__name__)


async def _dummy_task(progress: ProgressMonitor):
    for i in range(20):
        progress.task_start(f"task {i+1}")
        await asyncio.sleep(random.random() + 0.3)
        progress.task_done(f"task {i+1}")


SYNC_TASK = BackgroundTask(_dummy_task, _LOGGER)


@route("")
async def root(_request: web.Request, _conn: Connection, _user: auth.User):
    return await template("debug.jinja2")


@route("/start", method="POST")
async def start(_request: web.Request, _conn: Connection, _user: auth.User):
    SYNC_TASK.start()
    raise web.HTTPNoContent()


@route("/stop", method="POST")
async def stop(_request: web.Request, _conn: Connection, _user: auth.User):
    SYNC_TASK.stop()
    raise web.HTTPNoContent()


@route("/monitor")
async def monitor(request: web.Request, _conn: Connection, _user: auth.User):
    progress = WebProgressMonitor()
    SYNC_TASK.attach_monitor(progress)
    return progress.response(request)
