import logging
import time
from sqlite3 import Connection
from weakref import WeakSet, WeakValueDictionary

from aiohttp import WSMsgType, web
from aiohttp.web_ws import WebSocketResponse

from raphson_mp.common import eventbus, util
from raphson_mp.common.control import (
    ClientPing,
    ClientPlaying,
    ClientPong,
    ClientRelayCommand,
    ClientState,
    ClientSubscribe,
    ServerFileChange,
    ServerPing,
    ServerPlayed,
    ServerPlayerClosed,
    ServerPlayingStopped,
    ServerPong,
    Topic,
    parse,
    send,
)
from raphson_mp.server import activity, events
from raphson_mp.server.auth import User
from raphson_mp.server.decorators import route
from raphson_mp.server.vars import CLOSE_RESPONSES

_LOGGER = logging.getLogger(__name__)

_BY_ID: WeakValueDictionary[str, web.WebSocketResponse] = WeakValueDictionary()
_SUB_WS: dict[Topic, WeakSet[web.WebSocketResponse]] = {topic: WeakSet() for topic in Topic}

received_message_counter: int = 0


@route("", method="GET")
async def websocket(request: web.Request, _conn: Connection, user: User):
    player_id = request.query.get("id")

    if player_id is None:
        raise web.HTTPBadRequest(reason="missing id")

    # if we are authenticated using cookies, check for potential CSRF ("CSWH") using Origin header
    if "Cookie" in request.headers:
        expected_origin = util.get_expected_origin(request)
        actual_origin = request.headers["Origin"]
        if expected_origin != actual_origin:
            _LOGGER.warning("blocked websocket connection with Origin: %s", actual_origin)
            _LOGGER.warning("expected origin: %s", expected_origin)
            raise web.HTTPBadRequest()

    ws = web.WebSocketResponse()

    _BY_ID[player_id] = ws
    request.config_dict[CLOSE_RESPONSES].add(ws)

    _LOGGER.info("client connected: %s", player_id)

    await ws.prepare(request)

    async for message in ws:
        if message.type == WSMsgType.TEXT:
            try:
                command = parse(message.data)
                _LOGGER.debug("received message %s", command.__class__.__name__)
            except Exception:
                _LOGGER.warning("failed to parse message %s", message.data)
                continue

            global received_message_counter
            received_message_counter += 1

            if isinstance(command, ClientPlaying):
                await activity.update_player(
                    user,
                    player_id,
                    40,
                    ClientState(
                        track=command.track,
                        paused=command.paused,
                        position=command.position,
                        duration=command.duration,
                        control=command.control,
                        volume=command.volume,
                        player_name=command.client,
                        queue=command.queue,
                        playlists=command.playlists,
                    ),
                )
            elif isinstance(command, ClientState):
                await activity.update_player(user, player_id, 40, command)
            elif isinstance(command, ClientSubscribe):
                _SUB_WS[command.topic].add(ws)

                if command.topic == Topic.PLAYING:
                    # send current data to the client immediately
                    for playing in activity.get_players():
                        legacy_command = playing.legacy_server_command()
                        if legacy_command is not None:
                            await send(ws, legacy_command)
                elif command.topic == Topic.PLAYERS:
                    # send current data to the client immediately
                    for player in activity.get_players():
                        await send(ws, player.server_command())
            elif isinstance(command, ClientPing):
                target = _BY_ID.get(command.player_id)
                if target is not None:
                    await send(target, ServerPing(player_id=player_id))
            elif isinstance(command, ClientPong):
                target = _BY_ID.get(command.player_id)
                if target is not None:
                    await send(target, ServerPong(player_id=player_id))
            elif isinstance(command, ClientRelayCommand):
                target = _BY_ID.get(command.player_id)
                if target is not None:
                    await send(target, command.server_command())
                else:
                    _LOGGER.warning("unknown player id")
            else:
                _LOGGER.warning("ignoring unsupported command: %s", command)

    _LOGGER.info("client disconnected: %s", player_id)

    return ws


async def broadcast_playing(event: events.PlayerStateUpdateEvent) -> None:
    await send(_SUB_WS[Topic.PLAYERS], event.player.server_command())

    legacy_command = event.player.legacy_server_command()
    if legacy_command is None:
        await send(_SUB_WS[Topic.PLAYING], ServerPlayingStopped(player_id=event.player.player_id))
    else:
        await send(_SUB_WS[Topic.PLAYING], legacy_command)


async def broadcast_closed(event: events.PlayerClosedEvent):
    await send(_SUB_WS[Topic.PLAYING], ServerPlayingStopped(player_id=event.player.player_id))
    await send(_SUB_WS[Topic.PLAYERS], ServerPlayerClosed(player_id=event.player.player_id))


async def broadcast_history(event: events.TrackPlayedEvent):
    await send(
        [*_SUB_WS[Topic.PLAYING], *_SUB_WS[Topic.PLAYED]],
        ServerPlayed(
            username=event.user.nickname if event.user.nickname else event.user.username,
            played_time=event.timestamp,
            track=event.track.to_dict(),
        ),
    )


async def broadcast_file_change(event: events.FileChangeEvent):
    username = None
    if event.user:
        username = event.user.nickname if event.user.nickname else event.user.username
    await send(
        _SUB_WS[Topic.FILES],
        ServerFileChange(change_time=int(time.time()), action=event.action.value, track=event.track, username=username),
    )


# to be used from Kivy
def get_websocket(player_id: str) -> WebSocketResponse | None:
    return _BY_ID.get(player_id)


eventbus.subscribe(events.PlayerStateUpdateEvent, broadcast_playing)
eventbus.subscribe(events.PlayerClosedEvent, broadcast_closed)
eventbus.subscribe(events.TrackPlayedEvent, broadcast_history)
eventbus.subscribe(events.FileChangeEvent, broadcast_file_change)
