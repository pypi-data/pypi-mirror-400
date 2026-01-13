// Common JavaScript interface to API, to be used by the music player and other pages.

import { vars, uuidv4, checkResponseCode, jsonPost, jsonGet } from "./util.js";

export const VIRTUAL_PLAYLIST = '~';
export const NEWS_PATH = `${VIRTUAL_PLAYLIST}/news`;

export const RAPHSON_URL = '/static/img/raphson.png';
export const RAPHSON_SMALL_URL = '/static/img/raphson_small.webp';

export const AudioFormat = {
    OPUS_HIGH: 'webm_opus_high',
    OPUS_LOW: 'webm_opus_low',
    MP3: 'mp3_with_metadata',
};

export const ControlCommand = {
    CLIENT_REQUEST_UPDATE: "c_request_update",
    CLIENT_STATE: "c_state",
    CLIENT_SUBSCRIBE: "c_subscribe",
    CLIENT_PLAY: "c_play",
    CLIENT_PAUSE: "c_pause",
    CLIENT_PREVIOUS: "c_previous",
    CLIENT_NEXT: "c_next",
    CLIENT_VOLUME: "c_volume",
    CLIENT_SEEK: "c_seek",
    CLIENT_SET_QUEUE: "c_set_queue",
    CLIENT_SET_PLAYING: "c_set_playing",
    CLIENT_SET_PLAYLISTS: "c_set_playlists",
    CLIENT_PING: "c_ping",
    CLIENT_PONG: "c_pong",
    SERVER_REQUEST_UPDATE: "s_request_update",
    SERVER_PLAYER_STATE: "s_player_state",
    SERVER_PLAYED: "s_played",
    SERVER_PLAYER_CLOSED: "s_player_closed",
    SERVER_FILE_CHANGE: "s_file_change",
    SERVER_PLAY: "s_play",
    SERVER_PAUSE: "s_pause",
    SERVER_PREVIOUS: "s_previous",
    SERVER_NEXT: "s_next",
    SERVER_VOLUME: "s_volume",
    SERVER_SEEK: "s_seek",
    SERVER_SET_QUEUE: "s_set_queue",
    SERVER_SET_PLAYING: "s_set_playing",
    SERVER_SET_PLAYLISTS: "s_set_playlists",
    SERVER_PING: "s_ping",
    SERVER_PONG: "s_pong",
};

export const ControlTopic = {
    PLAYERS: "players",
    PLAYED: "played",
    FILES: "files",
};

class ControlChannel {
    /** @type {string} */
    player_id;
    /** @type {Set<string>} */
    #subscriptions;
    /** @type {Object<string, Array<(data: any) => void>>} */
    #handlers;
    /** @type {Array<Function>} */
    #onConnect;
    /** @type {WebSocket | null} */
    #socket;
    constructor() {
        this.player_id = uuidv4();
        this.#subscriptions = new Set();
        this.#handlers = {};
        this.#onConnect = [];
        this.#socket = null;

        for (const command of Object.values(ControlCommand)) {
            this.#handlers[command] = [];
        }

        setInterval(() => {
            if (this.#socket == null ||
                !(this.#socket.readyState in [WebSocket.CONNECTING, WebSocket.OPEN])
            ) {
                this.#open();
            }
        }, 10000);

        this.#open();

        // Reissue subscriptions when socket is opened
        this.registerConnectHandler(() => {
            for (const topic of this.#subscriptions) {
                this.sendMessage(ControlCommand.CLIENT_SUBSCRIBE, { "topic": topic });
            }
        });
    }

    #open() {
        // Modern browsers (since early 2024) have support for connecting to a partial URL (just "/control?id=...").
        // However, we need to support earlier versions, especially because of mobile Safari and Firefox ESR in Linux distributions.
        // So, construct a URL manually:
        var url = new URL('/control?id=' + encodeURIComponent(this.player_id), window.location.href);
        url.protocol = url.protocol.replace('http', 'ws'); // http -> ws, https -> wss
        console.info('ws: connect:', url.href);
        this.#socket = new WebSocket(url.href);

        this.#socket.addEventListener("message", event => this.#handleMessage(event.data));

        this.#socket.addEventListener("open", () => {
            this.#onConnect.forEach(f => f());
        });
    }

    /**
     * @param {string} message
     */
    #handleMessage(message) {
        const parsedMessage = JSON.parse(message);
        console.debug('api: ws: received:', message);
        if (parsedMessage.name in this.#handlers) {
            this.#handlers[parsedMessage.name].forEach(handler => handler(parsedMessage));
        } else {
            console.warn("ws: received command is unknown");
        }
    }

    /**
     * @param {string} name
     * @param {import("./types.js").ControlClientCommand} data
     */
    sendMessage(name, data) {
        if (this.#socket == null || this.#socket.readyState != WebSocket.OPEN) {
            console.warn('api: ws: disconnected, cannot send:', name);
            return;
        }
        console.debug('api: ws: send:', name, data);
        this.#socket.send(JSON.stringify({ name: name, ...data }));
    }

    /**
     * @param {string} command
     * @param {(data: any) => void} handler
     */
    registerMessageHandler(command, handler) {
        if (command.startsWith("c_")) throw new Error("it does not make sense to listen for a client event, they are only sent to the server");
        this.#handlers[command].push(handler);
    }

    /**
     * @param {string} command
     * @param {(data: any) => void} handler
     */
    unregisterMessageHandler(command, handler) {
        const i = this.#handlers[command].indexOf(handler);
        if (i == -1) throw new Error("handler not registered");
        this.#handlers[command].splice(i, 1);
    }

    /**
     * @param {() => void} handler
     */
    registerConnectHandler(handler) {
        this.#onConnect.push(handler);
    }

    /**
     * @param {string} topic
     * @returns {boolean} true if subscribed, false if already subscribed
     */
    subscribe(topic) {
        if (this.#subscriptions.has(topic)) return false;
        this.#subscriptions.add(topic);
        this.sendMessage(ControlCommand.CLIENT_SUBSCRIBE, { topic: topic });
        return true;
    }

    /**
     * @param {string} player_id
     */
    async play(player_id) {
        this.sendMessage(ControlCommand.CLIENT_PLAY, { player_id: player_id });
    }

    /**
     * @param {string} player_id
     */
    async pause(player_id) {
        this.sendMessage(ControlCommand.CLIENT_PAUSE, { player_id: player_id });
    }

    /**
     * @param {string} player_id
     */
    async previous(player_id) {
        this.sendMessage(ControlCommand.CLIENT_PREVIOUS, { player_id: player_id });
    }

    /**
     * @param {string} player_id
     */
    async next(player_id) {
        this.sendMessage(ControlCommand.CLIENT_NEXT, { player_id: player_id });
    }

    sendStopSignal() {
        const data = new FormData();
        data.set("csrf", vars.csrfToken);
        data.set("id", this.player_id);
        navigator.sendBeacon("/activity/stop", data);
    }
}

export const controlChannel = new ControlChannel();

export class Album {
    /** @type {string} */
    name;
    /** @type {string|null} */
    artist;
    /** @type {string} */
    track; // arbitrary track from album to get cover image

    /**
     * @param {import("./types.js").AlbumJson} albumObj
     */
    constructor(albumObj) {
        this.name = albumObj.name;
        this.artist = albumObj.artist;
        this.track = albumObj.track;
    }

    /**
     * @param {string} imageQuality 'low' or 'high'
     * @param {boolean} memeCover
     * @returns {string}
     */
    getCoverURL(imageQuality, memeCover = false) {
        return `/track/${encodeURIComponent(this.track)}/cover?quality=${imageQuality}&meme=${memeCover ? 1 : 0}`;
    }
}

export class Artist {
    /** @type {string} */
    name;

    /**
     * @param {import("./types.js").ArtistJson} artistObj
     */
    constructor(artistObj) {
        this.name = artistObj.name;
    }

    /**
     * @param {string} imageQuality 'low' or 'high'
     * @returns {string}
     */
    getImageURL(imageQuality) {
        return `/artist/${encodeURIComponent(this.name)}/image?quality=${encodeURIComponent(imageQuality)}`;
    }

    async getExtract() {
        const response = await fetch(`/artist/${encodeURIComponent(this.name)}/extract`);
        checkResponseCode(response);
        return await response.text();
    }
}

class SearchResult {
    /** @type {Array<Track>} */
    tracks;
    /** @type {Array<Artist>} */
    artists;
    /** @type {Array<Album>} */
    albums;

    /**
     * @param {Array<Track>} tracks
     * @param {Array<Artist>} artists
     * @param {Array<Album>} albums
     */
    constructor(tracks, artists, albums) {
        this.tracks = tracks;
        this.artists = artists;
        this.albums = albums;
    }
}

class Music {
    #playlists =  /** @type {Object.<String, Playlist> | null} */ (null);
    #onLoaded = /** @type {Array<() => void>} */ ([]);

    constructor() { }

    async loadPlaylists() {
        const response = await fetch('/playlist/list');
        checkResponseCode(response);
        const json = /** @type {Array<import("./types.js").PlaylistJson>} */ (await response.json());
        const playlists = /** @type {Object.<String, Playlist>} */ ({});
        for (const playlistObj of json) {
            playlists[playlistObj.name] = new Playlist(playlistObj);
        }
        this.#playlists = playlists;
        for (const func of this.#onLoaded) {
            func();
        }
        this.#onLoaded.length = 0;
    }

    /**
     * Register a callback function to be called when playlists are initially loaded. If playlists are already
     * loaded, when this function is called, the callback function is called immediately.
     * @param {() => void} callback
     */
    waitForPlaylistsLoaded(callback) {
        if (this.#playlists != null) {
            callback();
        } else {
            this.#onLoaded.push(callback);
        }
    }

    /**
     * @returns {Array<Playlist>}
     */
    playlists() {
        if (this.#playlists == null) {
            throw new Error("loadPlaylists() must be called first");
        }
        return Object.values(this.#playlists);

    }

    /**
     * @param {string} name
     * @returns {Playlist}
     */
    playlist(name) {
        if (this.#playlists == null) {
            throw new Error("loadPlaylists() must be called first");
        }

        return this.#playlists[name];
    }

    /**
     * @param {Array<import("./types.js").TrackJson>} json
     * @returns {Array<Track>}
     */
    #tracksFromJson(json) {
        const tracks = [];
        for (const trackObj of json) {
            tracks.push(new Track(trackObj));
        }
        return tracks;
    }

    /**
     *
     * @param {Array<import("./types.js").ArtistJson>} json
     * @returns {Array<Artist>}
     */
    #artistsFromJson(json) {
        const artists = [];
        for (const artistObj of json) {
            artists.push(new Artist(artistObj));
        }
        return artists;
    }

    /**
     * @param {Array<import("./types.js").AlbumJson>} json
     * @returns {Array<Album>}
     */
    #albumsFromJson(json) {
        const albums = [];
        for (const album of json) {
            albums.push(new Album(album));
        }
        return albums;
    }

    /**
     * @param {import("./types.js").FilterJson} filters
     * @returns {Promise<Array<Track>>}
     */
    async filter(filters) {
        const encodedFilters = [];
        for (const [key, value] of Object.entries(filters)) {
            encodedFilters.push(key + '=' + encodeURIComponent(value));
        }
        const response = await fetch('/tracks/filter?' + encodedFilters.join('&'));
        checkResponseCode(response);
        const json = await response.json();
        return this.#tracksFromJson(json.tracks);
    }

    /**
     * @param {string} query FTS5 search query
     * @param {AbortSignal | undefined} abortSignal
     * @returns {Promise<SearchResult>}
     */
    async search(query, abortSignal) {
        const response = await fetch('/tracks/search?query=' + encodeURIComponent(query), { signal: abortSignal });
        checkResponseCode(response);
        const json = await response.json();
        const tracks = this.#tracksFromJson(json.tracks);
        const artists = this.#artistsFromJson(json.artists);
        const albums = this.#albumsFromJson(json.albums);
        return new SearchResult(tracks, artists, albums);
    }

    /**
     * @param {string} path
     * @returns {Promise<Track>}
     */
    async track(path) {
        const response = await fetch(`/track/${encodeURIComponent(path)}/info`);
        checkResponseCode(response);
        return new Track(await response.json());
    }

    /**
     * @returns {Promise<Array<string>>}
     */
    async tags() {
        const response = await fetch('/tracks/tags');
        checkResponseCode(response);
        return await response.json();
    }

    /**
     * @param {Track} track
     */
    async played(track) {
        const data = {
            track: track.path,
        };
        await jsonPost('/activity/played', data);
    }
}

export const music = new Music();

export class Playlist {
    name;
    trackCount;
    favorite;
    write;
    synced;

    /**
     * @param {import("./types.js").PlaylistJson} playlistData
     */
    constructor(playlistData) {
        this.name = playlistData.name;
        this.trackCount = playlistData.track_count;
        this.favorite = playlistData.favorite;
        this.write = playlistData.write;
        this.synced = playlistData.synced ? playlistData.synced : false;
    }

    /**
     * @param {boolean} requireMetadata
     * @param {object} tagFilter Empty object for no tag filter
     * @param {string[] | null} intersectPlaylists
     * @returns {Promise<Track | null>}
     */
    async chooseRandomTrack(requireMetadata, tagFilter, intersectPlaylists = null) {
        const chooseData = { require_metadata: requireMetadata, ...tagFilter };
        if (intersectPlaylists != null) {
            // @ts-ignore
            chooseData.intersect_playlists = intersectPlaylists;
        }
        console.debug('api: choose track: ', this.name, requireMetadata, tagFilter, intersectPlaylists);
        const chooseResponse = await jsonPost('/playlist/' + encodeURIComponent(this.name) + '/choose_track', chooseData);
        if (chooseResponse.status == 204) {
            console.info('api: no suitable track found in playlist:', this.name);
            return null;
        }
        const trackData = await chooseResponse.json();
        return new Track(trackData);
    }
}

export class Track {
    /** @type {string} */
    path;
    /** @type {number} */
    mtime;
    /** @type {number} */
    ctime;
    /** @type {number} */
    duration;
    /** @type {Array<string>} */
    tags;
    /** @type {string | null} */
    title;
    /** @type {Array<string>} */
    artists;
    /** @type {string | null} */
    album;
    /** @type {string | null} */
    albumArtist;
    /** @type {number | null} */
    year;
    /** @type {number | null} */
    trackNumber;
    /** @type {string | null} */
    video;
    /** @type {string | null} */
    lyrics;

    /**
     * @param {import("./types.js").TrackJson} trackData
     */
    constructor(trackData) {
        this.path = trackData.path;
        this.mtime = trackData.mtime;
        this.ctime = trackData.ctime;
        this.duration = trackData.duration;
        this.title = trackData.title || null;
        this.album = trackData.album || null;
        this.albumArtist = trackData.album_artist || null;
        this.year = trackData.year || null;
        this.trackNumber = trackData.track_number || null;
        this.video = trackData.video || null;
        this.lyrics = trackData.lyrics || null;
        this.artists = trackData.artists || [];
        this.tags = trackData.tags || [];
    };

    get playlistName() {
        return this.path.substring(0, this.path.indexOf('/'));
    }

    get playlist() {
        return music.playlist(this.playlistName);
    }

    get parsedLyrics() {
        return parseLyrics(this.lyrics);
    }

    get plainLyrics() {
        const lyrics = this.parsedLyrics;
        if (lyrics instanceof PlainLyrics) {
            return lyrics.text;
        } else if (lyrics instanceof TimeSyncedLyrics) {
            return lyrics.asPlainText();
        } else {
            return null;
        }
    }

    /**
     * @returns {import("./types.js").TrackJson}
     */
    toJson() {
        return {
            'path': this.path,
            'mtime': this.mtime,
            'ctime': this.ctime,
            'duration': this.duration,
            'title': this.title,
            'album': this.album,
            'album_artist': this.albumArtist,
            'year': this.year,
            'track_number': this.trackNumber,
            'video': this.video,
            'lyrics': this.lyrics,
            'artists': this.artists,
            'tags': this.tags,
        };
    }

    isVirtual() {
        return this.playlistName == "~";
    }

    /**
     * @returns {Album | null}
     */
    getAlbum() {
        return this.album ? new Album({ name: this.album, artist: this.albumArtist, track: this.path }) : null;
    }

    /**
     * Generates display text for this track
     * @param {boolean} showPlaylist
     * @returns {string}
     */
    displayText(showPlaylist = true, showAlbum = true) {
        // Should be similar to on TrackBase.display_title on server for consistency

        let text = '';

        if (showPlaylist && !this.isVirtual()) {
            text += `${this.playlistName}: `;
        }

        if (this.title != null) {
            if (this.artists.length > 0) {
                text += this.artists.join(', ');
                text += ' - ';
            }
            text += this.title;

            if (this.album && showAlbum) {
                text += ` (${this.album}`;
                if (this.year) {
                    text += `, ${this.year})`;
                } else {
                    text += ')';
                }
            } else if (this.year) {
                text += ` (${this.year})`;
            }
        } else {
            // Not enough metadata available, generate display title based on file name
            let filename = this.path.substring(this.path.lastIndexOf('/') + 1);

            // remove extension
            filename = filename.substring(0, filename.lastIndexOf('.'));

            // Remove YouTube id suffix
            filename = filename.replaceAll(/\[[a-zA-Z0-9\-_]+\]/g, "");

            // Remove whitespace
            filename = filename.trim();

            text += filename;
        }

        return text;
    };

    /**
     * @param {string} audioType
     * @returns string
     */
    getAudioURL(audioType) {
        return `/track/${encodeURIComponent(this.path)}/audio?type=${audioType}&mtime=` + this.mtime;
    }

    /**
     * @param {string} imageQuality
     * @param {boolean} memeCover
     * @returns {string}
     */
    getCoverURL(imageQuality, memeCover = false) {
        return `/track/${encodeURIComponent(this.path)}/cover?quality=${imageQuality}&meme=${memeCover ? 1 : 0}&mtime=${this.mtime}`;
    }

    async delete() {
        const oldName = this.path.split('/').pop();
        const newName = '.trash.' + oldName;
        await jsonPost('/files/rename', { path: this.path, new_name: newName });
    }

    async dislike() {
        await jsonPost('/dislikes/add', { track: this.path });
    }

    /**
     * Updates track metadata by sending current metadata of this object to the server.
     */
    async saveMetadata() {
        const payload = {
            title: this.title,
            album: this.album,
            artists: this.artists,
            album_artist: this.albumArtist,
            tags: this.tags,
            year: this.year,
            track_number: this.trackNumber,
            lyrics: this.lyrics,
        };

        await jsonPost(`/track/${encodeURIComponent(this.path)}/update_metadata`, payload);
    }

    /**
     * Copy track to other playlist
     * @param {string} playlistName
     * @returns {Promise<void>}
     */
    async copyTo(playlistName) {
        await jsonPost('/files/copy', { src: this.path, dest: playlistName });
    }

    async refresh() {
        const json = await jsonGet(`/track/${encodeURIComponent(this.path)}/info`);
        this.constructor(json);
    }

    /**
     * Look up metadata for this track using the AcoustID service
     * @returns {Promise<import("./types.js").AcoustIDResult | null>}
     */
    async acoustid() {
        return await jsonGet(`/track/${encodeURIComponent(this.path)}/acoustid`);
    }

    getVideoURL() {
        return `/track/${encodeURIComponent(this.path)}/video`;
    }

    async reportProblem() {
        await jsonPost(`/track/${encodeURIComponent(this.path)}/report_problem`, {});
    }

    /**
     * Search new lyrics
     * @returns {Promise<boolean>} whether new lyrics was found
     */
    async searchLyrics() {
        const response = await jsonPost(`/track/${encodeURIComponent(this.path)}/search_lyrics`, {});
        const json = await response.json();
        this.lyrics = json.lyrics;
        return json.found;
    }

    isWritable() {
        if (vars.offlineMode || this.isVirtual()) {
            return false;
        }

        const playlist = this.playlist;
        return playlist.write && !playlist.synced;
    }
}

export class Lyrics { };

export class PlainLyrics extends Lyrics {
    /** @type {string} */
    text;

    /**
     * @param {string} text
     */
    constructor(text) {
        super();
        this.text = text;
    };
};

export class LyricsLine {
    /** @type {number} */
    startTime;
    /** @type {string} */
    text;

    /**
     *
     * @param {number} startTime
     * @param {string} text
     */
    constructor(startTime, text) {
        this.startTime = startTime;
        this.text = text;
    }
}

export class TimeSyncedLyrics extends Lyrics {
    /** @type {Array<LyricsLine>} */
    text;

    /**
     * @param {Array<LyricsLine>} text
     */
    constructor(text) {
        super();
        this.text = text;
    };

    /**
     * @returns {string}
     */
    asPlainText() {
        const lines = [];
        for (const line of this.text) {
            lines.push(line.text);
        }
        return lines.join('\n');
    }

    /**
     * @param {number} currentTime
     * @returns {number}
     */
    currentLine(currentTime) {
        currentTime += 0.5; // go to next line slightly earlier, to give the user time to read
        // current line is the last line where currentTime is after the line start time
        for (let i = 0; i < this.text.length; i++) {
            if (currentTime < this.text[i].startTime) {
                return i - 1;
            }
        }
        return this.text.length - 1;
    }
};

/**
 * @param {string | null} lyricsText
 */
export function parseLyrics(lyricsText) {
    if (lyricsText == null) {
        return null;
    }

    const rawLines = lyricsText.split('\n');
    const parsedLines = /** @type {Array<LyricsLine>} */ ([]);
    for (const line of rawLines) {
        const matches = line.match(/^\[(\d{2}):(\d{2})\.(\d{2})\]\s*(.*)/);
        if (matches) {
            const startTime = parseInt(matches[1]) * 60 + parseInt(matches[2]) + parseInt(matches[3]) / 100;
            const text = matches[4];
            parsedLines.push(new LyricsLine(startTime, text));
        }
    }

    if (parsedLines.length * 2 > rawLines.length) {
        return new TimeSyncedLyrics(parsedLines);
    } else {
        return new PlainLyrics(lyricsText);
    }
}
