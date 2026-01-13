# pylint: disable=invalid-name
from __future__ import annotations

from pathlib import Path

from raphson_mp.common.image import ImageFormat

# User configurable settings
log_level: str = "INFO"
log_short: bool = False
access_log: bool = False
# must always be a resolved path!
music_dir: Path | None = None
data_dir: Path = None  # pyright: ignore[reportAssignmentType]
blob_dir: Path | None = None
ffmpeg_log_level: str = "warning"
track_max_duration_seconds: int = 3600
radio_playlists: list[str] = []
lastfm_api_key: str | None = None
lastfm_api_secret: str | None = None
spotify_api_id: str | None = None
spotify_api_secret: str | None = None
offline_mode: bool = False
news_server: str | None = None
bwrap: bool = True
default_image_format = ImageFormat.WEBP
login_message: str | None = None

# Settings that are only available when the server is started
proxy_count: int = 0
