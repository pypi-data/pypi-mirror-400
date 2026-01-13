// base.jinja2
export type Vars = {
    csrfToken: string,
    offlineMode: string,
    loadTimestamp: number,
};

// common.track.TrackDict
export type TrackJson = {
    path: string
    mtime: number
    ctime: number
    duration: number
    title?: string | null
    album?: string | null
    album_artist?: string | null
    year?: number | null
    track_number?: number | null
    video?: string | null
    lyrics?: string | null
    artists?: Array<string>
    tags?: Array<string>
};

// common.track.QueuedTrackDict
export type QueuedTrackJson = {
    track: TrackJson,
    manual: boolean,
}

// routes.tracks.route_filter
export type FilterJson = {
    limit?: number,
    offset?: number,
    playlist?: string,
    artist?: string,
    tag?: string,
    album_artist?: string,
    album?: string,
    year?: number,
    title?: string,
    has_metadata?: string,
    order?: string,
}

// common.music.Album
export type AlbumJson = {
    name: string,
    artist: string | null,
    track: string, // arbitrary track from the album, can be used to obtain a cover art image
};

// common.music.Artist
export type ArtistJson = {
    name: string,
};

// common.control.ClientState
export type ControlClientState = {
    track: TrackJson | null,
    paused: boolean,
    position?: number | null,
    duration?: number | null,
    control: boolean,
    volume?: number | null,
    player_name: string,
    queue: Array<QueuedTrackJson> | null,
    playlists: Array<string> | null,
}

export type ControlClientQueue = {
    tracks: Array<QueuedTrackJson>
}

export type ControlClientRequestUpdate = {
    player_id: string
}

export type ControlClientSubscribe = {
    topic: string,
}

export type ControlClientToken = {
    csrf: string,
}

export type ControlClientPlay = {
    player_id: string,
}

export type ControlClientPause = {
    player_id: string,
}

export type ControlClientPrevious = {
    player_id: string,
}

export type ControlClientNext = {
    player_id: string,
}

export type ControlClientVolume = {
    player_id: string,
    volume: number
}

export type ControlClientSeek = {
    player_id: string,
    position: number,
}

export type ControlClientSetQueue = {
    player_id: string,
    tracks: Array<QueuedTrackJson>
}

export type ControlClientSetPlaying = {
    player_id: string,
    track: TrackJson,
}

export type ControlClientPlaylists = {
    player_id: string,
    playlists: Array<string>,
}

export type ControlClientSetPlaylists = {
    player_id: string,
    playlists: Array<string>,
}

export type ControlClientPing = {
    player_id: string,
};

export type ControlClientPong = {
    player_id: string,
};

export type ControlClientCommand =
    ControlClientState |
    ControlClientSubscribe |
    ControlClientToken |
    ControlClientPlay |
    ControlClientPause |
    ControlClientPrevious |
    ControlClientNext |
    ControlClientVolume |
    ControlClientSeek |
    ControlClientSetQueue |
    ControlClientSetPlaying |
    ControlClientPlaylists |
    ControlClientSetPlaylists |
    ControlClientPing |
    ControlClientPong;

// common.control.ServerPlaying
export type ControlServerPlayerState = {
    player_id: string,
    user_id: number,
    username: string,
    nickname: string,
    paused: boolean,
    position: number | null,
    duration: number | null,
    control: boolean,
    volume: number | null,
    expiry: number,
    player_name: string | null,
    track: TrackJson | null,
    queue: Array<QueuedTrackJson> | null,
    playlists: Array<string> | null,
};

// common.control.ServerPlayed
export type ControlServerPlayed = {
    played_time: number,
    username: string,
    track: TrackJson,
};

export type ControlServerPlayerClosed = {
    player_id: string,
}

export type FileAction = "insert" | "delete" | "update" | "move";

// common.control.ServerFileChange
export type ControlServerFileChange = {
    change_time: number,
    action: FileAction,
    track: string,
    username: string | null,
};

export type ControlServerSetQueue = {
    tracks: Array<QueuedTrackJson>,
}

export type ControlServerSetPlaying = {
    track: TrackJson,
}

export type ControlServerSetPlaylists = {
    playlists: Array<string>,
}

export type ControlServerPing = {
    player_id: string,
};

export type ControlServerPong = {
    player_id: string,
};

export type WebauthnSetupVars = {
    challenge: string,
    identifier: string,
    username: string,
    displayname: string,
};

// musicbrainz.MBMeta
export type AcoustIDRelease = {
    id: string,
    title: string,
    album: string,
    artists: Array<string>,
    album_artist: string,
    year: number | null,
    release_type: string,
    packaging: string,
}

// routes.track.route_acoustid
export type AcoustIDResult = {
    acoustid: string,
    releases: Array<AcoustIDRelease>,
}

export type ProgressEntry = {
    task?: string,
    state: "start" | "done" | "error" | "stopped" | "running",
};

// common.typing.PlaylistDict
export type PlaylistJson = {
    name: string
    track_count: number
    favorite: boolean
    write: boolean
    synced?: boolean
}

// Frontend only
export type SavedStateJson = {
    position: ?number,
    current: ?TrackJson,
    queue: QueuedTrackJson[],
};
