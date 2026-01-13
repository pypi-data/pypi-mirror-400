import logging
from sqlite3 import Connection
from typing import cast

from aiohttp import web

from raphson_mp.server import auth, settings
from raphson_mp.server.auth import AuthError, User
from raphson_mp.server.decorators import route
from raphson_mp.server.features import FEATURES, Feature
from raphson_mp.server.response import template

_LOGGER = logging.getLogger(__name__)


@route("/login", public=True)
async def route_login_get(request: web.Request, conn: Connection):
    try:
        await auth.verify_auth_cookie(conn, request)
        # User is already logged in
        raise web.HTTPSeeOther("/")
    except AuthError:
        pass

    (user_count,) = conn.execute("SELECT COUNT(*) FROM user").fetchone()
    if user_count == 0:
        return await template("login_noaccounts.jinja2")

    if Feature.WEBAUTHN in FEATURES:
        from raphson_mp.server import challenge

        webauthn_challenge = challenge.generate()
    else:
        webauthn_challenge = None

    return await template(
        "login.jinja2",
        invalid_password=request.query.get("pw") == "1",
        webauthn_challenge=webauthn_challenge,
        login_message=settings.login_message,
    )


@route("/login", method="POST", public=True)
async def route_login_post(request: web.Request, conn: Connection):
    if request.content_type == "application/json":
        data = await request.json()
    else:
        data = await request.post()
    username: str = cast(str, data["username"])
    password: str = cast(str, data["password"])

    session = await auth.log_in(request, conn, username, password)

    if session is None:
        if request.content_type == "application/json":
            raise web.HTTPForbidden()

        raise web.HTTPSeeOther("/auth/login?pw=1")

    if request.content_type == "application/json":
        return web.json_response({"token": session.token, "csrf": session.csrf_token})

    response = web.HTTPSeeOther("/")
    session.set_cookie(request, response)
    raise response


@route("/get_csrf")
async def route_get_csrf(_request: web.Request, _conn: Connection, user: User):
    """
    Get CSRF token
    """
    return web.json_response({"token": user.csrf})


@route("/webauthn_setup", method="POST")
async def webauthn_setup(request: web.Request, conn: Connection, user: auth.User):
    if Feature.WEBAUTHN not in FEATURES:
        raise web.HTTPServiceUnavailable()

    from raphson_mp.server import webauthn

    await webauthn.setup(request, conn, user)
    raise web.HTTPNoContent()


@route("/webauthn_login", method="POST", public=True, skip_csrf_check=True)
async def webauthn_login(request: web.Request, conn: Connection):
    if Feature.WEBAUTHN not in FEATURES:
        raise web.HTTPServiceUnavailable()

    from raphson_mp.server import webauthn

    session = await webauthn.log_in(request, conn)
    response = web.HTTPNoContent()
    session.set_cookie(request, response)
    raise response
