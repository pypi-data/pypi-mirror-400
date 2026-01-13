from __future__ import annotations

import json
import logging
from gettext import GNUTranslations
from sqlite3 import Connection
from typing import cast

from aiohttp import hdrs, web

from raphson_mp.common import const, util
from raphson_mp.server import auth, db, i18n, ratelimit, response, settings
from raphson_mp.server.decorators import route, simple_route

log = logging.getLogger(__name__)


@route("", redirect_to_login=True)
async def route_home(_request: web.Request, _conn: Connection, user: auth.User):
    """
    Home page, with links to file manager and music player
    """
    if settings.offline_mode:
        with db.MUSIC.connect() as conn:
            offline_mode_setup = conn.execute("SELECT 1 FROM track LIMIT 1").fetchone() is None
    else:
        offline_mode_setup = False

    return await response.template(
        "home.jinja2",
        user_is_admin=user.admin,
        offline_mode_setup=offline_mode_setup,
        version=const.PACKAGE_VERSION,
    )


@route("/install")
async def route_install(_request: web.Request, _conn: Connection, _user: auth.User):
    return await response.template("install.jinja2")


@simple_route("/pwa")
async def route_pwa(_request: web.Request):
    # Cannot have / as an entrypoint directly, because for some reason the first request
    # to the start_url does not include cookies. Even a regular 302 redirect doesn't work!
    return web.Response(text='<meta http-equiv="refresh" content="0;URL=\'/player\'">', content_type="text/html")


@simple_route("/csp_reports", method="POST")
async def route_csp_reports(request: web.Request):
    if request.content_type != "application/csp-report":
        raise web.HTTPBadRequest(reason="Content-Type must be application/csp-report")

    async with ratelimit.ERROR_REPORT:
        data = await util.get_content_bounded(request)
        log.warning("Received Content-Security-Policy report: %s", json.loads(data))

    raise web.HTTPNoContent()


@simple_route("/report_error", method="POST")
async def route_error_report(request: web.Request):
    async with ratelimit.ERROR_REPORT:
        data = await util.get_content_bounded(request)
        log.warning("Received JavaScript error: %s", data)

    raise web.HTTPNoContent()


# TODO add nice interface
# TODO add a way to discover this page
# TODO require user password
@route("/token")
async def route_token(request: web.Request, conn: Connection, user: auth.User):
    session = await auth.create_session(conn, request, user)
    return web.Response(text=session.token)


@simple_route("/health_check")
async def route_health_check(_request: web.Request):
    return web.Response(text="ok", content_type="text/plain")


@simple_route("/.well-known/security.txt")
async def security_txt(_request: web.Request):
    content = """Contact: mailto:robin@rslot.nl
Expires: 2026-06-01T23:59:59.000Z
Preferred-Languages: nl, en
"""
    return web.Response(text=content, content_type="text/plain")


@simple_route("/messages.js")
async def messages(request: web.Request):
    locale = request.query.get("locale")
    translations = i18n.translations("frontend", locale)
    messages: dict[str, str | dict[int, str]] = {}
    if isinstance(translations, GNUTranslations):
        catalog = cast(
            dict[str | tuple[str, int], str], translations._catalog
        )  # pyright: ignore[reportAttributeAccessIssue]
        for key, val in catalog.items():
            if key == "":  # skip header
                continue
            if isinstance(key, str):
                messages[key] = val
            else:
                if key[0] in messages:
                    cast(dict[int, str], messages[key[0]])[key[1]] = val
                else:
                    messages[key[0]] = {key[1]: val}

    js = f"globalThis.MESSAGES = {json.dumps(messages)};"
    response = web.Response(body=js, content_type="application/javascript")
    response.headers[hdrs.CACHE_CONTROL] = "max-age=3600"
    return response
