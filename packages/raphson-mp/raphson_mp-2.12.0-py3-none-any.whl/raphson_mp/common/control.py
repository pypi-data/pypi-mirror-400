from __future__ import annotations

import asyncio
import dataclasses
import json
import logging
from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum
from typing import Any

from aiohttp import ClientWebSocketResponse, web
from typing_extensions import override

from raphson_mp.common.typing import QueuedTrackDict, TrackDict

_LOGGER = logging.getLogger(__name__)


class Topic(Enum):
    PLAYING = "playing"  # Deprecated: receive s_playing, s_playing_stopped, s_played
    PLAYERS = "players"  # player info: s_player_state, s_player_closed
    PLAYED = "played"  # played tracks: s_played
    FILES = "files"  # changed files: s_file_change


@dataclass(kw_only=True)
class Command(ABC):
    name: str

    def data(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    @classmethod
    def from_data(cls, data: dict[str, Any]) -> Command:
        assert data["name"] == cls.name
        return cls(**data)

    async def send(self, ws: web.WebSocketResponse | ClientWebSocketResponse) -> None:
        try:
            await ws.send_json(self.data())
        except ConnectionError:
            pass


@dataclass(kw_only=True)
class ServerCommand(Command, ABC):
    """Represents a command from the server"""


@dataclass(kw_only=True)
class ClientCommand(Command, ABC):
    """Represents a command from the client"""


@dataclass(kw_only=True)
class ClientRelayCommand(ClientCommand, ABC):
    """A ClientCommand relayed by the server, as a ServerCommand, to a different client"""

    player_id: str

    @abstractmethod
    def server_command(self) -> ServerCommand:
        pass


# Deprecated
@dataclass(kw_only=True)
class ClientPlaying(ClientCommand):
    """Sent from player client to server, to let the server know about its current state"""

    name: str = "c_playing"
    track: TrackDict
    paused: bool
    position: float | None = None
    duration: float | None = None
    control: bool = False
    volume: float | None = None
    client: str
    queue: list[QueuedTrackDict] | None = None
    playlists: list[str] | None = None


@dataclass(kw_only=True)
class ClientState(ClientCommand):
    """Sent from player client to server, to let the server know about its current state"""

    name: str = "c_state"
    track: TrackDict | None = None
    paused: bool = False
    position: float | None = None
    duration: float | None = None
    control: bool = False
    volume: float | None = None
    player_name: str | None = None
    queue: list[QueuedTrackDict] | None = None
    playlists: list[str] | None = None


@dataclass(kw_only=True)
class ClientRequestUpdate(ClientRelayCommand):
    """Ask another player to send updated state (ClientPlaying)"""

    name: str = "c_request_update"

    @override
    def server_command(self):
        return ServerRequestUpdate()


@dataclass(kw_only=True)
class ClientSubscribe(ClientCommand):
    """Command to subscribe to topics (events) from a client"""

    name: str = "c_subscribe"
    topic: Topic

    @override
    def data(self) -> dict[str, Any]:
        return {"name": self.name, "topic": self.topic.value}

    @override
    @classmethod
    def from_data(cls, data: dict[str, str]) -> Command:
        return cls(topic=Topic(data["topic"]))


@dataclass(kw_only=True)
class ClientPlay(ClientRelayCommand):
    """Instruct a player to start playing"""

    name: str = "c_play"

    @override
    def server_command(self):
        return ServerPlay()


@dataclass(kw_only=True)
class ClientPause(ClientRelayCommand):
    """Instruct a player to pause"""

    name: str = "c_pause"

    @override
    def server_command(self):
        return ServerPause()


@dataclass(kw_only=True)
class ClientPrevious(ClientRelayCommand):
    """Instruct a player to go to the previous track"""

    name: str = "c_previous"

    @override
    def server_command(self):
        return ServerPrevious()


@dataclass(kw_only=True)
class ClientNext(ClientRelayCommand):
    """Instruct a player to go to the next track"""

    name: str = "c_next"

    @override
    def server_command(self):
        return ServerNext()


@dataclass(kw_only=True)
class ClientVolume(ClientRelayCommand):
    """Instruct a player to change its volume"""

    name: str = "c_volume"
    volume: float

    @override
    def server_command(self):
        return ServerVolume(volume=self.volume)


@dataclass(kw_only=True)
class ClientSeek(ClientRelayCommand):
    """Instruct a player to seek"""

    name: str = "c_seek"
    position: float

    @override
    def server_command(self):
        return ServerSeek(position=self.position)


@dataclass(kw_only=True)
class ClientSetQueue(ClientRelayCommand):
    name: str = "c_set_queue"
    tracks: list[QueuedTrackDict]

    @override
    def server_command(self):
        return ServerSetQueue(tracks=self.tracks)


@dataclass(kw_only=True)
class ClientSetPlaying(ClientRelayCommand):
    name: str = "c_set_playing"
    track: TrackDict

    @override
    def server_command(self):
        return ServerSetPlaying(track=self.track)


@dataclass(kw_only=True)
class ClientSetPlaylists(ClientRelayCommand):
    name: str = "c_set_playlists"
    playlists: list[str]

    @override
    def server_command(self):
        return ServerSetPlaylists(playlists=self.playlists)


@dataclass(kw_only=True)
class ClientPing(ClientCommand):
    name: str = "c_ping"
    player_id: str  # target player


@dataclass(kw_only=True)
class ClientPong(ClientCommand):
    name: str = "c_pong"
    player_id: str  # target player


@dataclass(kw_only=True)
class ServerPlaying(ServerCommand):
    """
    ClientPlaying command relayed by the server as ServerPlaying command to clients subscribed to Topic.ACTIVITY
    """

    name: str = "s_playing"
    player_id: str
    user_id: int
    username: str  # username
    nickname: str  # nickname or username
    paused: bool  # whether media is paused
    position: float | None  # position in playing track
    duration: float | None  # duration of track
    control: bool  # whether control is supported
    volume: float | None  # current volume 0.0-1.0
    expiry: int  # number of seconds after update before the entry should be ignored
    client: str
    track: TrackDict
    queue: list[QueuedTrackDict] | None = None
    playlists: list[str] | None = None


@dataclass(kw_only=True)
class ServerPlayerState(ServerCommand):
    name: str = "s_player_state"
    player_id: str
    user_id: int
    username: str  # username
    nickname: str  # nickname or username
    paused: bool  # whether media is paused
    position: float | None  # position in playing track
    duration: float | None  # duration of track
    control: bool  # whether control is supported
    volume: float | None  # current volume 0.0-1.0
    expiry: int  # number of seconds after update before the entry should be ignored
    player_name: str | None
    track: TrackDict | None
    queue: list[QueuedTrackDict] | None = None
    playlists: list[str] | None = None


@dataclass(kw_only=True)
class ServerRequestUpdate(ServerCommand):
    name: str = "s_request_update"


@dataclass(kw_only=True)
class ServerPlayed(ServerCommand):
    name: str = "s_played"
    played_time: int  # timestamp at which track was played
    username: str  # nickname or username
    track: TrackDict


# Deprecated
@dataclass(kw_only=True)
class ServerPlayingStopped(ServerCommand):
    """Fired when a player has stopped playing"""

    name: str = "s_playing_stopped"
    player_id: str


@dataclass(kw_only=True)
class ServerPlayerClosed(ServerCommand):
    """Fired when a player has stopped existing"""

    name: str = "s_player_closed"
    player_id: str


class FileAction(Enum):
    INSERT = "insert"
    DELETE = "delete"
    UPDATE = "update"
    MOVE = "move"


@dataclass(kw_only=True)
class ServerFileChange(ServerCommand):
    name: str = "s_file_change"
    change_time: int
    action: str
    track: str
    username: str | None


@dataclass(kw_only=True)
class ServerPlay(ServerCommand):
    name: str = "s_play"


@dataclass(kw_only=True)
class ServerPause(ServerCommand):
    name: str = "s_pause"


@dataclass(kw_only=True)
class ServerPrevious(ServerCommand):
    name: str = "s_previous"


@dataclass(kw_only=True)
class ServerNext(ServerCommand):
    name: str = "s_next"


@dataclass(kw_only=True)
class ServerVolume(ServerCommand):
    name: str = "s_volume"
    volume: float


@dataclass(kw_only=True)
class ServerSeek(ServerCommand):
    name: str = "s_seek"
    position: float


@dataclass(kw_only=True)
class ServerSetQueue(ServerCommand):
    name: str = "s_set_queue"
    tracks: list[QueuedTrackDict]


@dataclass(kw_only=True)
class ServerSetPlaying(ServerCommand):
    name: str = "s_set_playing"
    track: TrackDict


@dataclass(kw_only=True)
class ServerSetPlaylists(ServerCommand):
    name: str = "s_set_playlists"
    playlists: list[str]


@dataclass(kw_only=True)
class ServerPing(ClientCommand):
    name: str = "s_ping"
    player_id: str  # source player


@dataclass(kw_only=True)
class ServerPong(ClientCommand):
    name: str = "s_pong"
    player_id: str  # source player


COMMANDS: list[type[Command]] = [
    ClientState,
    ClientPlaying,
    ClientRequestUpdate,
    ClientSubscribe,
    ClientPlay,
    ClientPause,
    ClientPrevious,
    ClientNext,
    ClientVolume,
    ClientSeek,
    ClientSetQueue,
    ClientSetPlaying,
    ClientSetPlaylists,
    ClientPing,
    ClientPong,
    ServerPlayerState,
    ServerPlaying,
    ServerRequestUpdate,
    ServerPlayed,
    ServerPlayingStopped,
    ServerPlayerClosed,
    ServerFileChange,
    ServerPlay,
    ServerPause,
    ServerPrevious,
    ServerNext,
    ServerVolume,
    ServerSeek,
    ServerSetQueue,
    ServerSetPlaying,
    ServerSetPlaylists,
    ServerPing,
    ServerPong,
]

_BY_NAME: dict[str, type[Command]] = {}

for command in COMMANDS:
    _BY_NAME[command.name] = command


def parse(message: str) -> Command:
    json_message = json.loads(message)
    command_t = _BY_NAME.get(json_message["name"])
    if command_t is None:
        raise ValueError("unknown command: " + json_message["name"])
    command = command_t.from_data(json_message)
    return command


async def send(
    sockets: (
        ClientWebSocketResponse
        | web.WebSocketResponse
        | Iterable[web.WebSocketResponse]
        | Iterable[ClientWebSocketResponse]
    ),
    command: Command,
):
    if sockets:
        _LOGGER.debug("sending message %s", command.__class__.__name__)

    if isinstance(sockets, ClientWebSocketResponse) or isinstance(sockets, web.WebSocketResponse):
        await command.send(sockets)
    else:
        await asyncio.gather(*[command.send(socket) for socket in sockets])
