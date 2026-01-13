from __future__ import annotations

import logging
import time
from collections.abc import Iterable
from dataclasses import dataclass
from sqlite3 import Connection
from typing import cast

from raphson_mp.client.track import Track
from raphson_mp.common import eventbus
from raphson_mp.common.control import ClientState, ServerPlayerState, ServerPlaying
from raphson_mp.common.track import NoSuchTrackError, TrackBase
from raphson_mp.server import auth, events, settings

_LOGGER = logging.getLogger(__name__)


@dataclass
class Player:
    player_id: str
    user_id: int
    username: str
    nickname: str
    lastfm_update_time: float
    expiry: int
    state_update_time: float
    state: ClientState

    @property
    def extrapolated_position(self):
        position = self.state.position
        if not self.state.paused and position is not None and self.state.duration is not None:
            return min(self.state.duration, position + time.time() - self.state_update_time)
        return position

    def legacy_server_command(self) -> ServerPlaying | None:
        if self.state.track is None:
            return None
        return ServerPlaying(
            player_id=self.player_id,
            user_id=self.user_id,
            username=self.username,
            nickname=self.nickname,
            paused=self.state.paused,
            position=self.extrapolated_position,
            duration=self.state.duration,
            control=self.state.control,
            volume=self.state.volume,
            expiry=self.expiry,
            client=self.state.player_name if self.state.player_name else "",
            track=self.state.track,
            queue=self.state.queue,
            playlists=self.state.playlists,
        )

    def server_command(self) -> ServerPlayerState:
        return ServerPlayerState(
            player_id=self.player_id,
            user_id=self.user_id,
            username=self.username,
            nickname=self.nickname,
            paused=self.state.paused,
            position=self.extrapolated_position,
            duration=self.state.duration,
            control=self.state.control,
            volume=self.state.volume,
            expiry=self.expiry,
            player_name=self.state.player_name,
            track=self.state.track,
            queue=self.state.queue,
            playlists=self.state.playlists,
        )


_PLAYERS: dict[str, Player] = {}


def get_players() -> Iterable[Player]:
    """Return list of active clients (not necessarily playing)"""
    return _PLAYERS.values()


async def update_player(
    user: auth.User,
    player_id: str,
    expiry: int,
    state: ClientState,
) -> None:
    """Set current player state"""
    current_time = time.time()

    player = _PLAYERS.get(player_id)
    if player is None:
        _PLAYERS[player_id] = player = Player(
            player_id=player_id,
            user_id=user.user_id,
            username=user.username,
            nickname=user.nickname if user.nickname else user.username,
            lastfm_update_time=current_time,
            expiry=expiry,
            state_update_time=current_time,
            state=state,
        )
    else:
        player.nickname = user.nickname if user.nickname else user.username
        player.state_update_time = current_time
        player.state = state

    if not settings.offline_mode and state.track and not state.paused and player.lastfm_update_time < current_time - 60:
        from raphson_mp.server import lastfm

        user_key = lastfm.get_user_key(cast(auth.StandardUser, user))
        if user_key:
            track = Track.from_dict(state.track)
            try:
                await lastfm.update_now_playing(user_key, track)
                player.lastfm_update_time = current_time
            except NoSuchTrackError:
                pass

    await eventbus.fire(events.PlayerStateUpdateEvent(player))


async def set_played(conn: Connection, user: auth.User, track: TrackBase, timestamp: int):
    """Mark a track as played: save to history table and scrobble to last.fm"""
    private = user.privacy == auth.PrivacyOption.AGGREGATE

    if not private:
        await eventbus.fire(events.TrackPlayedEvent(user, timestamp, track))

    conn.execute(
        """
        INSERT INTO history (timestamp, user, track, playlist, private)
        VALUES (?, ?, ?, ?, ?)
        """,
        (timestamp, user.user_id, track.path, track.playlist, private),
    )

    # last.fm requires track length to be at least 30 seconds
    if not settings.offline_mode and not private and track.duration >= 30:
        from raphson_mp.server import lastfm

        lastfm_key = lastfm.get_user_key(cast(auth.StandardUser, user))
        if lastfm_key:
            await lastfm.scrobble(lastfm_key, track, timestamp)


async def _stop_playing(player: Player):
    _LOGGER.debug("player %s stopped playing", player.player_id)
    del _PLAYERS[player.player_id]
    await eventbus.fire(events.PlayerClosedEvent(player))


async def stop_playing(user: auth.User, player_id: str):
    """Call when player exists. Removes player from local state and sends StoppedPlayingEvent"""
    player = _PLAYERS.get(player_id)
    if player is None:
        _LOGGER.warning("stop_playing() called for unregistered player %s", player_id)
        return

    if player.user_id != user.user_id:
        _LOGGER.warning("user %s attempted to stop player owned by different user %s", user.username, player.user_id)
        return

    await _stop_playing(player)


async def remove_expired_playing():
    """
    Called periodically to remove players from which we haven't got an update in a while, and
    for some reason no call to stop_playing() call was received either.
    """
    current_time = time.time()
    to_remove: list[Player] = []
    for player in get_players():
        if player.state_update_time + player.expiry < current_time:
            _LOGGER.info("player expired: %s", player.player_id)
            to_remove.append(player)

    for playing in to_remove:
        await _stop_playing(playing)
