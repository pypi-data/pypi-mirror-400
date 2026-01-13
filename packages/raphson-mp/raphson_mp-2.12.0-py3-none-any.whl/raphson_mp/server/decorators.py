import asyncio
import logging
from collections.abc import Awaitable
from dataclasses import dataclass
from sqlite3 import Connection
from typing import Callable, ParamSpec, Protocol, TypeVar, runtime_checkable

import aiohttp
from aiohttp import web
from aiohttp.typedefs import Handler

from raphson_mp.server import auth, db, i18n, vars


@runtime_checkable
class PublicRouteCallable(Protocol):
    async def __call__(self, request: web.Request, conn: Connection, /) -> web.StreamResponse: ...


@runtime_checkable
class AuthRouteCallable(Protocol):
    async def __call__(self, request: web.Request, conn: Connection, user: auth.User, /) -> web.StreamResponse: ...


RouteCallable = PublicRouteCallable | AuthRouteCallable

_LOGGER = logging.getLogger(__name__)
SAFE_METHODS = {"GET", "HEAD", "PROPFIND", "OPTIONS"}


@dataclass
class Route:
    routedefs: list[web.AbstractRouteDef]


def route(
    *paths: str,
    method: str = "GET",
    public: bool = False,
    require_admin: bool = False,
    skip_csrf_check: bool = False,
    redirect_to_login: bool = False,
) -> Callable[[RouteCallable], Route]:
    assert not (public and require_admin), "cannot be public if admin is required"

    def decorator(route: RouteCallable) -> Route:
        async def handler(request: web.Request) -> web.StreamResponse:
            with db.MUSIC.connect() as conn:
                vars.JINJA_ENV.set(request.config_dict[vars.APP_JINJA_ENV])
                vars.USER.set(None)
                vars.LOCALE.set(i18n.locale_from_request(request))

                if public:
                    assert isinstance(route, PublicRouteCallable)
                    return await route(request, conn)

                assert isinstance(route, AuthRouteCallable)
                require_csrf = not skip_csrf_check and request.method not in SAFE_METHODS
                user = await auth.verify_auth_cookie(
                    conn,
                    request,
                    require_admin=require_admin,
                    require_csrf=require_csrf,
                    redirect_to_login=redirect_to_login,
                )
                vars.USER.set(user)
                vars.LOCALE.set(i18n.locale_from_request(request))

                return await route(request, conn, user)

        return Route([web.route(method, path, handler) for path in paths])

    return decorator


def simple_route(
    *paths: str,
    method: str = "GET",
) -> Callable[[Handler], Route]:
    """Simple route without any authentication"""

    def decorator(handler: Handler) -> Route:
        return Route([web.route(method, path, handler) for path in paths])

    return decorator


RetryParams = ParamSpec("RetryParams")
RetryReturn = TypeVar("RetryReturn")


def retry(
    logger: logging.Logger, retry_count: int = 3, retry_wait: float = 2
) -> Callable[[Callable[RetryParams, Awaitable[RetryReturn]]], Callable[RetryParams, Awaitable[RetryReturn]]]:
    def decorator(func: Callable[RetryParams, Awaitable[RetryReturn]]) -> Callable[RetryParams, Awaitable[RetryReturn]]:
        async def new_func(*args: RetryParams.args, **kwargs: RetryParams.kwargs) -> RetryReturn:
            nonlocal retry_count
            our_retry_count = retry_count
            our_retry_wait = retry_wait
            while True:
                try:
                    return await func(*args, **kwargs)
                except aiohttp.ClientConnectionError as ex:
                    if our_retry_count > 0:
                        logger.info("failed to connect, trying again in %s seconds: %s", our_retry_wait, ex)
                    else:
                        raise ex
                except aiohttp.ClientResponseError as ex:
                    if our_retry_count > 0 and ex.code == 429 and "Retry-After" in ex.history[0].headers:
                        our_retry_wait = int(ex.history[0].headers["Retry-After"])
                        logger.info(
                            "we are rate limited, trying again in %s seconds as instructed by Retry-After header",
                            our_retry_wait,
                        )
                    if our_retry_count > 0 and ex.code in {429, 502, 503}:
                        logger.info("got http error %s, trying again in %s seconds", ex.code, our_retry_wait)
                    else:
                        raise ex

                await asyncio.sleep(our_retry_wait)
                our_retry_count -= 1
                our_retry_wait *= 2

        return new_func

    return decorator
