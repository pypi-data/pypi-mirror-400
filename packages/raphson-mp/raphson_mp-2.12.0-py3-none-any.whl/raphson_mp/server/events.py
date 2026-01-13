from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from raphson_mp.common.control import FileAction
from raphson_mp.common.eventbus import Event
from raphson_mp.common.track import TrackBase

if TYPE_CHECKING:
    from raphson_mp.server.activity import Player
    from raphson_mp.server.auth import User


@dataclass
class PlayerStateUpdateEvent(Event):
    player: Player


@dataclass
class PlayerClosedEvent(Event):
    player: Player


@dataclass
class TrackPlayedEvent(Event):
    user: User
    timestamp: int
    track: TrackBase


@dataclass
class FileChangeEvent(Event):
    action: FileAction
    track: str
    user: User | None
